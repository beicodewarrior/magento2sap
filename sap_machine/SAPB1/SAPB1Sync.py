# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\SAPB1\SAPB1Sync.py
# Compiled at: 2016-06-18 20:45:10
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
from datetime import datetime, timedelta
from time import time
import traceback, MySQLdb, decimal, pymssql, json
from utility.utility import DecimalEncoder

class SAPB1Sync(object):

    def __init__(self, sapb1di_conf, dst_conf, connect_di=True):
        self.logger = Logger('SAPB1Sync', sapb1di_conf['logfilename'])
        if connect_di:
            SAPbobsCOM = __import__(sapb1di_conf['diapi'])
            self.constants = getattr(SAPbobsCOM, 'constants')
            Company = getattr(SAPbobsCOM, 'Company')
            self.company = Company()
            self.company.Server = sapb1di_conf['server']
            self.company.UseTrusted = False
            self.company.language = eval('self.constants.' + sapb1di_conf['language'])
            self.company.DbServerType = eval('self.constants.' + sapb1di_conf['dbservertype'])
            self.company.DbUserName = sapb1di_conf['dbusername']
            self.company.DbPassword = sapb1di_conf['dbpassword']
            self.company.CompanyDB = sapb1di_conf['companydb']
            self.company.UserName = sapb1di_conf['username']
            self.company.Password = sapb1di_conf['password']
            self.company.Connect()
            self.companyName = self.company.CompanyName
            log = 'Open SAPB1 connection for ' + self.companyName
            self.logger.info(log)
        else:
            self.company = None
        HOST = dst_conf['host']
        USER = dst_conf['user']
        PWD = dst_conf['password']
        DB = dst_conf['db']
        self.dstDb = MySQLdb.connect(HOST, USER, PWD, DB)
        log = 'Open dst database connection'
        self.logger.info(log)
        self.dstCursor = self.dstDb.cursor(MySQLdb.cursors.DictCursor)
        self._taxMetrics = {}
        self._shipmentMethods = {}
        self._docDuteDate = 1
        self._mOrderStatus = ['pending', 'processing']
        self._mOrderCountries = ['US', 'CA']
        self.sapb1Conn = pymssql.connect(sapb1di_conf['server'], sapb1di_conf['dbusername'], sapb1di_conf['dbpassword'], sapb1di_conf['companydb'])
        self.sapb1Cursor = self.sapb1Conn.cursor()
        log = 'Open SAPB1 DB connection'
        self.logger.info(log)
        self.sapb1di_conf = sapb1di_conf
        self.dst_conf = dst_conf
        return

    def __del__(self):
        if self.company:
            self.company.Disconnect()
        self.dstDb.close()
        self.sapb1Conn.close()

    @property
    def taxMetrics(self):
        return self._taxMetrics

    @taxMetrics.setter
    def taxMetrics(self, value):
        self._taxMetrics = value

    @property
    def shipmentMethods(self):
        return self._shipmentMethods

    @shipmentMethods.setter
    def shipmentMethods(self, value):
        self._shipmentMethods = value

    @property
    def docDuteDate(self):
        return self._docDuteDate

    @docDuteDate.setter
    def docDuteDate(self, value):
        self._docDuteDate = value

    @property
    def mOrderStatus(self):
        return self._mOrderStatus

    @mOrderStatus.setter
    def mOrderStatus(self, value):
        self._mOrderStatus = value

    def getDocEntry(self, id, docType):
        sqls = {}
        sqls['oOrders'] = "SELECT MAX(DocEntry) FROM dbo.ORDR WHERE U_MageOrderIncId = '%s'" % id
        sqls['oInvoices'] = "SELECT DISTINCT t0.DocEntry\n                                FROM dbo.OINV t0, dbo.INV1 t1\n                                WHERE t0.DocEntry = t1.DocEntry\n                                AND t1.BaseType = '%s'\n                                AND t1.BaseEntry = '%s'" % (self.constants.oDeliveryNotes, id)
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = sqls[docType]
        rs.DoQuery(sql)
        docNum = rs.Fields.Item(0).Value
        return docNum

    def getCntctCode(self, cardCode, mOrder):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        address = mOrder['billto_address'] + ', ' + mOrder['billto_city'] + ', ' + mOrder['billto_region'] + ' ' + mOrder['billto_postcode'] + ', ' + mOrder['billto_country']
        param = {'FirstName': mOrder['billto_firstname'], 
           'LastName': mOrder['billto_lastname'], 
           'E_MailL': mOrder['billto_email'], 
           'Address': self.trimValue(address, 100)}
        sql = "SELECT cntctcode FROM dbo.OCPR WHERE cardcode = '%s' " % cardCode
        for k, v in param.items():
            if v is not None:
                v = v.replace("'", "''")
                sql = sql + "AND %s = '%s' " % (k, v)
            else:
                sql = sql + 'AND %s is null ' % k

        rs.DoQuery(sql)
        cntctCode = rs.Fields.Item(0).Value
        return cntctCode

    def getExpnsCode(self, expnsName):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = "SELECT ExpnsCode FROM dbo.OEXD WHERE ExpnsName = '%s'" % expnsName
        rs.DoQuery(sql)
        expnsCode = rs.Fields.Item(0).Value
        return expnsCode

    def getTrnspCode(self, trnspName):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = "SELECT TrnspCode FROM dbo.OSHP WHERE TrnspName = '%s'" % trnspName
        rs.DoQuery(sql)
        trnspCode = rs.Fields.Item(0).Value
        return trnspCode

    def getTransportationCode(self, shipmentMethod):
        trnspName = None
        if shipmentMethod in self._shipmentMethods.keys():
            trnspName = self._shipmentMethods[shipmentMethod]
        else:
            for k, v in self._shipmentMethods.items():
                if shipmentMethod.find(k) != -1:
                    trnspName = v
                    break

        if trnspName is not None:
            return self.getTrnspCode(trnspName)
        else:
            return
            return

    def insertCntctCode(self, mOrder):
        busPartner = self.company.GetBusinessObject(self.constants.oBusinessPartners)
        busPartner.GetByKey(mOrder['sapb1_card_code'])
        current = busPartner.ContactEmployees.Count
        busPartner.ContactEmployees.Add()
        busPartner.ContactEmployees.SetCurrentLine(current)
        name = mOrder['billto_firstname'] + ' ' + mOrder['billto_lastname'] + ' ' + str(time())
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
        return self.getCntctCode(mOrder['sapb1_card_code'], mOrder)

    def getContactPersonCode(self, mOrder):
        contactPersonCode = self.getCntctCode(mOrder['sapb1_card_code'], mOrder)
        if contactPersonCode == 0:
            try:
                contactPersonCode = self.insertCntctCode(mOrder)
            except Exception as e:
                log = str(e)
                self.logger.error(log)
                raise

        return contactPersonCode

    def getDfCurrency(self):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = 'SELECT MainCurncy FROM dbo.OADM'
        rs.DoQuery(sql)
        dfcurrency = rs.Fields.Item(0).Value
        rs.MoveNext()
        return dfcurrency

    def getTaxCode(self, lineTotal, taxAmt):
        taxCode = self._taxMetrics['Exempt']
        for k, v in self._taxMetrics['code_rate'].items():
            if abs(round(lineTotal * v / 100 - taxAmt)) == 0 and taxAmt != 0:
                taxCode = k
                break

        return taxCode

    def trimValue(self, value, maxLength):
        if len(value) > maxLength:
            return value[0:maxLength - 1]
        return value

    def getEOrder(self, mOrder):
        mOrder['billto_telephone'] = self.trimValue(mOrder['billto_telephone'], 20)
        mOrder['billto_address'] = self.trimValue(mOrder['billto_address'], 100)
        mOrder['shipto_address'] = self.trimValue(mOrder['shipto_address'], 100)
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.DocDueDate = datetime.now() + timedelta(days=self._docDuteDate)
        order.CardCode = mOrder['sapb1_card_code']
        order.CardName = mOrder['billto_firstname'] + ' ' + mOrder['billto_lastname']
        order.DocCurrency = self.getDfCurrency()
        order.ContactPersonCode = self.getContactPersonCode(mOrder)
        order.Expenses.ExpenseCode = self.getExpnsCode('Freight')
        order.Expenses.LineTotal = mOrder['shipping_amt']
        taxCode = self.getTaxCode(float(mOrder['shipping_amt']), float(mOrder['shipping_tax_amt']))
        order.Expenses.TaxCode = taxCode
        if mOrder['discount_amt'] != 0:
            order.DiscountPercent = abs(mOrder['discount_amt']) / mOrder['sub_total'] * 100
        transportationCode = self.getTransportationCode(mOrder['shipment_method'])
        if transportationCode is not None:
            order.TransportationCode = transportationCode
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
        self.getEOrderExt(order, mOrder)
        i = 0
        for item in mOrder['items']:
            self.getEOrderLines(i, order, item, mOrder)
            i = i + 1

        return order

    def getEOrderExt(self, order, mOrder):
        pass

    def getEOrderLines(self, i, order, item, mOrder):
        order.Lines.Add()
        order.Lines.SetCurrentLine(i)
        order.Lines.ItemCode = item['sku']
        order.Lines.Quantity = int(item['qty'])
        order.Lines.Price = decimal.Decimal(item['price'])
        lineTotal = order.Lines.Price * order.Lines.Quantity
        taxCode = self.getTaxCode(lineTotal, float(item['tax_amt']))
        order.Lines.TaxCode = taxCode
        order.Lines.LineTotal = lineTotal
        self.getEOrderLinesExt(order, item, mOrder)

    def getEOrderLinesExt(self, order, item, mOrder):
        pass

    def addB1OrderFunct(self, order):
        mOrderIncId = order.UserFields.Fields.Item('U_MageOrderIncId').Value
        lRetCode = order.Add()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)
        else:
            eOrderIncId = self.getDocEntry(mOrderIncId, 'oOrders')
            return eOrderIncId

    def cancelB1OrderFunct(self, mOrder):
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.GetByKey(mOrder['e_order_inc_id'])
        lRetCode = order.Cancel()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)

    def insertEOrder(self, mOrder):
        eOrder = {}
        eOrder['m_order_inc_id'] = mOrder['m_order_inc_id']
        eOrder['e_order_inc_id'] = self.getDocEntry(str(mOrder['m_order_inc_id']), 'oOrders')
        eOrder['sync_status'] = 'F'
        eOrder['sync_notes'] = 'DST to SAPB1'
        if eOrder['e_order_inc_id'] == 0:
            try:
                order = self.getEOrder(mOrder)
                eOrderIncId = self.addB1OrderFunct(order)
                eOrder['sync_status'] = 'O'
                eOrder['e_order_inc_id'] = eOrderIncId
            except Exception as e:
                log = traceback.format_exc()
                eOrder['sync_notes'] = log
                self.logger.exception(e)

        else:
            eOrder['sync_status'] = 'O'
        return eOrder

    def cancelEOrder(self, mOrder):
        eOrder = {}
        eOrder['m_order_inc_id'] = mOrder['m_order_inc_id']
        eOrder['e_order_inc_id'] = mOrder['e_order_inc_id']
        eOrder['sync_status'] = 'F'
        eOrder['sync_notes'] = 'DST to SAPB1'
        try:
            self.cancelB1OrderFunct(mOrder)
            eOrder['sync_status'] = 'X'
        except Exception as e:
            log = traceback.format_exc()
            eOrder['sync_notes'] = log
            self.logger.exception(e)

        return eOrder

    def getEInvoice(self, eShipment):
        delivery = self.company.GetBusinessObject(self.constants.oDeliveryNotes)
        delivery.GetByKey(eShipment['e_shipment_inc_id'])
        invoice = self.company.GetBusinessObject(self.constants.oInvoices)
        invoice.CardName = delivery.CardName
        invoice.UserFields.Fields.Item('U_MageInvoiceIncId').Value = str(eShipment['m_invoice_inc_id'])
        for i in range(0, delivery.Expenses.Count):
            delivery.Expenses.SetCurrentLine(i)
            if delivery.Expenses.LineTotal > 0:
                invoice.Expenses.Add()
                invoice.Expenses.SetCurrentLine(i)
                invoice.Expenses.BaseDocType = self.constants.oDeliveryNotes
                invoice.Expenses.BaseDocLine = delivery.Expenses.LineNum
                invoice.Expenses.BaseDocEntry = delivery.DocEntry

        self.getEInvoiceExt(invoice, delivery)
        for i in range(0, delivery.Lines.Count):
            self.getEInvoiceLines(i, invoice, delivery)

        return invoice

    def getEInvoiceExt(self, invoice, delivery):
        pass

    def getEInvoiceLines(self, i, invoice, delivery):
        delivery.Lines.SetCurrentLine(i)
        invoice.Lines.Add()
        invoice.Lines.SetCurrentLine(i)
        invoice.Lines.ItemCode = delivery.Lines.ItemCode
        invoice.Lines.Quantity = delivery.Lines.Quantity
        invoice.Lines.BaseEntry = delivery.DocEntry
        invoice.Lines.BaseLine = delivery.Lines.LineNum
        invoice.Lines.BaseType = self.constants.oDeliveryNotes
        self.getEInvoiceLinesExt(i, invoice, delivery)

    def getEInvoiceLinesExt(self, i, invoice, delivery):
        pass

    def insertEInvoice(self, eShipment):
        eInvoice = {}
        eInvoice['m_order_inc_id'] = eShipment['m_order_inc_id']
        eInvoice['m_invoice_inc_id'] = eShipment['m_invoice_inc_id']
        eInvoice['e_shipment_inc_id'] = eShipment['e_shipment_inc_id']
        eInvoice['e_invoice_inc_id'] = self.getDocEntry(eShipment['e_shipment_inc_id'], 'oInvoices')
        eInvoice['sync_status'] = 'F'
        eInvoice['sync_notes'] = 'DST to SAPB1'
        if eInvoice['e_invoice_inc_id'] == 0:
            try:
                invoice = self.getEInvoice(eShipment)
                lRetCode = invoice.Add()
                if lRetCode != 0:
                    eInvoice['sync_notes'] = str(self.company.GetLastError())
                    self.logger.error(self.company.GetLastError())
                else:
                    eInvoice['sync_status'] = 'O'
                    eInvoice['e_invoice_inc_id'] = self.getDocEntry(eShipment['e_shipment_inc_id'], 'oInvoices')
                return eInvoice
            except Exception as e:
                log = str(e)
                eInvoice['sync_notes'] = log
                self.logger.error(log)
                return eInvoice

        else:
            eInvoice['sync_status'] = 'O'
            return eInvoice

    def getMOrders(self):
        the_sql = "SELECT * FROM m_order WHERE sync_status ='N' and m_order_status in (%s);"
        format_strings = (',').join(['%s'] * len(self._mOrderStatus))
        the_sql = the_sql % format_strings
        self.dstCursor.execute(the_sql, tuple(self._mOrderStatus))
        mOrders = self.dstCursor.fetchall()
        for mOrder in mOrders:
            the_sql = "SELECT sku, qty, price, tax_amt FROM m_order_item WHERE m_order_id = '%s';" % mOrder['id']
            self.dstCursor.execute(the_sql)
            mOrderItems = self.dstCursor.fetchall()
            mOrderItems = list(mOrderItems)
            for mOrderItem in mOrderItems:
                mOrderItem['qty'] = str(mOrderItem['qty'])
                mOrderItem['price'] = str(mOrderItem['price'])
                mOrderItem['tax_amt'] = str(mOrderItem['tax_amt'])

            mOrder['items'] = mOrderItems

        return mOrders

    def getMCancelOrders(self):
        the_sql = "SELECT * FROM m_order\n                    WHERE sync_status ='O'\n                    and m_order_status = 'canceled'\n                    and e_order_inc_id is not null;"
        self.dstCursor.execute(the_sql)
        mOrders = self.dstCursor.fetchall()
        return mOrders

    def getEShipments(self):
        the_sql = "SELECT m_order_inc_id, m_invoice_inc_id, e_shipment_inc_id\n                    FROM e_shipment\n                    WHERE sync_status = 'O'\n                    AND e_shipment_inc_id not in (\n                        SELECT e_shipment_inc_id\n                        FROM e_invoice\n                        WHERE sync_status = 'O');"
        self.dstCursor.execute(the_sql)
        eShipments = self.dstCursor.fetchall()
        eShipments = list(eShipments)
        return eShipments

    def updateMOrder(self, eOrder):
        the_sql = 'UPDATE m_order\n                    SET e_order_inc_id = %s, sync_status = %s, sync_notes = %s, sync_dt = NOW()\n                    WHERE m_order_inc_id = %s;'
        self.dstCursor.execute(the_sql, [eOrder['e_order_inc_id'], eOrder['sync_status'], eOrder['sync_notes'],
         eOrder['m_order_inc_id']])

    def updateEInvoice(self, eInvoice):
        the_sql = 'REPLACE INTO e_invoice VALUES(%s, %s, %s, %s, %s, %s, NOW());'
        params = [eInvoice['e_shipment_inc_id'], eInvoice['m_order_inc_id'], eInvoice['m_invoice_inc_id'],
         eInvoice['e_invoice_inc_id'], eInvoice['sync_status'], eInvoice['sync_notes']]
        self.dstCursor.execute(the_sql, params)

    def syncOrder(self):
        try:
            for mOrder in self.getMOrders():
                log = 'starting m_order_inc_id: ' + str(mOrder['m_order_inc_id'])
                self.logger.info(log)
                eOrder = self.insertEOrder(mOrder)
                log = 'm_order_inc_id/e_order_inc_id: ' + str(mOrder['m_order_inc_id']) + '/' + str(eOrder['e_order_inc_id']) + ' inserted.'
                self.logger.info(log)
                self.updateMOrder(eOrder)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            log = 'Error %d: %s' % (e.args[0], e.args[1])
            self.logger.error(log)
            self.dstDb.close()

    def syncOrderStatus(self):
        try:
            for mOrder in self.getMCancelOrders():
                eOrder = self.cancelEOrder(mOrder)
                log = 'm_order_inc_id/e_order_inc_id: ' + str(mOrder['m_order_inc_id']) + '/' + str(eOrder['e_order_inc_id']) + ' canceled.'
                self.logger.info(log)
                self.updateMOrder(eOrder)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            log = 'Error %d: %s' % (e.args[0], e.args[1])
            self.logger.error(log)
            self.dstDb.close()

    def syncInvoice(self):
        try:
            for eShipment in self.getEShipments():
                log = 'm_invoice_inc_id: ' + str(eShipment['m_invoice_inc_id'])
                self.logger.info(log)
                eInvoice = self.insertEInvoice(eShipment)
                log = 'e_invoice_inc_id: ' + str(eInvoice['e_invoice_inc_id'])
                self.logger.info(log)
                self.updateEInvoice(eInvoice)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            log = 'Error %d: %s' % (e.args[0], e.args[1])
            self.logger.error(log)
            self.dstDb.close()

    def syncShipmentToDst(self):
        try:
            sql = "\n                select id, e_order_inc_id,m_order_inc_id, total_qty\n                from m_order\n                where m_order_status in ('pending','processing') and sync_status = 'O'\n            "
            self.dstCursor.execute(sql)
            rows = self.dstCursor.fetchall()
            for row in rows:
                print row
                self.getShipmentFromSapb1(row)

            self.dstDb.commit()
        except Exception as e:
            print str(e)
            self.dstDb.rollback()

    def getShipmentFromSapb1(self, order):
        sql = "select\n            t0.DocEntry,\n            t1.BaseEntry,\n            t1.ShipDate,\n            t0.TrackNo,\n            t1.Quantity,\n            t3.ItemCode,\n            ISNULL(t2.TrnspName,'')\n            from\n            ODLN t0 left join DLN1 t1 on (t0.DocEntry = t1.DocEntry)\n            LEFT JOIN OSHP t2 on (t0.TrnspCode = t2.TrnspCode)\n            INNER JOIN OITM t3 on t1.ItemCode = t3.ItemCode\n            where t0.U_MageOrderIncId =%s"
        e_order_inc_id = order['e_order_inc_id']
        m_order_inc_id = order['m_order_inc_id']
        self.sapb1Cursor.execute(sql, m_order_inc_id)
        rows = self.sapb1Cursor.fetchall()
        shipments = self.getExistingShipment(m_order_inc_id)
        shipment_params = []
        lines = []
        dst_shipment_sql = '\n            insert into e_shipment(e_shipment_inc_id,m_order_inc_id,tracking,ship_dt,sync_status,create_dt,sync_dt,sync_notes,carrier)\n            values (%s,%s,%s,%s,%s,now(),now(),%s,%s)\n        '
        shipment_id = ''
        new_shipments = {}
        for row in rows:
            e_shipment_inc_id, e_order_inc_id, ship_dt, track_no, qty, item_code, carrier = row
            e_shipment_inc_id = str(e_shipment_inc_id)
            if qty is None or int(qty) <= 0:
                continue
            if e_shipment_inc_id not in shipments and e_shipment_inc_id not in new_shipments:
                param = [
                 e_shipment_inc_id, m_order_inc_id, track_no, ship_dt, 'N', 'Get from SAP B1', carrier]
                self.dstCursor.execute(dst_shipment_sql, param)
                shipment_id = self.dstCursor.lastrowid
                shipments.append(e_shipment_inc_id)
                new_shipments[e_shipment_inc_id] = shipment_id
                lines.append([shipment_id, item_code, qty])
                print row
            elif e_shipment_inc_id in new_shipments:
                lines.append([new_shipments[e_shipment_inc_id], item_code, qty])
                print row

        dst_shipment_item_sql = '\n            insert into e_shipment_item(e_shipment_id,sku,qty)\n            values (%s,%s,%s)\n        '
        self.dstCursor.executemany(dst_shipment_item_sql, lines)
        return

    def getExistingShipment(self, m_order_inc_id):
        sql = 'select id,e_shipment_inc_id, m_order_inc_id, sync_status\n            from e_shipment\n            where m_order_inc_id = %s\n        '
        self.dstCursor.execute(sql, [m_order_inc_id])
        rows = self.dstCursor.fetchall()
        shipping_doc_entries = []
        for row in rows:
            shipping_doc_entries.append(str(row['e_shipment_inc_id']))

        return shipping_doc_entries

    def syncProductToDst(self):
        try:
            sql = '\n                SELECT t1.ItemCode, t1.ItemName, t1.OnHand-t1.IsCommited,  t2.Price\n                FROM OITM t1,ITM1 t2,OPLN t3\n                WHERE t1.ItemCode = t2.ItemCode and\n                t2.PriceList = t3.ListNum and\n                t3.ListName = %s\n            '
            self.sapb1Cursor.execute(sql, self.sapb1di_conf['export_price_list'])
            rows = self.sapb1Cursor.fetchall()
            products = []
            stock_data = []
            ins_e_product_sql = "\n            insert into e_product (sku,price,qty,sync_status,create_at,sync_notes)\n            values (%s,%s,%s,'N',now(),'Pull from SAPB1')\n            "
            upd_e_product_sql = "\n            update e_product set price = %s, qty = %s, sync_status = 'N', sync_notes = 'Pull from SAPB1'\n            where sku = %s\n            "
            for row in rows:
                sku, name, qty, price = row
                if 'WAREHOUSES' in self.sapb1di_conf:
                    warehouses = self.sapb1di_conf['WAREHOUSES']
                    total_qty = 0
                    for warehouse_code in warehouses:
                        inventory = self.getInventoryByWarehouse(sku, warehouse_code)
                        logging.info('ItemName: %s, Warehouse: %s, Qty: %d' % (sku, warehouse_code, inventory))
                        total_qty = total_qty + inventory

                    qty = total_qty
                exist = self.isProductExist(sku)
                if exist:
                    sql = upd_e_product_sql
                    param = [price, qty, sku]
                else:
                    sql = ins_e_product_sql
                    param = [sku, price, qty]
                print param
                self.dstCursor.execute(sql, param)

            self.dstDb.commit()
        except Exception as e:
            print str(e)
            self.dstDb.rollback()

    def isProductExist(self, sku):
        sql = 'select count(*) as cnt from e_product where sku = %s'
        self.dstCursor.execute(sql, [sku])
        res = self.dstCursor.fetchone()
        if res is not None and int(res['cnt']) > 0:
            return True
        else:
            return False
            return

    def getInventoryByWarehouse(self, item_code, warehouse_code):
        sql = '\n        select OnHand - IsCommited as qty\n        from OITW where ItemCode = %s and WhsCode = %s\n        '
        self.sapb1Cursor.execute(sql, (item_code, warehouse_code))
        row = self.sapb1Cursor.fetchone()
        if row is not None and len(row) > 0:
            return int(row[0])
        else:
            return 0
            return

    def exportProductToFile(self):
        sql = '\n            SELECT t1.ItemCode, t1.ItemName, t1.OnHand,  t2.Price\n            FROM OITM t1,ITM1 t2,OPLN t3\n            WHERE t1.ItemCode = t2.ItemCode and\n            t2.PriceList = t3.ListNum and\n            t3.ListName = %s\n        '
        self.sapb1Cursor.execute(sql, self.sapb1di_conf['export_price_list'])
        rows = self.sapb1Cursor.fetchall()
        products = []
        stock_data = []
        for row in rows:
            sku, name, qty, price = row
            product = {'sku': sku, 
               'type_id': 'simple', 
               'name': name, 
               'description': name, 
               'short_description': name, 
               'weight': '0', 
               'price': str(price)}
            stock = {'sku': sku, 
               'qty': str(qty)}
            products.append(product)
            stock_data.append(stock)

        product_file = 'sapb1_products.json'
        product_json_fp = open(product_file, 'wb')
        json.dump(products, product_json_fp, sort_keys=True, indent=4, separators=(',',
                                                                                   ': '))
        stock_file = 'sapb1_products_stock.json'
        stock_json_fp = open(stock_file, 'wb')
        json.dump(stock_data, stock_json_fp, sort_keys=True, indent=4, separators=(',',
                                                                                   ': '))
        print 'Products saved in %s' % product_file
        print 'Stock saved in %s' % stock_file

    def fetchCursorResultAsDict(self, cursor):
        result = []
        columns = tuple([ d[0].decode('utf8') for d in cursor.description ])
        for row in cursor:
            result.append(dict(zip(columns, row)))

        return result

    def getSyncTaskLastCutOffDate(self, task):
        sql = 'select max(last_cutoff_dt) as last_cutoff_dt from sync_control where task = %s'
        self.dstCursor.execute(sql, [task])
        res = self.dstCursor.fetchone()
        if res is not None and len(res) > 0 and res['last_cutoff_dt'] is not None:
            last_cutoff_dt = str(res['last_cutoff_dt'])
        else:
            last_cutoff_dt = '2000-01-01 00:00:00'
        return last_cutoff_dt

    def generateGetProductSQL(self, productAttributes={}):
        parts = [
         'SELECT']
        select_parts = []
        for alias, columnName in productAttributes.items():
            select_parts.append(('{0} as {1}').format(columnName, alias))

        parts.append((',\n').join(select_parts))
        parts.append('\n            FROM OITM\n            LEFT JOIN ITM1 ON OITM.ItemCode = ITM1.ItemCode\n            LEFT JOIN OPLN ON ITM1.PriceList = OPLN.ListNum\n        ')
        parts.append('\n            WHERE OPLN.ListName = %s AND\n            (OITM.UpdateDate >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n            OR OITM.UpdateDate is null)\n        ')
        sql = ('\n').join(parts)
        return sql

    def syncProductMaster(self, productAttributes={}):
        try:
            start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task = 'product_master_to_dst'
            last_cutoff_dt = self.getSyncTaskLastCutOffDate(task)
            sql = self.generateGetProductSQL(productAttributes)
            print sql
            self.sapb1Cursor.execute(sql, (self.sapb1di_conf['export_price_list'], last_cutoff_dt))
            rows = self.fetchCursorResultAsDict(self.sapb1Cursor)
            products = []
            ins_or_upd_e_product_master_sql = '\n                INSERT INTO e_product_master\n                (sku,e_product_id,raw_data,sync_status,sync_dt,sync_notes)\n                VALUES\n                (%s,%s,%s,%s,NOW(),%s)\n                ON DUPLICATE KEY UPDATE\n                e_product_id = %s,\n                raw_data = %s,\n                sync_status = %s,\n                sync_notes = %s,\n                sync_dt = NOW()\n            '
            e_ids = []
            for row in rows:
                sku = row['sku']
                e_product_id = None
                raw_data = json.dumps(row, cls=DecimalEncoder)
                product = {'sku': sku, 
                   'e_product_id': e_product_id, 
                   'raw_data': raw_data, 
                   'sync_status': 'N', 
                   'sync_notes': 'SAPB1 to DST'}
                param = [
                 product['sku'],
                 product['e_product_id'],
                 product['raw_data'],
                 product['sync_status'],
                 product['sync_notes'],
                 product['e_product_id'],
                 product['raw_data'],
                 product['sync_status'],
                 product['sync_notes']]
                self.dstCursor.execute(ins_or_upd_e_product_master_sql, param)
                e_ids.append(self.dstCursor.lastrowid)

            if e_ids:
                last_cutoff_entity_id = max(e_ids)
                sync_status = 'O'
                last_cutoff_dt = start
                last_start_dt = start
                last_end_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sync_notes = 'Sync from SAPB1 to DST'
                sql = 'insert into sync_control\n                (task,sync_status,last_cutoff_entity_id,last_cutoff_dt,last_start_dt,last_end_dt,sync_notes)\n                values(%s,%s,%s,%s,%s,%s,%s)'
                self.dstCursor.execute(sql, [task, sync_status, last_cutoff_entity_id, last_cutoff_dt, last_start_dt, last_end_dt, sync_notes])
            self.dstDb.commit()
        except Exception as e:
            print traceback.format_exc()
            self.dstDb.rollback()

        return
# okay decompiling SAPB1Sync.pyc
