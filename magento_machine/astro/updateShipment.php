<?php
$magentoRoot = "/var/www/astropaper/web/";
require_once($magentoRoot."app/bootstrap.php");
// DST connection
if (count($argv) > 1 && $argv[1] == 'dev') {
  $dstServerHost = "localhost";
  $dstUsername = "astrodst";
  $dstPassword = "yBuWsClD";
  $dstDatabase = "astropaper_dst";
} else {
  $dstServerHost = "127.0.0.1";//astro.chdqipdgp8gj.us-west-2.rds.amazonaws.com";
  $dstUsername = "silkdba";
  $dstPassword = "fj8Tu6Nh5M";
  $dstDatabase = "astropaper_dst";
}


$notifyShipment = true;
$notifyInvoice = false;

$listEShipmentSQL = "SELECT * FROM e_shipment WHERE sync_status = :sync_status";
$listEShipmentItemSQL = "SELECT * FROM e_shipment_item WHERE e_shipment_id = :e_shipment_id";
$updateEShipmentSQL = "UPDATE e_shipment
                        SET
                        m_shipment_inc_id = :m_shipment_inc_id,
                        m_invoice_inc_id = :m_invoice_inc_id,
                        sync_status = :sync_status,
                        sync_notes = :sync_notes
                        WHERE id = :id";
$updateEShipmentInvoiceIncIdSQL = "UPDATE e_shipment
                        SET
                        m_invoice_inc_id = :m_invoice_inc_id
                        WHERE m_order_inc_id = :m_order_inc_id";
/*
function getOrderItemFromSku($order,$eShipmentItem){
  $item = array();
  foreach ($order->getAllItems() as $orderItem) {
    if ($orderItem->getSku() == $orderItem['sku'] && $orderItem->getProductType == 'simple'){
      $item[$orderItem->getId()] = $eShipmentItem['qty'];
      break;
    }
  }
  return $item;
} */

function getOrderItemFromSku($order,$eShipmentItem){
  $item = array();
  foreach ($order->getAllItems() as $orderItem) {
    var_dump($orderItem->getId());
    var_dump($eShipmentItem['order_item_id']);
    if ($orderItem->getId() == $eShipmentItem['order_item_id']){
      $item[$orderItem->getId()] = $eShipmentItem['qty'];
      break;
    }
  }
  return $item;
}

function updateShipment(){
  global $dstConn, $objectManager,$listEShipmentSQL,$listEShipmentItemSQL,$updateEShipmentSQL,$updateEShipmentInvoiceIncIdSQL;
  $stmt = $dstConn->prepare($listEShipmentSQL);
  $stmt->execute(array(':sync_status' => 'N'));
  $eShipments = $stmt->fetchAll(PDO::FETCH_ASSOC);
  var_dump($eShipments);
  foreach($eShipments as $eShipment){
    $syncResult = array(
      'm_shipment_inc_id' => $eShipment['m_shipment_inc_id'],
      'm_invoice_inc_id' => $eShipment['m_invoice_inc_id'],
      'sync_status' => 'F',
      'sync_notes' => ''
    );
    try {
      $orderId = $eShipment['m_order_inc_id'];
      $order = $objectManager->create('Magento\Sales\Model\Order')->loadByAttribute('increment_id', $orderId);
      $stmt = $dstConn->prepare($listEShipmentItemSQL);
      $stmt->execute(array(':e_shipment_id' => $eShipment['id']));
      $eShipmentItems = $stmt->fetchAll(PDO::FETCH_ASSOC);
      //var_dump($eShipmentItems);
      $items = array();
      foreach($eShipmentItems as $eShipmentItem){
        $item = getOrderItemFromSku($order,$eShipmentItem);
        if (!empty($item)){
          foreach($item as $orderItemId => $qty){
            $items[$orderItemId] = $qty;
          }
        }
      }
      var_dump($items);
      $shipmentSyncResult = createShipment($order,$items,$eShipment);
      $invoicSyncResult = createInvoice($order,array());
      if (!empty($shipmentSyncResult['m_shipment_inc_id'])){
        $syncResult['m_shipment_inc_id'] = $shipmentSyncResult['m_shipment_inc_id'];
      }
      if (!empty($invoicSyncResult['m_invoice_inc_id'])){
        $syncResult['m_invoice_inc_id'] = $invoicSyncResult['m_invoice_inc_id'];
      }
      $syncResult['sync_notes'] .= $shipmentSyncResult['sync_notes']."\n".$invoicSyncResult['sync_notes'];
      /*if ($shipmentSyncResult['sync_status'] == 'F' or $invoicSyncResult['sync_status'] == 'F') {
        $syncResult['sync_status'] = 'F';
      } else {
        $syncResult['sync_status'] = 'O';
      }*/
      //Create invoice once all shipped and update the DST m_invoice_inc_id
      $syncResult['sync_status'] = $shipmentSyncResult['sync_status'];
      if (!empty($syncResult['m_invoice_inc_id']) && !empty($syncResult['m_shipment_inc_id'])){
        $syncResult['sync_status'] = 'O';
      }
      if ($invoicSyncResult['sync_status'] == 'O') {
        $updStmt = $dstConn->prepare($updateEShipmentInvoiceIncIdSQL);
        $updStmt->execute(
            array(
                ":m_invoice_inc_id" => $syncResult['m_invoice_inc_id'],
                ":m_order_inc_id"=>$eShipment["m_order_inc_id"],
              ));
      }
    } catch (Exception $error) {
      $syncResult['sync_notes'] = "Failed to create shipment: \n";
      $syncResult['sync_notes'] .= $error->getMessage() . "\n";
    }
    var_dump($syncResult);
    $updateStmt = $dstConn->prepare($updateEShipmentSQL);
    $updateStmt->execute(
        array(
            ":m_shipment_inc_id" => $syncResult['m_shipment_inc_id'],
            ":m_invoice_inc_id" => $syncResult['m_invoice_inc_id'],
            ":sync_status" => $syncResult['sync_status'],
            ":sync_notes" => $syncResult['sync_notes'],
            ":id"=>$eShipment["id"],
          ));
  }
}

