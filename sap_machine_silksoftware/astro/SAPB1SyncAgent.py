# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: C:\Users\silksoftware\Documents\magedst\astro\SAPB1SyncAgent.py
# Compiled at: 2017-11-02 00:25:44
import sys
reload(sys)
sys.path.insert(0, '..')
sys.setdefaultencoding('utf-8')
from SAPB1.SAPB1Sync2 import SAPB1Sync2
import traceback
from datetime import datetime
import json
from utility.utility import DecimalEncoder
import MySQLdb, decimal
from datetime import datetime, timedelta
from time import time

class SAPB1SyncAstro(SAPB1Sync2):

    def __init__(self, sapb1di_conf, dst_conf, connect_di=True):
        SAPB1Sync2.__init__(self, sapb1di_conf, dst_conf, connect_di)
        self.warehouseCodes = ['001']
        self.dstControl.defaultCutoffDt = '2015-10-01'
        self.bpPaymentMethods = ['Incoming Pmnt', 'Incoming BT', 'Incoming BT 02']
        self.downpaymentMethods = ['cashondelivery']
        self.priceList = '8'
        self._docDuteDate = 0
        self.productMasterQueryMap = {'fields': {'ProductType': 'V33_Magento_Link.[ProductType]', 
                      'sku': 'V33_Magento_Link.[sku]', 
                      'Sync': 'V33_Magento_Link.[Sync]', 
                      'name': 'V33_Magento_Link.[name]', 
                      'Attr_Set': 'V33_Magento_Link.[Attr_Set]', 
                      'Attributes': 'V33_Magento_Link.[Attributes]', 
                      'Brand': 'V33_Magento_Link.[Brand]', 
                      'Manufacturer': 'V33_Magento_Link.[Manufacturer]', 
                      'Paper_Weight': 'V33_Magento_Link.[Paper_Weight]', 
                      'Category': 'V33_Magento_Link.[Category]', 
                      'Thickness': 'V33_Magento_Link.[Thickness]', 
                      'Finish': 'V33_Magento_Link.[Finish]', 
                      'Size': 'V33_Magento_Link.[Size]', 
                      'Color': 'V33_Magento_Link.[Color]', 
                      'Pack_Size': 'V33_Magento_Link.[Pack_Size]', 
                      'Grain_Direction': 'V33_Magento_Link.[Grain_Direction]', 
                      'Env_Format': 'V33_Magento_Link.[Env_Format]', 
                      'Weight': 'V33_Magento_Link.[Weight]', 
                      'Website_Code': 'V33_Magento_Link.[Website_Code]', 
                      'short_desc': 'V33_Magento_Link.[short_desc]', 
                      'long_desc': 'V33_Magento_Link.[long_desc]', 
                      'UpdateDate': 'V33_Magento_Link.[UpdateDate]', 
                      'Recycled': 'V33_Magento_Link.[Recycled]', 
                      'Acid_Free': 'V33_Magento_Link.[Acid Free]', 
                      'Laser_Compatible': 'V33_Magento_Link.[Laser Compatible]', 
                      'FSC_Certified': 'V33_Magento_Link.[FSC Certified]', 
                      'Cotton': 'V33_Magento_Link.[100% Cotton]', 
                      'Tree_Free': 'V33_Magento_Link.[Tree Free]', 
                      'Width': 'V33_Magento_Link.[Width]', 
                      'Length': 'V33_Magento_Link.[Length]', 
                      'validFor': "'Y'", 
                      'Spec_Color': 'V33_Magento_Link.[SpecColor]', 
                      'Env_Type': 'V33_Magento_Link.[EnvType]', 
                      'Update_to_Sync': 'OITM.U_V33_UPDATE_TO_SYNC'}, 
           'source_tables': '\n                FROM V33_Magento_Link AS V33_Magento_Link\n                INNER JOIN OITM ON OITM.ItemCode = V33_Magento_Link.sku\n            ', 
           'wheres': "\n                WHERE '8' = %s and\n                (V33_Magento_Link.updateDate >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n                OR V33_Magento_Link.updateDate IS NULL)\n                AND OITM.U_V33_UPDATE_TO_SYNC = 'Y'\n            ", 
           'target_table': 'e_product_master'}
        self.sapb1Queries['listConfigProductSQL'] = '\n            SELECT\n            [Configurable],[Simple],A.Attributes,A.Attr_Set\n            FROM [dbo].[V33_Magento_Config_Simple_List] A\n            WHERE A.UpdateDate >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n        '
        self.sapb1Queries['listEProductPriceSQL'] = "\n            SELECT T0.ItemCode, T1.Price\n            FROM OITM T0\n            INNER JOIN ITM1 T1 ON T0.ItemCode = T1.ItemCode\n            INNER JOIN OPLN T2 ON T1.PriceList = T2.ListNum\n            WHERE\n            T0.SellItem = 'Y' AND\n            CASE\n                WHEN T0.updateDate IS NULL THEN T0.createDate\n                ELSE T0.updateDate END >= cast(floor(cast(CAST( %s AS datetime) AS float)) AS datetime)\n            AND T1.Pricelist = %s\n            AND T0.U_V33_PRODUCT_TYPE = 'Simple'\n            GROUP BY  T0.ItemCode, T1.Price\n        "
        self.sapb1Queries['listEProductTierPriceSQL'] = "\n            SELECT\n                ITM1.ItemCode, ITM1.Price,\n                OPLN.ListName AS CustomerGroup,\n                SPP2.Price AS TierPrice, SPP2.Amount AS Qty,\n                OITM.U_V33_PRICING_STRUC\n            FROM ITM1\n            INNER JOIN OITM ON OITM.ItemCode = ITM1.ItemCode\n            INNER JOIN OPLN ON OPLN.ListNum = ITM1.PriceList\n            LEFT JOIN OSPP ON OSPP.ItemCode = ITM1.ItemCode AND OSPP.ListNum = OPLN.ListNum\n            LEFT JOIN SPP2 ON SPP2.ItemCode = OSPP.ItemCode AND SPP2.CardCode = OSPP.CardCode\n            WHERE\n                OITM.U_V33_PRICING_STRUC IS NOT NULL AND LTRIM(RTRIM(OITM.U_V33_PRICING_STRUC)) != ''\n            AND\n                OPLN.ListName NOT IN ('_Vendor Price List', 'ZZ_Dont_use_Price List 10', 'ZZ-Dont_use_Customer Price List')\n            AND\n                (\n                    CASE WHEN OITM.UpdateDate IS NULL THEN OITM.CreateDate ELSE OITM.UpdateDate END\n                    >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n                    OR\n                    CASE WHEN OSPP.UpdateDate IS NULL THEN OSPP.CreateDate ELSE OSPP.UpdateDate END\n                    >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n                )\n            ORDER BY ITM1.ItemCode, OPLN.ListName;\n        "
        self.queries.listMOrderItemsSQL = "\n            SELECT * FROM m_order_item WHERE m_order_id = '%s';\n        "
        self._customCutFeeSku = 'CUSTOM CUT'
        self._handlingFeeSku = 'handling_fee'
        self.queries.listMInvoicesSQL = "SELECT m_order_inc_id, m_invoice_inc_id, e_shipment_inc_id\n                                FROM e_shipment\n                                WHERE sync_status = 'O'\n                                AND e_shipment_inc_id not in (\n                                    SELECT e_shipment_inc_id\n                                    FROM e_invoice\n                                    WHERE sync_status = 'O')\n                                AND m_invoice_inc_id IS NOT NULL\n                                AND m_invoice_inc_id != '';"
        self.sapb1Queries['listEShipmentsSQL'] = "\n            SELECT\n            t0.DocEntry,\n            t1.BaseEntry,\n            t1.ShipDate,\n            t0.TrackNo,\n            t4.PACK_TRACKINGNUM,\n            t1.Quantity,\n            t3.ItemCode,\n            ISNULL(t2.TrnspName,''),\n            t1.U_MageOrderLineId\n            FROM\n            ODLN t0 left join DLN1 t1 on (t0.DocEntry = t1.DocEntry)\n            LEFT JOIN OSHP t2 on (t0.TrnspCode = t2.TrnspCode)\n            INNER JOIN OITM t3 on t1.ItemCode = t3.ItemCode\n            LEFT JOIN [TWBS_SBO-Common].dbo.TWBS_UPS_Response t4 ON t4.DocNum = CONVERT(varchar, t0.DocNum)\n            WHERE t0.U_MageOrderIncId = %s\n        "
        self.sapb1Queries['listECustomerSQL'] = "\n            SELECT\n            OCRD.CardCode,\n            OCRD.CardName,\n            OCRD.ValidFor,\n            OPLN.ListName,\n            OSHP.TrnspName,\n            OCRD.IntrntSite,\n            OCPR.CntctCode,\n            OCTG.PymntGroup,\n            OCPR.E_MailL AS email,\n            OCRD.E_Mail AS bp_email,\n            OCPR.Name,\n            OCPR.FirstName,\n            OCPR.MiddleName,\n            OCPR.LastName,\n            OCPR.Gender,\n            OCRD.VatStatus,\n            OCRD.U_V33_MIN_PRIC_BRACK\n            FROM OCPR\n            INNER JOIN OCRD ON OCRD.CardCode = OCPR.CardCode AND OCRD.CardType = 'C'\n            INNER JOIN OPLN ON OCRD.ListNum = OPLN.ListNum\n            LEFT OUTER JOIN OCTG ON OCRD.GroupNum = OCTG.GroupNum\n            LEFT OUTER JOIN OSHP ON OCRD.ShipType = OSHP.TrnspCode\n            WHERE OCPR.updateDate >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n        "
        self.sapb1Queries['getECustomerTelphoneSQL'] = '\n            SELECT Tel1 FROM OCPR WHERE CardCode = %s AND Name = %s\n        '
        self.sapb1Queries['updateEProductUpdateToSyncSQL'] = '\n            UPDATE OITM SET U_V33_UPDATE_TO_SYNC = %s WHERE ItemCode = %s\n        '

    def __del__(self):
        if self.dstDb:
            self.dstDb.close()
            self.logger.info('Close DST database connection')

    def b1eOrderExtFunct(self, order, mOrder):
        order.UserFields.Fields.Item('U_WEB_ORDER').Value = 'Y'
        if mOrder['additional_fee'] != 0:
            handlingFeeItem = {'sku': self._handlingFeeSku, 'qty': '1', 
               'price': str(abs(mOrder['additional_fee'])), 
               'tax_amt': '0', 
               'custom_cut_width': '0', 
               'custom_cut_length': '0', 
               'custom_cut_total_cut': '0', 
               'id': '-999'}
            mOrder['items'].append(handlingFeeItem)

    def b1eOrderLineExtFunct(self, i, order, item, mOrder):
        order.Lines.SetCurrentLine(i)
        if 'cut_fee' not in item or decimal.Decimal(item['cut_fee']) <= 0:
            order.Lines.UserFields.Fields.Item('U_V33_CUST_WIDTH').Value = str(item['custom_cut_width'])
            order.Lines.UserFields.Fields.Item('U_V33_CUST_LENGTH').Value = str(item['custom_cut_length'])
            order.Lines.UserFields.Fields.Item('U_V33_TOTAL_CUT').Value = str(item['custom_cut_total_cut'])
        order.Lines.UserFields.Fields.Item('U_MageOrderLineId').Value = str(item['id'])

    def getCardCodeByEmail(self, email):
        cardCode = self.getDocEntry(email, 'oBusinessPartnersByEmail')
        return cardCode

    def getCardCodeByECustomerId(self, eCustomerId, mOrder):
        cardCode = self.getDocEntry(eCustomerId, 'oBusinessPartnersByCode')
        if cardCode is None or str(cardCode).strip() == '' or cardCode == 0:
            cardCode = self.getCardCodeByEmail(mOrder['billto_email'])
        return cardCode

    def getCardNameByEmail(self, email):
        cardName = self.getDocEntry(email, 'oBusinessPartnersNameByEmail')
        return cardName

    newCustomerListNum = None
    getListNumByNameSQL = ' SELECT TOP 1 ListNum FROM OPLN WHERE ListName = %s '

    def getListNumByName(self, listName):
        if self.newCustomerListNum is None:
            self.sapb1Cursor.execute(self.getListNumByNameSQL, listName)
            result = self.sapb1Cursor.fetchone()
            if result is not None and len(result) > 0:
                self.newCustomerListNum = result[0]
        return self.newCustomerListNum

    def b1eCustFunct(self, mCustomer):
        customer = self.company.GetBusinessObject(self.constants.oBusinessPartners)
        cardCode = self.getDocEntry(mCustomer['m_cust_inc_id'], 'oBusinessPartners')
        if cardCode is None or str(cardCode).strip() == '' or cardCode == 0:
            cardCode = self.getCardCodeByEmail(mCustomer['email'])
        exist = 1 if cardCode != 0 and str(cardCode).strip() != '' else 0
        if exist == 1:
            customer.GetByKey(cardCode)
        else:
            customer.CardCode = 'C' + self._cardCodePrefix + str(mCustomer['m_cust_inc_id'])
            customer.CardForeignName = mCustomer['m_cust_inc_id']
            customer.CardName = mCustomer['firstname'] + ' ' + mCustomer['lastname']
            customer.CardType = self.constants.cCustomer
            customer.CompanyPrivate = self.constants.cPrivate
            listNum = self.getListNumByName(self.sapb1di_conf['new_customer_price_list'])
            if listNum is not None:
                customer.PriceListNum = listNum
        return (
         customer, exist)

    def b1eCustAddrFunct(self, i, customer, address, mCustomer):
        customer.Addresses.Add()
        customer.Addresses.SetCurrentLine(i)
        customer.Addresses.AddressName = 'Address' + str(i + 1)
        if 'company' in address and address['company'] is not None and len(address['company'].strip()) > 0:
            if customer.Addresses.AddressType == self.constants.bo_BillTo or customer.Addresses.AddressType == self.constants.bo_ShipTo:
                customer.Addresses.AddressName = address['company']
            else:
                customer.Addresses.AddressName = address['company'] + str(i + 1)
        else:
            customer.Addresses.AddressName = 'Address' + str(i + 1)
        customer.Addresses.ZipCode = address['postcode']
        customer.Addresses.Street = address['street']
        customer.Addresses.City = address['city']
        customer.Addresses.Country = address['country_id']
        if 'region_id' in address and address['region_id'] is not None:
            customer.Addresses.State = address['region_id']
        if mCustomer['default_billing'] == address['entity_id']:
            customer.Addresses.AddressType = self.constants.bo_BillTo
        if mCustomer['default_shipping'] == address['entity_id']:
            customer.Addresses.AddressType = self.constants.bo_ShipTo
        return

    def b1eProductsTierPriceFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductTierPriceSQL'], params)
        eProductsTierPrice = self.fetchCursorResultAsDict(self.sapb1Cursor)
        result = []
        for tierPrice in eProductsTierPrice:
            if 'vendor' in tierPrice['CustomerGroup'].lower() or 'dont_use' in tierPrice['CustomerGroup'].lower():
                continue
            if tierPrice['U_V33_PRICING_STRUC'] == 'Parent Size':
                if tierPrice['TierPrice'] is None:
                    continue
            elif tierPrice['TierPrice'] is None:
                if tierPrice['Price'] is None:
                    continue
                else:
                    tierPrice['TierPrice'] = tierPrice['Price']
            if tierPrice['Qty'] is None:
                tierPrice['Qty'] = 0.001
            result.append(tierPrice)

        return result

    def b1mProductTierPriceFunct(self, eProductTierPrice):
        websiteCode = self._defaultWebsiteCode
        mProductTierPrice = {'sku': eProductTierPrice['ItemCode'], 
           'all_groups': 0, 
           'customer_group': eProductTierPrice['CustomerGroup'], 
           'qty': eProductTierPrice['Qty'], 
           'price': eProductTierPrice['TierPrice'], 
           'website_code': websiteCode, 
           'sync_status': 'N', 
           'sync_notes': 'ERP to DST'}
        return mProductTierPrice

    def b1eOrderLineFunct(self, i, order, item, mOrder):
        order.Lines.Add()
        order.Lines.SetCurrentLine(i)
        order.Lines.ItemCode = item['sku']
        order.Lines.Quantity = item['qty']
        order.Lines.Price = decimal.Decimal(item['price'])
        lineTotal = order.Lines.Price * order.Lines.Quantity
        taxCode = self.getTaxCode(lineTotal, float(item['tax_amt']), mOrder[self._taxPostcodeColumn], mOrder[self._taxCountryColumn])
        order.Lines.TaxCode = taxCode
        order.Lines.LineTotal = lineTotal

    def b1eShipsFunct(self):
        orderStatusFormatString = (',').join(['%s'] * len(self.needShipOrderStatus))
        self.queries.listNeedShipOrdersSQL = self.queries.listNeedShipOrdersSQL.format(mOrderStatus=orderStatusFormatString)
        self.dstCursor.execute(self.queries.listNeedShipOrdersSQL, self.needShipOrderStatus)
        needShipOrders = self.dstCursor.fetchall()
        eShips = {}
        for needShipOrder in needShipOrders:
            mOrderIncId = needShipOrder['m_order_inc_id']
            existingShipments = self.getOrderExistingShipment(mOrderIncId)
            self.sapb1Cursor.execute(self.sapb1Queries['listEShipmentsSQL'], mOrderIncId)
            b1Shipments = self.sapb1Cursor.fetchall()
            for biShipment in b1Shipments:
                eShipmentIncId, eOrderIncId, shipDt, trackNo, packTrackNo, qty, itemCode, carrier, orderItemId = biShipment
                if trackNo is None:
                    if packTrackNo is None:
                        trackNo = '(no tracking number)'
                    else:
                        trackNo = packTrackNo
                eShipmentIncId = str(eShipmentIncId)
                if qty is None or qty <= 0:
                    continue
                if eShipmentIncId not in eShips and eShipmentIncId not in existingShipments:
                    eShips[eShipmentIncId] = {'m_order_inc_id': mOrderIncId, 'e_shipment_inc_id': eShipmentIncId, 
                       'ship_dt': shipDt, 
                       'tracking': trackNo, 
                       'carrier': carrier, 
                       'items': [
                               {'sku': itemCode, 
                                  'qty': qty, 
                                  'order_item_id': orderItemId}]}
                elif eShipmentIncId in eShips:
                    eShips[eShipmentIncId]['items'].append({'sku': itemCode, 
                       'qty': qty, 
                       'order_item_id': orderItemId})

        return eShips.values()

    def b1eProductsInventoryFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        listEProductInventorySQL = "\n            SELECT V33_Magento_InvAvail.ItemCode, V33_Magento_InvAvail.ItemName, V33_Magento_InvAvail.AvailStock AS qty\n            FROM V33_Magento_InvAvail\n            INNER JOIN OITM ON OITM.ItemCode = V33_Magento_InvAvail.ItemCode\n            INNER JOIN OITW ON OITW.ItemCode = V33_Magento_InvAvail.ItemCode\n            WHERE\n                OITM.SellItem = 'Y'\n            AND OITW.ItemCode IN (\n                    SELECT DISTINCT ItemCode FROM OINM\n                    WHERE OINM.createDate >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n                )\n            AND OITM.U_V33_PRODUCT_TYPE = 'Simple'\n        "
        params = [lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(listEProductInventorySQL, params)
        eProductsInventory = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsInventory

    def b1mProductExtFunct(self, mProduct, eProduct):
        sql = "\n            SELECT OITM.ItemCode, ITM2.VendorCode, OCRD.CardName\n            FROM OITM\n            LEFT JOIN ITM2 ON OITM.ItemCode = ITM2.ItemCode\n            LEFT JOIN OCRD ON ITM2.VendorCode = OCRD.CardCode\n            WHERE OITM.SellItem = 'Y' AND OITM.ItemCode = %s AND\n            CASE WHEN OITM.updateDate IS NULL THEN OITM.createDate ELSE OITM.updateDate END\n            >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n        "
        formattedProductJsonObj = json.loads(mProduct['raw_data'])
        if 'Manufacturer' in formattedProductJsonObj and formattedProductJsonObj['Manufacturer'] is not None and len(formattedProductJsonObj['Manufacturer'].strip()) > 0:
            pass
        else:
            param = (
             mProduct['sku'],
             self.dstControl.getTaskLastCutoffDate('productmaster_erp_to_dst'))
            self.sapb1Cursor.execute(sql, param)
            manufacturers = self.fetchCursorResultAsDict(self.sapb1Cursor)
            if len(manufacturers) > 0:
                formattedProductJsonObj['Manufacturer'] = manufacturers[0]['CardName']
                mProduct['raw_data'] = json.dumps(formattedProductJsonObj)
        return

    def b1mCustomerExtFunct(self, customer, eCustomer):
        nameSplited = eCustomer['Name'].split(' ')
        firstName = nameSplited[0]
        lastName = nameSplited[0]
        if len(nameSplited) >= 2:
            lastName = nameSplited[1]
        if eCustomer['FirstName'] is None:
            eCustomer['FirstName'] = firstName
        if eCustomer['LastName'] is None:
            eCustomer['LastName'] = lastName
        return

    def insertMCustomer(self, eCustomer):
        e_cust_inc_id = eCustomer['CardCode']
        customer = self.getMCustomer(eCustomer)
        customer['e_json_data'] = json.dumps(customer)
        for key, value in customer.items():
            if key not in ('id', 'email', 'website_code', 'e_json_data'):
                del customer[key]

        customer['sync_status'] = 'N'
        customer['sync_dt'] = datetime.now()
        customer['sync_notes'] = 'Sync to DST'
        customer['e_cust_inc_id'] = e_cust_inc_id
        updateColumns = {'e_json_data': customer['e_json_data'], 
           'sync_status': 'N', 
           'sync_dt': datetime.now(), 
           'sync_notes': 'Sync to DST', 
           'e_cust_inc_id': customer['e_cust_inc_id']}
        sql, values = self.getInsertOnDupldateUpdateSqlnValues('e_customer', customer, updateColumns)
        self.dstCursor.execute(sql, values)
        eCustomerId = self.dstCursor.lastrowid
        customer['id'] = eCustomerId
        return customer

    def getDocEntry(self, id, docType):
        sqls = {}
        sqls['oOrders'] = "SELECT DocEntry FROM dbo.ORDR WHERE U_MageOrderIncId = '%s'" % id
        sqls['oInvoices'] = "SELECT DISTINCT t0.DocEntry\n                                FROM dbo.OINV t0, dbo.INV1 t1\n                                WHERE t0.DocEntry = t1.DocEntry\n                                AND t1.BaseType = '%s'\n                                AND t1.BaseEntry = '%s'" % (self.constants.oDeliveryNotes, id)
        sqls['oBusinessPartners'] = "SELECT distinct CardCode FROM OCRD WHERE CardFName = '%s'" % id
        sqls['oDownPayments'] = "SELECT DISTINCT t0.DocEntry\n                                    FROM dbo.ODPI t0, dbo.DPI1 t1\n                                    WHERE t0.DocEntry = t1.DocEntry\n                                    AND t1.BaseType = '%s'\n                                    AND t1.BaseEntry = '%s'" % (self.constants.oOrders, id)
        sqls['dptInvoice'] = "SELECT DocEntry FROM dbo.ODPI WHERE DpmAmnt != DpmAppl AND U_MageOrderIncId = '%s'" % id
        sqls['oBusinessPartnersByEmail'] = "\n            SELECT DISTINCT OCRD.CardCode\n            FROM  OCRD\n            INNER JOIN OCPR ON OCRD.CardCode = OCPR.CardCode\n            WHERE OCRD.CardType = 'C'\n            AND ( OCRD.E_Mail = '%s' OR OCPR.E_MailL = '%s' )\n        " % (id, id)
        sqls['oBusinessPartnersNameByEmail'] = "\n            SELECT DISTINCT OCRD.CardName\n            FROM  OCRD\n            INNER JOIN OCPR ON OCRD.CardCode = OCPR.CardCode\n            WHERE OCRD.CardType = 'C'\n            AND ( OCRD.E_Mail = '%s' OR OCPR.E_MailL = '%s' )\n        " % (id, id)
        sqls['oBusinessPartnersByCode'] = "SELECT distinct CardCode FROM OCRD WHERE CardCode = '%s'" % id
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = sqls[docType]
        rs.DoQuery(sql)
        docNum = rs.Fields.Item(0).Value
        return docNum

    def syncCustomerToDST(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'customer_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eCustomer in self.getECustomers(task):
                if eCustomer['email'] is None:
                    if eCustomer['bp_email'] is None:
                        self.logger.warning(('No e-mail for "{}" - "{}".').format(eCustomer['CardName'], eCustomer['Name']))
                        continue
                    else:
                        eCustomer['email'] = eCustomer['bp_email']
                mCustomer = self.insertMCustomer(eCustomer)
                log = ('id/email/:{0}/{1}').format(mCustomer['id'], mCustomer['email'])
                self.logger.info(log)
                if mCustomer['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mCustomer['id']

            self.dstDb.commit()
            if lastCutoffEntityId is not None:
                syncStatus = 'O'
                syncNotes = 'Sync from ERP to DST'
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()
            syncStatus = 'F'
            syncNotes = e

        lastCutoffDt = start
        lastStartDt = start
        lastEndDt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
        self.dstDb.commit()
        return

    def b1eCustomerAddresses(self, eCustomer):
        cardCode = eCustomer['CardCode']
        self.sapb1Cursor.execute(self.sapb1Queries['listECustomerAddressSQL'], cardCode)
        eAddresses = self.fetchCursorResultAsDict(self.sapb1Cursor)
        self.sapb1Cursor.execute(self.sapb1Queries['getECustomerTelphoneSQL'], (cardCode, eCustomer['Name']))
        result = self.sapb1Cursor.fetchone()
        if len(result) > 0:
            telephone = result[0]
        for address in eAddresses:
            address['telephone'] = telephone

        return eAddresses

    def getEOrder(self, mOrder):
        f = lambda mOrder: eval(self.functs.eOrderFunct)
        order = f(mOrder)
        f = lambda order, mOrder: eval(self.functs.eOrderExtFunct)
        f(order, mOrder)
        i = 0
        for item in mOrder['items']:
            f = lambda i, order, item, mOrder: eval(self.functs.eOrderLineFunct)
            f(i, order, item, mOrder)
            f = lambda i, order, item, mOrder: eval(self.functs.eOrderLineExtFunct)
            f(i, order, item, mOrder)
            i = i + 1
            if 'cut_fee' in item and decimal.Decimal(item['cut_fee']) > 0:
                order.Lines.Add()
                order.Lines.SetCurrentLine(i)
                order.Lines.ItemCode = self._customCutFeeSku
                order.Lines.Quantity = 1
                order.Lines.Price = decimal.Decimal(item['cut_fee'])
                order.Lines.TaxCode = self._taxMetrics['Exempt']
                order.Lines.LineTotal = order.Lines.Price * order.Lines.Quantity
                order.Lines.UserFields.Fields.Item('U_V33_CUST_WIDTH').Value = str(item['custom_cut_width'])
                order.Lines.UserFields.Fields.Item('U_V33_CUST_LENGTH').Value = str(item['custom_cut_length'])
                order.Lines.UserFields.Fields.Item('U_V33_TOTAL_CUT').Value = str(item['custom_cut_total_cut'])
                order.Lines.UserFields.Fields.Item('U_MageOrderLineId').Value = '-998'
                i = i + 1

        return order

    def syncProductMaster(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productmaster_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            mProductSku = []
            for eProduct in self.getEProducts(task):
                mProduct = self.insertMProduct(eProduct)
                mProductSku.append(mProduct['sku'])
                log = ('id/sku/e_product_id:{0}/{1}/{2}').format(mProduct['id'], mProduct['sku'], mProduct['e_product_id'])
                self.logger.info(log)
                if mProduct['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProduct['id']

            self.dstDb.commit()
            for sku in mProductSku:
                self.sapb1Cursor.execute(self.sapb1Queries['updateEProductUpdateToSyncSQL'], ('N', sku))

            self.sapb1Conn.commit()
            if lastCutoffEntityId is not None:
                syncStatus = 'O'
                syncNotes = 'Sync from ERP to DST'
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()
            syncStatus = 'F'
            syncNotes = e

        lastCutoffDt = start
        lastStartDt = start
        lastEndDt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
        self.dstDb.commit()
        return

    def b1eOrderFunct(self, mOrder):
        mOrder['billto_telephone'] = self.trimValue(mOrder['billto_telephone'], 20)
        if mOrder['billto_companyname'] is not None and len(mOrder['billto_companyname'].strip()) > 0:
            mOrder['billto_address'] = mOrder['billto_companyname'] + ', ' + mOrder['billto_address']
        if mOrder['shipto_companyname'] is not None and len(mOrder['shipto_companyname'].strip()) > 0:
            mOrder['shipto_address'] = mOrder['shipto_companyname'] + ', ' + mOrder['shipto_address']
        mOrder['billto_address'] = self.trimValue(mOrder['billto_address'], 100)
        mOrder['shipto_address'] = self.trimValue(mOrder['shipto_address'], 100)
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.DocDueDate = datetime.now() + timedelta(days=self._docDuteDate)
        order.CardCode = self.getCardCodeByECustomerId(mOrder[self._cardCodeColumn], mOrder)
        mOrder[self._cardCodeColumn] = order.CardCode
        name = self.getCardNameByEmail(mOrder['billto_email'])
        name = str(name[0:50])
        order.CardName = name
        order.DocCurrency = self.getDfCurrency()
        order.ContactPersonCode = self.getContactPersonCode(mOrder)
        if self._expenseFreightName is not None:
            order.Expenses.ExpenseCode = self.getExpnsCode(self._expenseFreightName)
            order.Expenses.LineTotal = mOrder['shipping_amt']
            taxCode = self.getTaxCode(float(mOrder['shipping_amt']), float(mOrder['shipping_tax_amt']), mOrder[self._taxPostcodeColumn], mOrder[self._taxCountryColumn])
            order.Expenses.TaxCode = taxCode
        if mOrder['discount_amt'] != 0:
            order.DiscountPercent = abs(mOrder['discount_amt']) / mOrder['sub_total'] * 100
        transportationCode = self.getTransportationCode(mOrder['shipment_method'])
        if transportationCode is not None:
            order.TransportationCode = transportationCode
        paymentMethodCode = self.getPaymentMethod(mOrder['payment_method'])
        if paymentMethodCode is not None:
            order.PaymentMethod = paymentMethodCode
        order.UserFields.Fields.Item('U_MageOrderIncId').Value = str(mOrder['m_order_inc_id'])
        order.AddressExtension.BillToCity = mOrder['billto_city']
        order.AddressExtension.BillToCountry = mOrder['billto_country']
        if mOrder['billto_country'] in self._mOrderCountries:
            order.AddressExtension.BillToState = mOrder['billto_region']
        order.AddressExtension.BillToStreet = mOrder['billto_address']
        order.AddressExtension.BillToZipCode = mOrder['billto_postcode']
        order.AddressExtension.ShipToCity = mOrder['shipto_city']
        order.AddressExtension.ShipToCountry = mOrder['shipto_country']
        if mOrder['shipto_country'] in self._mOrderCountries:
            order.AddressExtension.ShipToState = mOrder['shipto_region']
        order.AddressExtension.ShipToStreet = mOrder['shipto_address']
        order.AddressExtension.ShipToZipCode = mOrder['shipto_postcode']
        return order

    def addUpdateB1ECustFunct(self, customer, exist):
        if exist == 0:
            lRetCode = customer.Add()
        else:
            lRetCode = 0
        if lRetCode != 0:
            log = self.company.GetLastErrorDescription()
            self.logger.error(log)
            raise Exception(log)
        else:
            eCustIncId = self.getDocEntry(customer.CardForeignName, 'oBusinessPartners')
            return eCustIncId

    def insertCntctCode(self, mOrder):
        busPartner = self.company.GetBusinessObject(self.constants.oBusinessPartners)
        busPartner.GetByKey(mOrder[self._cardCodeColumn])
        current = busPartner.ContactEmployees.Count
        if busPartner.ContactEmployees.InternalCode == 0:
            nextLine = 0
        else:
            nextLine = current
        busPartner.PriceListNum = '8'
        busPartner.PayTermsGrpCode = 4
        busPartner.ContactEmployees.Add()
        busPartner.ContactEmployees.SetCurrentLine(nextLine)
        name = mOrder['billto_firstname'] + ' ' + mOrder['billto_lastname']
        name = name[0:36] + ' ' + str(time())
        busPartner.ContactEmployees.Name = name
        busPartner.ContactEmployees.FirstName = mOrder['billto_firstname']
        busPartner.ContactEmployees.LastName = mOrder['billto_lastname']
        busPartner.ContactEmployees.Phone1 = mOrder['billto_telephone']
        busPartner.ContactEmployees.E_Mail = mOrder['billto_email']
        address = mOrder['billto_address'] + ', ' + mOrder['billto_city'] + ', ' + mOrder['billto_region'] + ' ' + mOrder['billto_postcode'] + ', ' + mOrder['billto_country']
        busPartner.ContactEmployees.Address = self.trimValue(address, 100)
        lRetCode = busPartner.Update()
        if lRetCode != 0:
            log = self.company.GetLastErrorDescription()
            self.logger.error(log)
            raise Exception(log)
        return self.getCntctCode(mOrder[self._cardCodeColumn], mOrder)
# okay decompiling SAPB1SyncAgent.pyc
