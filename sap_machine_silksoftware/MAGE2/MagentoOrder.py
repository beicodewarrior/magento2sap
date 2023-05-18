# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoOrder.py
# Compiled at: 2016-06-18 20:45:10
__author__ = 'sandy.tu'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import json, csv, decimal
from MagentoCommon import MagentoCore
from utility.DSTControl import DSTControl

class MagentoOrder(MagentoCore):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoCore.__init__(self, mageConf, mageConn)
        self.mageApi = mageApi
        self.dstCursor = dstCursor
        self.dstControl = DSTControl(dstCursor)
        queries = {'isCanInvoiceSQL': '\n                SELECT entity_id, increment_id, base_grand_total, base_total_invoiced\n                FROM sales_order\n                WHERE increment_id = %s', 
           'getOrderLineItemBySkuSQL': '\n                SELECT a.item_id\n                FROM sales_order_item a, sales_order b\n                WHERE a.parent_item_id is null AND\n                    a.order_id = b.entity_id AND\n                    a.sku = %s AND\n                    b.increment_id = %s\n            ', 
           'getOrderPaymentMethodSQL': '\n                SELECT method\n                FROM sales_order_payment\n                WHERE parent_id = %s\n            ', 
           'updateMagentoOrderStatusSQL': '\n                UPDATE sales_order\n                SET status = %s\n                WHERE increment_id = %s\n            ', 
           'getShippingMatrixDeliveryTypeSQL': '\n                SELECT delivery_type FROM shipping_matrixrate\n                WHERE pk = %s\n            ', 
           'isOrderHasShipmentSQL': '\n                SELECT count(*)\n                FROM sales_order o\n                INNER JOIN sales_flat_shipment s ON o.entity_id = s.order_id\n                WHERE o.increment_id = %s\n            ', 
           'isOrderCompletedShipmentSQL': "\n                SELECT o.total_qty_ordered - IFNULL(ship.total_qty,0) AS cnt\n                FROM sales_order o\n                LEFT JOIN (\n                    SELECT sum(total_qty) as total_qty, order_id\n                    FROM sales_flat_shipment s\n                    INNER JOIN sales_order o ON s.order_id = o.entity_id\n                    WHERE o.increment_id = %s\n                    GROUP BY order_id\n                ) ship ON o.entity_id = ship.order_id\n                WHERE o.increment_id = %s and o.status != 'complete'\n            ", 
           'getOrderStatusSQL': '\n                SELECT status FROM sales_flat_order WHERE increment_id = %s\n            ', 
           'getOrderIdByOrderIncIdSQL': '\n                SELECT entity_id FROM sales_order WHERE increment_id = %s\n            '}
        self.queries = dict(self.queries, **queries)
        self.dstQueries = {'mOrderFieldUpdateSQL': '\n                UPDATE m_order\n                SET {columnName} = %s\n                WHERE id = %s\n            ', 
           'mOrderStatusUpdateSQL': '\n                UPDATE m_order\n                SET m_order_status = %s,\n                sync_dt = now(),\n                sync_notes = %s,\n                sync_status = %s\n                WHERE id = %s\n            ', 
           'updateShipmethodFromDeliveryTypeSQL': '\n                UPDATE m_order\n                SET shipment_method = %s\n                WHERE id = %s\n            ', 
           'getMOrderSQL': '\n                SELECT * FROM m_order WHERE id = %s\n            ', 
           'getMOrderItemSQL': '\n                SELECT * FROM m_order_item WHERE m_order_id = %s\n            ', 
           'updateMOrderFormattedData': '\n                UPDATE m_order\n                SET formatted_data = %s\n                WHERE id = %s\n            ', 
           'getExistingInvoiceSQL': '\n                SELECT count(*) FROM e_shipment WHERE m_order_inc_id = %s\n            '}
        self.mOrderQueryMap = {'fields': {'id': 'sales_order.entity_id', 
                      'm_order_inc_id': 'sales_order.increment_id', 
                      'm_order_date': 'sales_order.created_at', 
                      'm_order_status': 'sales_order.status', 
                      'e_customer_id': 'NULL', 
                      'm_customer_group': 'customer_group.customer_group_code', 
                      'm_store_id': 'sales_order.store_id', 
                      'm_customer_id': 'sales_order.customer_id', 
                      'shipment_carrier': "''", 
                      'shipment_method': 'IFNULL(sales_order.shipping_method,"")', 
                      'billto_firstname': 'IFNULL(bill_to.firstname,"")', 
                      'billto_lastname': 'IFNULL(bill_to.lastname,"")', 
                      'billto_email': 'IFNULL(bill_to.email,"")', 
                      'billto_companyname': 'IFNULL(bill_to.company,"")', 
                      'billto_address': 'IFNULL(bill_to.street,"")', 
                      'billto_city': 'IFNULL(bill_to.city,"")', 
                      'billto_region': 'IFNULL(bill_to_region.code,"")', 
                      'billto_country': 'IFNULL(bill_to.country_id,"")', 
                      'billto_postcode': 'IFNULL(bill_to.postcode,"")', 
                      'billto_telephone': 'IFNULL(bill_to.telephone,"")', 
                      'shipto_firstname': 'IFNULL(ship_to.firstname,"")', 
                      'shipto_lastname': 'IFNULL(ship_to.lastname,"")', 
                      'shipto_companyname': 'IFNULL(ship_to.company,"")', 
                      'shipto_address': 'IFNULL(ship_to.street,"")', 
                      'shipto_city': 'IFNULL(ship_to.city,"")', 
                      'shipto_region': 'IFNULL(ship_to_region.code,"")', 
                      'shipto_country': 'IFNULL(ship_to.country_id,"")', 
                      'shipto_postcode': 'IFNULL(ship_to.postcode,"")', 
                      'shipto_telephone': 'IFNULL(ship_to.telephone,"")', 
                      'total_qty': 'IFNULL(sales_order.total_qty_ordered,0)', 
                      'sub_total': 'IFNULL(sales_order.subtotal,0)', 
                      'discount_amt': 'IFNULL(sales_order.discount_amount,0)', 
                      'shipping_amt': 'IFNULL(sales_order.shipping_amount,0)', 
                      'tax_amt': 'IFNULL(sales_order.tax_amount,0)', 
                      'giftcard_amt': '0', 
                      'storecredit_amt': '0', 
                      'grand_total': 'sales_order.grand_total', 
                      'coupon_code': 'sales_order.coupon_code', 
                      'shipping_tax_amt': 'IFNULL(sales_order.shipping_tax_amount,0)', 
                      'sync_status': "'N'", 
                      'create_dt': 'now()', 
                      'sync_dt': 'now()', 
                      'sync_notes': "'Magento to DST'"}, 
           'source_tables': "\n                FROM\n                sales_order\n                LEFT JOIN sales_order_address bill_to on (sales_order.entity_id = bill_to.parent_id and bill_to.address_type = 'billing')\n                LEFT JOIN sales_order_address ship_to on (sales_order.entity_id = ship_to.parent_id and ship_to.address_type = 'shipping')\n                LEFT JOIN directory_country_region bill_to_region on (bill_to.region_id = bill_to_region.region_id and bill_to.country_id = bill_to_region.country_id)\n                LEFT JOIN directory_country_region ship_to_region on (ship_to.region_id = ship_to_region.region_id and ship_to.country_id = ship_to_region.country_id)\n                LEFT JOIN customer_entity customer on sales_order.customer_id = customer.entity_id\n                LEFT JOIN customer_group customer_group on customer.group_id = customer_group.customer_group_id\n            ", 
           'wheres': '\n                WHERE\n                sales_order.updated_at >= %s\n                ORDER BY sales_order.entity_id\n            ', 
           'target_table': 'm_order'}
        self.mOrderItemQueryMap = {'fields': {'id': 'sales_order_item.item_id', 
                      'm_order_id': 'sales_order_item.order_id', 
                      'sku': 'sales_order_item.sku', 
                      'name': 'sales_order_item.name', 
                      'uom': "''", 
                      'original_price': 'sales_order_item.original_price', 
                      'price': 'sales_order_item.price', 
                      'discount_amt': 'sales_order_item.discount_amount', 
                      'tax_amt': 'sales_order_item.tax_amount', 
                      'qty': 'sales_order_item.qty_ordered', 
                      'sub_total': 'sales_order_item.row_total'}, 
           'source_tables': '\n                FROM\n                    sales_order_item\n            ', 
           'wheres': '\n                WHERE\n                    parent_item_id is null and\n                    order_id = %s\n            ', 
           'target_table': 'm_order_item'}
        self.mOrderStatusHistoryQueryMap = {'fields': {'id': 'sales_order_status_history.entity_id', 
                      'm_order_inc_id': 'sales_order.increment_id', 
                      'is_customer_notified': 'sales_order_status_history.is_customer_notified', 
                      'is_visible_on_front': 'sales_order_status_history.is_visible_on_front', 
                      'comment': 'sales_order_status_history.comment', 
                      'm_order_status': 'sales_order_status_history.status', 
                      'comment_created_at': 'sales_order_status_history.created_at', 
                      'entity_name': 'sales_order_status_history.entity_name', 
                      'sync_status': "'N'", 
                      'create_dt': 'now()', 
                      'sync_dt': 'now()', 
                      'sync_notes': "'Magento to DST'"}, 
           'source_tables': '\n                FROM\n                    sales_order_status_history\n                INNER JOIN sales_order ON sales_order_status_history.parent_id = sales_order.entity_id\n            ', 
           'wheres': '\n                WHERE\n                    sales_order_status_history.comment is not null AND\n                    sales_order_status_history.created_at >= %s\n            ', 
           'target_table': 'm_order_status_history'}
        self.mOrderAdditionalFields = []
        self.timezoneDiff = 0
        self.shipmentEmailFlag = 1
        self.shipmentIncludeComment = 0
        self.needCreateInvoice = 1
        self.needCaptureInvoice = 1
        self.invoiceEmailFlag = 0
        self.invoiceIncludeComment = 0
        self.creditMemoNotifCustomer = 1
        self.creditMemoIncludeComment = 0
        self.creditMemoRefundToStoreCreditAmount = '0'
        self.afterShipStatus = 'complete'
        self._lastCutoffDt = ''
        self._orderToInvoiceMapping = {'baseCurrencyCode': 'base_currency_code', 
           'baseToGlobalRate': 'base_to_global_rate', 
           'baseToOrderRate': 'base_to_order_rate', 
           'billingAddressId': 'billing_address_id', 
           'globalCurrencyCode': 'global_currency_code', 
           'orderCurrencyCode': 'order_currency_code', 
           'orderId': 'entity_id', 
           'storeCurrencyCode': 'store_currency_code', 
           'storeId': 'store_id', 
           'storeToBaseRate': 'store_to_base_rate', 
           'storeToOrderRate': 'store_to_order_rate', 
           'baseShippingAmount': 'base_shipping_amount', 
           'baseShippingInclTax': 'base_shipping_incl_tax', 
           'baseShippingTaxAmount': 'base_shipping_tax_amount', 
           'shippingAmount': 'shipping_amount', 
           'shippingInclTax': 'shipping_incl_tax', 
           'shippingTaxAmount': 'shipping_tax_amount'}
        self._orderItemToInvoiceItemMapping = {'name': 'name', 
           'orderItemId': 'item_id', 
           'price': 'price', 
           'priceInclTax': 'price_incl_tax', 
           'basePrice': 'base_price', 
           'basePriceInclTax': 'base_price_incl_tax', 
           'productId': 'product_id', 
           'sku': 'sku'}
        self._orderToShipmentMapping = {'billingAddressId': 'billing_address_id', 
           'orderId': 'entity_id', 
           'customerId': 'customer_id', 
           'storeId': 'store_id'}
        self._orderItemToShipmentItemMapping = {'name': 'name', 
           'orderItemId': 'item_id', 
           'price': 'price', 
           'productId': 'product_id', 
           'sku': 'sku'}

    def generateGetFromMagentoSQL(self, queryMap):
        sql = 'SELECT '
        selects = []
        for alias in sorted(queryMap['fields']):
            column = queryMap['fields'][alias]
            selects.append(('{0} as {1}').format(column, alias))

        select = (', ').join(selects)
        sql = sql + select + ' ' + queryMap['source_tables'] + ' ' + queryMap['wheres']
        return sql

    def generateInsertDstTableSQL(self, queryMap):
        sql = 'REPLACE INTO ' + queryMap['target_table'] + ' ('
        columns = []
        i = 0
        for alias in sorted(queryMap['fields']):
            columns.append(alias)
            i = i + 1

        sql = sql + (', ').join(columns)
        values = ['%s'] * i
        sql = sql + ') VALUES (' + (', ').join(values) + ')'
        return sql

    def getNowStr(self, timezone=''):
        if timezone == 'UTC':
            now = datetime.utcnow()
        else:
            now = datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        return nowstr

    def convertTimezone(self, time, timezoneDiff=None):
        if time is None:
            return time
        else:
            if time == '':
                return time
            if timezoneDiff is None:
                if self.timezoneDiff is None:
                    timezoneDiff = 0
                else:
                    timezoneDiff = self.timezoneDiff
            adjTime = time - timedelta(hours=timezoneDiff)
            return adjTime

    def processMOrderAdditionalFields(self, mOrderId, mOrderInsertParam, mOrderAdditionalFields):
        return mOrderInsertParam

    def insertMOrderItem(self, mOrderId):
        mOrderItemGetSQL = self.generateGetFromMagentoSQL(self.mOrderItemQueryMap)
        mOrderItemInsertSQL = self.generateInsertDstTableSQL(self.mOrderItemQueryMap)
        self.mageCursor.execute(mOrderItemGetSQL, [mOrderId])
        columns = tuple([ d[0].decode('utf8') for d in self.mageCursor.description ])
        items = self.mageCursor.fetchall()
        for row in items:
            item = list(row)
            self.dstCursor.execute(mOrderItemInsertSQL, item)
            self.insertMOrderItemExt(dict(zip(columns, row)))

    def insertMOrderItemExt(self, orderItem):
        pass

    def getPaymentMethodByOrderId(self, orderId):
        self.mageCursor.execute(self.queries['getOrderPaymentMethodSQL'], [orderId])
        res = self.mageCursor.fetchall()
        methods = []
        if res is not None and len(res) > 0:
            for r in res:
                methods.append(r[0])

        paymentMethod = (',').join(methods)
        return paymentMethod

    def processPaymentMethodByOrderId(self, order):
        orderId = order['id']
        paymentMethod = self.getPaymentMethodByOrderId(orderId)
        paymentMethodPair = {'columnName': 'payment_method'}
        paymentMethodUpdateSQL = self.dstQueries['mOrderFieldUpdateSQL'].format(**paymentMethodPair)
        self.dstCursor.execute(paymentMethodUpdateSQL, [paymentMethod, orderId])

    def processCloseOrder(self, order):
        mOrderStatus = order['m_order_status']
        mOrderId = order['id']
        mOrderIncId = order['m_order_inc_id']
        syncNotes = ('{0}/{1} : Update order status from Magento').format(mOrderIncId, mOrderStatus)
        param = [mOrderStatus, syncNotes, 'N', mOrderId]
        self.dstCursor.execute(self.dstQueries['mOrderStatusUpdateSQL'], param)
        self.logger.info(syncNotes)

    def getShippingMatrixDeliveryType(self, shippingMethod):
        if shippingMethod is None:
            return
        else:
            pieces = shippingMethod.split('_')
            if len(pieces) < 3:
                return shippingMethod
            if pieces[0] == 'matrixrate' and pieces[1] == 'matrixrate':
                pk = pieces[2]
                self.mageCursor.execute(self.queries['getShippingMatrixDeliveryTypeSQL'], [pk])
                res = self.mageCursor.fetchone()
                if res is not None and len(res) > 0:
                    deliveryType = res[0]
                    return deliveryType
                return shippingMethod
            else:
                return shippingMethod
            return

    def updateShipmethodFromShippingMatrix(self, order):
        mOrderId = order['id']
        shippingMethod = order['shipment_method']
        deliveryType = self.getShippingMatrixDeliveryType(shippingMethod)
        self.dstCursor.execute(self.dstQueries['updateShipmethodFromDeliveryTypeSQL'], [deliveryType, mOrderId])

    def exportMagentoOrderExt(self, order):
        pass

    def mOrderToJson(self, mOrder):
        for key, value in mOrder.items():
            if value is not None and (type(value) == datetime or isinstance(value, decimal.Decimal)):
                mOrder[key] = str(value)

        mOrderId = mOrder['id']
        self.dstCursor.execute(self.dstQueries['getMOrderItemSQL'], mOrderId)
        items = self.fetchCursorResultAsDict(self.dstCursor)
        for item in items:
            for k, v in item.items():
                if v is not None and (type(v) == datetime or isinstance(v, decimal.Decimal)):
                    item[k] = str(v)

        mOrder['items'] = items
        return json.dumps(mOrder)

    def updateMOrderFormattedData(self, mOrderId, formattedData):
        self.dstCursor.execute(self.dstQueries['updateMOrderFormattedData'], [formattedData, mOrderId])
        self.logger.info(('Update m_order formatted data for : {0}').format(mOrderId))

    def syncMagentoOrderToDst(self):
        syncResult = {'sync_status': 'F', 
           'sync_notes': ''}
        try:
            start = self.getNowStr()
            newCutoffDt = self.getNowStr('UTC')
            task = 'order_mage_to_dst'
            if self._lastCutoffDt == '':
                lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
            else:
                lastCutoffDt = self._lastCutoffDt
            mOrderGetSQL = self.generateGetFromMagentoSQL(self.mOrderQueryMap)
            mOrderInsertSQL = self.generateInsertDstTableSQL(self.mOrderQueryMap)
            self.mageCursor.execute(mOrderGetSQL, [lastCutoffDt])
            result = self.fetchCursorResultAsDict(self.mageCursor)
            orders = []
            lastCutoffEntityId = None
            for r in result:
                if r['m_order_status'] in ['complete', 'canceled', self.afterShipStatus]:
                    self.processCloseOrder(r)
                    lastCutoffEntityId = r['id']
                    continue
                mOrderInsertParam = []
                mOrderId = None
                for alias in sorted(r):
                    if alias == 'id':
                        mOrderId = r[alias]
                    if alias == 'm_order_date':
                        mOrderDate = self.convertTimezone(r[alias])
                        mOrderInsertParam.append(mOrderDate)
                    else:
                        mOrderInsertParam.append(r[alias])

                mOrderInsertParam = self.processMOrderAdditionalFields(mOrderId, mOrderInsertParam, self.mOrderAdditionalFields)
                self.dstCursor.execute(mOrderInsertSQL, mOrderInsertParam)
                self.insertMOrderItem(mOrderId)
                self.processPaymentMethodByOrderId(r)
                self.exportMagentoOrderExt(r)
                lastCutoffEntityId = mOrderId
                self.logger.info(('Order To DST: {0}').format(r['m_order_inc_id']))

            if lastCutoffEntityId:
                syncStatus = 'O'
                lastCutoffDt = newCutoffDt
                lastStartDt = start
                lastEndDt = self.getNowStr()
                syncNotes = 'Sync from Magento to DST'
                self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
            else:
                syncStatus = 'I'
                syncNotes = 'No order needs to sync'
            syncResult['sync_status'] = syncStatus
            syncResult['sync_notes'] = syncNotes
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def isOrderHasShipment(self, mOrderIncId):
        self.mageCursor.execute(self.queries['isOrderHasShipmentSQL'], [mOrderIncId])
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0 and res[0] > 0:
            return True
        else:
            return False

    def isOrderCompletedShipment(self, mOrderIncId):
        self.mageCursor.execute(self.queries['isOrderCompletedShipmentSQL'], [mOrderIncId, mOrderIncId])
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0 and int(res[0]) == 0:
            return True
        else:
            return False

    def generateTrackComment(self, carrier='custom', title='', tracking=''):
        if tracking is None:
            tracking = ''
        if title is None:
            title = ''
        if carrier is None:
            carrier = ''
        comment = ('|').join([carrier, title, tracking])
        return comment

    def isCanInvoice(self, mOrderIncId):
        self.mageCursor.execute(self.queries['isCanInvoiceSQL'], [mOrderIncId])
        res = self.mageCursor.fetchone()
        flag = False
        if res is not None:
            entity_id, increment_id, base_grand_total, base_total_invoiced = res
            if base_total_invoiced < base_grand_total:
                flag = True
        return flag

    def getOrderLineItemBySku(self, mOrderIncId, sku):
        self.mageCursor.execute(self.queries['getOrderLineItemBySkuSQL'], [sku, mOrderIncId])
        row = self.mageCursor.fetchone()
        if row is not None and row[0] is not None:
            return int(row[0])
        else:
            return
            return

    def getOrderIdByOrderIncId(self, mOrderIncId):
        self.mageCursor.execute(self.queries['getOrderIdByOrderIncIdSQL'], [mOrderIncId])
        res = self.mageCursor.fetchone()
        mOrderId = None
        if res is not None and len(res) > 0:
            mOrderId = res[0]
        return mOrderId

    def importShipment(self, eShipment):
        mOrderIncId = eShipment['m_order_inc_id']
        syncResult = {'id': eShipment['id'], 
           'm_order_inc_id': mOrderIncId, 
           'm_shipment_inc_id': eShipment['m_shipment_inc_id'], 
           'm_invoice_inc_id': eShipment['m_invoice_inc_id'], 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            mOrderId = self.getOrderIdByOrderIncId(mOrderIncId)
            if mOrderId is None:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Order Inc Id: {0} is not found').format(mOrderIncId)
                self.logger.exception(syncResult['sync_notes'])
                return syncResult
            shipmentData = {'entity': {'orderId': mOrderId, 
                          'items': []}}
            mOrderIncId = eShipment['m_order_inc_id']
            carrier = eShipment['carrier']
            tracking = eShipment['tracking']
            for line in eShipment['lines']:
                sku = line['sku']
                qty = line['qty']
                orderItemId = self.getOrderLineItemBySku(mOrderIncId, sku)
                if orderItemId is None:
                    continue
                else:
                    item = {'orderItemId': orderItemId, 
                       'qty': qty}
                    shipmentData['entity']['items'].append(item)

            try:
                orderData = self.getOrderDataThroughApi(mOrderId)
                shipmentData = self.generateShipmentApiData(shipmentData, orderData)
                mShipment = self.mageApi.createShipment(shipmentData)
                mShipmentId = mShipment['entity_id']
                mShipmentIncId = mShipment['increment_id']
                syncResult['m_shipment_inc_id'] = mShipmentIncId
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = syncResult['sync_notes'] + ('\nshipment {0} create successfully for {1}').format(mShipmentIncId, mOrderIncId)
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Failed to create shipment for order Inc Id: {0} with error: {1}').format(mOrderIncId, traceback.format_exc())
                self.logger.exception(syncResult['sync_notes'])
                return syncResult
            else:
                trackData = {'entity': {'carrierCode': 'custom', 
                              'orderId': mOrderId, 
                              'parentId': mShipmentId, 
                              'title': carrier, 
                              'trackNumber': tracking}}
                try:
                    mTrack = self.mageApi.createShipmentTrack(trackData)
                    mTrackId = mTrack['entity_id']
                    syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n track {0} create successfully for shipment {1}').format(mTrackId, mShipmentIncId)
                    syncResult['sync_status'] = 'O'
                except Exception as e:
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = ('Failed to create track for shipment: {0} with error: {1}').format(mShipmentIncId, traceback.format_exc())
                    self.logger.exception(syncResult['sync_notes'])
                    return syncResult

            if self.needCreateInvoice == True:
                invoiceSyncResult = self.importInvoice(mOrderId, shipmentData['entity']['items'])
                if invoiceSyncResult['sync_status'] == 'O':
                    syncResult['m_invoice_inc_id'] = invoiceSyncResult['m_invoice_inc_id']
                    if self.needCaptureInvoice == True:
                        captureResult = self.captureInvoice(invoiceSyncResult['m_invoice_id'])
                        syncResult['sync_notes'] = syncResult['sync_notes'] + '\n' + captureResult['sync_notes']
                syncResult['sync_notes'] = syncResult['sync_notes'] + '\n' + invoiceSyncResult['sync_notes']
            syncResult = self.importShipmentExt(eShipment, syncResult)
        except Exception as e:
            error = traceback.format_exc()
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def generateShipmentApiData(self, shipmentData, orderData):
        shipmentEntity = self.orderToShipment(orderData)
        shipmentEntity['items'] = []
        for item in shipmentData['entity']['items']:
            shipmentItemData = {}
            orderItemId = item['orderItemId']
            for orderItem in orderData['items']:
                if orderItemId == orderItem['item_id']:
                    shipmentItemData = self.orderItemToShipmentItem(orderItem)
                    shipmentItemData['qty'] = item['qty']
                    shipmentItemData = self.calculateShipmentItemData(shipmentItemData, orderItem)
                    shipmentEntity['items'].append(shipmentItemData)

        shipmentEntity = self.calculateShipmentData(shipmentEntity, orderData)
        shipmentData = {'entity': shipmentEntity}
        return shipmentData

    def mappingData(self, source, mapping):
        target = {}
        for k, v in mapping.items():
            if v in source:
                target[k] = source[v]

        return target

    def orderToShipment(self, orderData, mapping={}):
        if len(mapping) == 0:
            mapping = self._orderToShipmentMapping
        shipmentData = self.mappingData(orderData, mapping)
        return shipmentData

    def orderItemToShipmentItem(self, orderItem, mapping={}):
        if len(mapping) == 0:
            mapping = self._orderItemToShipmentItemMapping
        shipmentItem = self.mappingData(orderItem, mapping)
        return shipmentItem

    def calculateShipmentData(self, shipmentData, orderData):
        totalQty = 0
        totalWeight = 0
        for item in shipmentData['items']:
            totalWeight = totalWeight + item['weight']
            totalQty = totalQty + item['qty']

        return shipmentData

    def calculateShipmentItemData(self, shipmentItemData, orderItem):
        if orderItem['qty_ordered'] == 0:
            percentage = 0
        else:
            percentage = float(shipmentItemData['qty']) / orderItem['qty_ordered']
        shipmentItemData['rowTotal'] = orderItem['row_total'] * percentage
        shipmentItemData['weight'] = orderItem['weight'] * percentage
        return shipmentItemData

    def importShipmentExt(self, eShipment, syncResult):
        return syncResult

    def setMagentoOrderStatus(self, mOrderIncId, orderStatus):
        self.mageCursor.execute(self.queries['updateMagentoOrderStatusSQL'], [orderStatus, mOrderIncId])

    def importCreditMemo(self, eCreditMemo):
        syncResult = {'id': eCreditMemo['id'], 
           'm_order_inc_id': eCreditMemo['m_order_inc_id'], 
           'm_credit_memo_inc_id': eCreditMemo['m_credit_memo_inc_id'], 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            itemsQty = {}
            mOrderIncId = eCreditMemo['m_order_inc_id']
            for line in eCreditMemo['lines']:
                sku = line['sku']
                qty = line['qty']
                orderItemId = self.getOrderLineItemBySku(mOrderIncId, sku)
                if orderItemId is None:
                    continue
                if orderItemId in itemsQty:
                    itemsQty[orderItemId] = itemsQty[orderItemId] + qty
                else:
                    itemsQty[orderItemId] = qty

            items = []
            for k, v in itemsQty.items():
                items.append({'order_item_id': str(k), 'qty': str(float(v))})

            creditMemoData = {'qtys': items, 'shipping_amount': eCreditMemo['shipping_amount'], 
               'adjustment_positive': eCreditMemo['adjustment_positive'], 
               'adjustment_negative': eCreditMemo['adjustment_negative']}
            comment = eCreditMemo['comment']
            mCreditMemoIncId = self.mageApi.createSalesOrderCreditmemo(eCreditMemo['m_order_inc_id'], creditMemoData, comment, self.creditMemoNotifCustomer, self.creditMemoIncludeComment, self.creditMemoRefundToStoreCreditAmount)
            syncResult['m_credit_memo_inc_id'] = mCreditMemoIncId
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('order_increment_id/credit_memo_inc_id : {0}/{1}').format(eCreditMemo['m_order_inc_id'], mCreditMemoIncId)
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def syncMagentoOrderStatusHistoryToDst(self):
        syncResult = {'sync_status': 'F', 
           'sync_notes': ''}
        try:
            start = self.getNowStr()
            task = 'order_status_hist_mage_to_dst'
            lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
            mOrderStatusHistoryGetSQL = self.generateGetFromMagentoSQL(self.mOrderStatusHistoryQueryMap)
            mOrderStatusHistoryInsertSQL = self.generateInsertDstTableSQL(self.mOrderStatusHistoryQueryMap)
            self.mageCursor.execute(mOrderStatusHistoryGetSQL, [lastCutoffDt])
            result = self.fetchCursorResultAsDict(self.mageCursor)
            orders = []
            lastCutoffEntityId = None
            for r in result:
                insertParam = []
                commentId = None
                for alias in sorted(r):
                    if alias == 'id':
                        commentId = r[alias]
                    if alias == 'comment_created_at':
                        commentCreatedAt = self.convertTimezone(r[alias])
                        insertParam.append(commentCreatedAt)
                    else:
                        insertParam.append(r[alias])

                self.dstCursor.execute(mOrderStatusHistoryInsertSQL, insertParam)
                if lastCutoffEntityId < commentId:
                    lastCutoffEntityId = commentId
                self.logger.info(('{0} Order Status History To DST: {1}').format(r['id'], r['m_order_inc_id']))

            if lastCutoffEntityId:
                syncStatus = 'O'
                lastCutoffDt = start
                lastStartDt = start
                lastEndDt = self.getNowStr()
                syncNotes = 'Sync from Magento to DST'
                self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
            else:
                syncStatus = 'I'
                syncNotes = 'No order status history needs to sync'
            syncResult['sync_status'] = syncStatus
            syncResult['sync_notes'] = syncNotes
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def getOrderStatus(self, mOrderIncId):
        self.mageCursor.execute(self.queries['getOrderStatusSQL'], [mOrderIncId])
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            return res[0]
        else:
            return

    def updateMagentoOrderStatus(self, mOrder, updateOrderStatus):
        syncResult = {'id': mOrder['id'], 
           'm_order_inc_id': mOrder['m_order_inc_id'], 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            mOrderIncId = mOrder['m_order_inc_id']
            orderStatus = self.getOrderStatus(mOrderIncId)
            if orderStatus == updateOrderStatus:
                syncNotes = ('order:{0} is status {1} in Magento').format(mOrderIncId, orderStatus)
                syncStatus = 'I'
            else:
                self.mageApi.addSalesOrderComment(mOrderIncId, updateOrderStatus, '')
                syncNotes = ('order:{0} update to {1}').format(mOrderIncId, updateOrderStatus)
                syncStatus = 'O'
        except Exception as e:
            syncNotes = ('Failed to update order:{0} to {1}').format(mOrderIncId, updateOrderStatus)
            syncNotes = syncNotes + (' with error: {0}').format(traceback.format_exc())
            syncStatus = 'F'

        self.logger.info(syncNotes)
        syncResult['sync_notes'] = syncNotes
        syncResult['sync_status'] = syncStatus
        return syncResult

    def getOrderDataThroughApi(self, mOrderId):
        orderData = self.mageApi.getOrderById(mOrderId)
        return orderData

    def orderToInvoice(self, orderData, mapping={}):
        if len(mapping) == 0:
            mapping = self._orderToInvoiceMapping
        invoiceData = self.mappingData(orderData, mapping)
        return invoiceData

    def orderItemToInvoiceItem(self, orderItem, mapping={}):
        if len(mapping) == 0:
            mapping = self._orderItemToInvoiceItemMapping
        invoiceItem = self.mappingData(orderItem, mapping)
        return invoiceItem

    def generateInvoiceComments(self, orderData, comments):
        return comments

    def calculateInvoiceData(self, invoiceData, orderData, includeShippingAmount=True):
        baseSubtotal = 0
        baseSubtotalInclTax = 0
        baseTaxAmount = 0
        baseTotalRefunded = 0
        discountAmount = 0
        grandTotal = 0
        subtotal = 0
        subtotalInclTax = 0
        taxAmount = 0
        totalQty = 0
        for item in invoiceData['items']:
            baseSubtotal = baseSubtotal + item['baseRowTotal']
            baseSubtotalInclTax = baseSubtotalInclTax + item['baseRowTotal']
            baseTaxAmount = baseTaxAmount + item['baseTaxAmount']
            discountAmount = discountAmount + item['discountAmount']
            subtotal = subtotal + item['rowTotal']
            subtotalInclTax = subtotalInclTax + item['rowTotalInclTax']
            taxAmount = taxAmount + item['taxAmount']
            totalQty = totalQty + item['qty']

        invoiceData['baseSubtotal'] = baseSubtotal
        invoiceData['baseSubtotalInclTax'] = baseSubtotalInclTax
        invoiceData['baseTaxAmount'] = baseTaxAmount
        invoiceData['discountAmount'] = discountAmount
        invoiceData['subtotal'] = subtotal
        invoiceData['subtotalInclTax'] = subtotalInclTax
        invoiceData['taxAmount'] = taxAmount
        invoiceData['totalQty'] = totalQty
        if includeShippingAmount == True:
            invoiceData['grandTotal'] = subtotal + taxAmount + invoiceData['shippingAmount'] - discountAmount
        else:
            invoiceData['grandTotal'] = subtotal + taxAmount - discountAmount
        return invoiceData

    def calculateInvoiceItemData(self, invoiceItemData, orderItem):
        if orderItem['qty_ordered'] == 0:
            percentage = 0
        else:
            percentage = float(invoiceItemData['qty']) / orderItem['qty_ordered']
        invoiceItemData['baseDiscountAmount'] = orderItem['base_discount_amount'] * percentage
        invoiceItemData['baseDiscountTaxCompensationAmount'] = orderItem['base_discount_tax_compensation_amount'] * percentage
        invoiceItemData['baseRowTotal'] = orderItem['base_row_total'] * percentage
        invoiceItemData['baseRowTotalInclTax'] = orderItem['base_row_total_incl_tax'] * percentage
        invoiceItemData['baseTaxAmount'] = orderItem['base_tax_amount'] * percentage
        invoiceItemData['discountAmount'] = orderItem['discount_amount'] * percentage
        invoiceItemData['discountTaxCompensationAmount'] = orderItem['discount_tax_compensation_amount'] * percentage
        invoiceItemData['rowTotal'] = orderItem['row_total'] * percentage
        invoiceItemData['rowTotalInclTax'] = orderItem['row_total_incl_tax'] * percentage
        invoiceItemData['taxAmount'] = orderItem['tax_amount'] * percentage
        return invoiceItemData

    def importInvoice(self, mOrderId, items, comments=[], orderData={}, includeShippingAmount=True):
        syncResult = {'m_order_id': mOrderId, 
           'm_invoice_id': None, 
           'm_invoice_inc_id': None, 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            if len(orderData) == 0:
                orderData = self.getOrderDataThroughApi(mOrderId)
            includeShippingAmount = self.shouldInvoiceIncludeShippingAmount(mOrderId)
            invoiceData = self.orderToInvoice(orderData)
            invoiceData['items'] = []
            for item in items:
                orderItemId = item['orderItemId']
                for orderItem in orderData['items']:
                    if orderItemId == orderItem['item_id']:
                        invoiceItemData = self.orderItemToInvoiceItem(orderItem)
                        invoiceItemData['qty'] = item['qty']
                        invoiceItemData = self.calculateInvoiceItemData(invoiceItemData, orderItem)
                        invoiceData['items'].append(invoiceItemData)

            invoiceData = self.calculateInvoiceData(invoiceData, orderData, includeShippingAmount)
            invoiceData['comments'] = self.generateInvoiceComments(orderData, comments)
            invoiceEntity = {'entity': invoiceData}
            mInvoice = self.mageApi.createInvoice(invoiceEntity)
            syncResult['m_invoice_inc_id'] = mInvoice['increment_id']
            syncResult['m_invoice_id'] = mInvoice['entity_id']
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('Invoice created for {0}').format(mOrderId)
        except Exception as e:
            error = traceback.format_exc()
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def captureInvoice(self, invoiceId):
        syncResult = {'m_invoice_id': invoiceId, 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            result = self.mageApi.captureInvoice(invoiceId)
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('Invoice {0} has been captured').format(invoiceId)
        except Exception as e:
            error = traceback.format_exc()
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def shouldInvoiceIncludeShippingAmount(self, mOrderIncId):
        self.dstCursor.execute(self.dstQueries['getExistingInvoiceSQL'], [mOrderIncId])
        res = self.dstCursor.fetchone()
        flag = True
        if res is not None and len(res) > 0:
            if res[0] > 0:
                flag = False
        return flag
# okay decompiling MagentoOrder.pyc