function createShipment($order,$items,$eShipment){
  global $objectManager,$notifyShipment;
  $syncResult = array(
    'm_shipment_inc_id' => $eShipment['m_shipment_inc_id'],
    'sync_status' => 'F',
    'sync_notes' => ''
  );
  try {
    if($order->canShip()){
      $tracking[] = array(
          'carrier_code' => 'custom',
          'title' => $eShipment['carrier'],
          'number' => $eShipment["tracking"]
      );
      $shipment = $objectManager->create('Magento\Sales\Model\Order\ShipmentFactory')->create($order,$items, $tracking);
      $shipment->register();
      $shipment->getOrder()->setIsInProcess(true);
      $transaction = $objectManager->create('Magento\Framework\DB\Transaction');
      $transaction->addObject($shipment)
                  ->addObject($shipment->getOrder())
                  ->save();
      $syncResult['m_shipment_inc_id'] = $shipment->getIncrementId();
      $syncResult['sync_status'] = 'O';
      $syncResult['sync_notes'] = "Shipment has been created!";
      if ($notifyShipment) {
        $send = $objectManager->create('Magento\Sales\Model\Order\Email\Sender\ShipmentSender')->send($shipment);
      }
      $order->addStatusHistoryComment(__('Shipment #%1 has been created.', $shipment->getIncrementId()))
            ->setIsCustomerNotified($notifyShipment)
            ->save();
    } else {
      $syncResult['sync_status'] = 'F';
      $syncResult['sync_notes'] = "Order cannot be shipped!";
    }
  } catch (Exception $error) {
    $syncResult['sync_notes'] = "Failed to create shipment: \n";
    $syncResult['sync_notes'] .= $error->getMessage() . "\n";
  }
  //var_dump($syncResult);
  return $syncResult;
}


function createInvoice($order,$items,$captureOption='online'){
  global $objectManager,$notifyInvoice;
  $syncResult = array(
    'm_invoice_inc_id' => '',
    'sync_status' => 'F',
    'sync_notes' => ''
  );
  try {
    if ($order->canInvoice() && !$order->canShip()) {
      $invoice = $objectManager->create('Magento\Sales\Model\Service\InvoiceService')->prepareInvoice($order,$items);
      if (!$invoice->getTotalQty()) {
        $syncResult['sync_notes'] = "Invoice cannot be created without products.";
        return $syncResult;
      }
      if ($captureOption == 'online'){
        $invoice->setRequestedCaptureCase(\Magento\Sales\Model\Order\Invoice::CAPTURE_ONLINE);
      } else if ($captureOption == 'offline'){
        $invoice->setRequestedCaptureCase(\Magento\Sales\Model\Order\Invoice::CAPTURE_OFFLINE);
      } else {
        $invoice->setRequestedCaptureCase(\Magento\Sales\Model\Order\Invoice::CAPTURE_NONE);
      }
      $invoice->register();
      $transaction = $objectManager->create('Magento\Framework\DB\Transaction')
                      ->addObject($invoice)
                      ->addObject($invoice->getOrder());
      $transaction->save();

      $syncResult['sync_status'] = 'O';
      $syncResult['sync_notes'] = "Invoice has been created.";
      $syncResult['m_invoice_inc_id'] = $invoice->getIncrementId();
      if ($notifyInvoice) {
        $send = $objectManager->create('Magento\Sales\Model\Order\Email\Sender\InvoiceSender')->send($invoice);
      }
      $order->addStatusHistoryComment(__('Invoice #%1 has been created.', $invoice->getIncrementId()))
            ->setIsCustomerNotified($notifyInvoice)
            ->save();
    } else {
      $syncResult['sync_notes'] = "Order cannot be invoiced.";
    }
  } catch (Exception $error) {
    $syncResult['sync_notes'] = "Failed to create invoice: \n";
    $syncResult['sync_notes'] .= $error->getMessage() . "\n";
  }
  //var_dump($syncResult);
  return $syncResult;
}

try {
  $dstConn = new PDO("mysql:host=$dstServerHost;dbname=$dstDatabase", $dstUsername, $dstPassword);
  print "Connected to ".$dstServerHost." ".$dstDatabase."\n";
} catch (Exception $error) {
  print "Failed to connect to DST with error: \n";
  print $error->getMessage() . "\n";
  exit(0);
}
$bootstrap = \Magento\Framework\App\Bootstrap::create(BP, $_SERVER);
$app = $bootstrap->createApplication('Magento\Framework\App\Http');
$bootstrap->run($app);
$objectManager = \Magento\Framework\App\ObjectManager::getInstance();
updateShipment();
$dstConn = null;

?>

