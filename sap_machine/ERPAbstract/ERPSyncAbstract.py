# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\ERPAbstract\ERPSyncAbstract.py
# Compiled at: 2016-07-26 09:39:58
__author__ = 'bibow'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import MySQLdb, decimal
from TX import Functs
from TX import Queries
import json

class ERPSyncAbstract(object):

    def __init__(self, appName, logFileName, dst_conf, functs, queries):
        self.logger = Logger(appName, logFileName)
        self.appName = appName
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
        self._mOrderStatus = ['pending', 'processing']
        self._needShipOrderStatus = ['pending', 'processing', 'processing_payment_confirmation']
        self._downpaymentMethods = []
        self.functs = Functs(functs)
        self.queries = Queries(queries)

    def __del__(self):
        self.dstDb.close()
        self.logger.info('Close DST database connection')

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
    def mOrderStatus(self):
        return self._mOrderStatus

    @mOrderStatus.setter
    def mOrderStatus(self, value):
        self._mOrderStatus = value

    @property
    def needShipOrderStatus(self):
        return self._needShipOrderStatus

    @needShipOrderStatus.setter
    def needShipOrderStatus(self, value):
        self._needShipOrderStatus = value

    @property
    def downpaymentMethods(self):
        return self._downpaymentMethods

    @downpaymentMethods.setter
    def downpaymentMethods(self, value):
        self._downpaymentMethods = value

    def getReplaceSqlnValues(self, table, columns):
        sql = 'REPLACE INTO ' + table + ' (%s) VALUES (%s);'
        keys = (',').join(columns.keys())
        valString = (',').join(('%s ' * len(columns.keys())).strip().split(' '))
        sql = sql % (keys, valString)
        return (
         sql, columns.values())

    def getInsertSqlnValues(self, table, columns):
        sql = 'INSERT INTO ' + table + ' (%s) VALUES (%s);'
        keys = (',').join(columns.keys())
        valString = (',').join(('%s ' * len(columns.keys())).strip().split(' '))
        sql = sql % (keys, valString)
        return (
         sql, columns.values())

    def getUpdateSqlnValues(self, table, columns, keys):
        cols = []
        for k in columns.keys():
            col = k + ' = %s'
            cols.append(col)

        kys = []
        for k in keys.keys():
            key = k + ' = %s'
            kys.append(key)

        sql = 'UPDATE ' + table + ' SET ' + (',').join(cols) + ' WHERE ' + (',').join(kys) + ';'
        values = columns.values() + keys.values()
        return (
         sql, values)

    def getInsertOnDupldateUpdateSqlnValues(self, table, insertColumns, updateColumns):
        sql = 'INSERT INTO ' + table + ' (%s) VALUES (%s)'
        keys = (',').join(insertColumns.keys())
        valString = (',').join(('%s ' * len(insertColumns.keys())).strip().split(' '))
        sql = sql % (keys, valString)
        cols = []
        for k in updateColumns.keys():
            col = k + ' = %s'
            cols.append(col)

        sql = sql + ' ON DUPLICATE KEY UPDATE ' + (',').join(cols) + ';'
        values = insertColumns.values() + updateColumns.values()
        return (
         sql, values)

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

        return order

    def insertEOrder(self, mOrder):
        f = lambda mOrder: eval(self.functs.eOrderIncIdFunct)
        eOrder = {}
        eOrder['m_order_inc_id'] = mOrder['m_order_inc_id']
        eOrder['e_order_inc_id'] = f(mOrder)
        eOrder['sync_status'] = 'F'
        eOrder['sync_notes'] = 'DST to ' + self.appName
        if eOrder['e_order_inc_id'] is None:
            try:
                order = self.getEOrder(mOrder)
                f = lambda order: eval(self.functs.addEOrderFunct)
                eOrderIncId = f(order)
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
            f = lambda mOrder: eval(self.functs.cancelEOrderFunct)
            f(mOrder)
            eOrder['sync_status'] = 'X'
        except Exception as e:
            log = traceback.format_exc()
            eOrder['sync_notes'] = log
            self.logger.exception(e)

        return eOrder

    def getMOrders(self):
        format_strings = (',').join(['%s'] * len(self.mOrderStatus))
        self.queries.listMOrdersSQL = self.queries.listMOrdersSQL % format_strings
        self.dstCursor.execute(self.queries.listMOrdersSQL, tuple(self.mOrderStatus))
        mOrders = self.dstCursor.fetchall()
        for mOrder in mOrders:
            self.dstCursor.execute(self.queries.listMOrderItemsSQL, [mOrder['id']])
            mOrderItems = self.dstCursor.fetchall()
            mOrderItems = list(mOrderItems)
            for mOrderItem in mOrderItems:
                mOrderItem['qty'] = str(mOrderItem['qty'])
                mOrderItem['price'] = str(mOrderItem['price'])
                mOrderItem['tax_amt'] = str(mOrderItem['tax_amt'])

            mOrder['items'] = mOrderItems

        return mOrders

    def getMCancelOrders(self):
        self.dstCursor.execute(self.queries.listMCancelOrdersSQL)
        mOrders = self.dstCursor.fetchall()
        return mOrders

    def updateMOrder(self, eOrder):
        columns = {'e_order_inc_id': eOrder['e_order_inc_id'], 
           'sync_status': eOrder['sync_status'], 
           'sync_notes': eOrder['sync_notes'], 
           'sync_dt': datetime.now()}
        keys = {'m_order_inc_id': eOrder['m_order_inc_id']}
        sql, values = self.getUpdateSqlnValues('m_order', columns, keys)
        self.dstCursor.execute(sql, values)

    def syncOrder(self):
        try:
            for mOrder in self.getMOrders():
                eOrder = self.insertEOrder(mOrder)
                log = 'm_order_inc_id/e_order_inc_id: ' + str(mOrder['m_order_inc_id']) + '/' + str(eOrder['e_order_inc_id']) + ' inserted.'
                self.logger.info(log)
                self.updateMOrder(eOrder)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
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
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()

    def getEDownPayment(self, mDownPayment):
        f = lambda mDownPayment: eval(self.functs.eOrderRFunct)
        order, orderItemCount = f(mDownPayment)
        f = lambda order, mDownPayment: eval(self.functs.eDownPaymentFunct)
        downPayment = f(order, mDownPayment)
        f = lambda downPayment, order: eval(self.functs.eDownPaymentExtFunct)
        f(downPayment, order)
        for i in range(0, orderItemCount):
            f = lambda i, downPayment, order: eval(self.functs.eDownPaymentLineFunct)
            f(i, downPayment, order)
            f = lambda i, downPayment, order: eval(self.functs.eDownPaymentLineExtFunct)
            f(i, downPayment, order)

        return (downPayment, order)

    def insertEDownPayment(self, mDownPayment):
        f = lambda mDownPayment: eval(self.functs.eDownPaymentIncIdFunct)
        eDownPayment = {}
        eDownPayment['e_order_inc_id'] = mDownPayment['e_order_inc_id']
        eDownPayment['e_downpayment_inc_id'] = f(mDownPayment)
        eDownPayment['sync_status'] = 'F'
        eDownPayment['sync_notes'] = 'DST to ' + self.appName
        eDownPayment['sync_dt'] = datetime.now()
        if eDownPayment['e_downpayment_inc_id'] is None:
            try:
                downPayment, order = self.getEDownPayment(mDownPayment)
                f = lambda downPayment, order: eval(self.functs.addEDownPaymentFunct)
                eDownPaymentIncId = f(downPayment, order)
                eDownPayment['sync_status'] = 'O'
                eDownPayment['e_downpayment_inc_id'] = eDownPaymentIncId
            except Exception as e:
                log = traceback.format_exc()
                eDownPayment['sync_notes'] = log
                self.logger.exception(e)

        else:
            eDownPayment['sync_notes'] = 'O'
        return eDownPayment

    def getMDownPayments(self):
        if len(self.downpaymentMethods) == 0:
            self.downpaymentMethods = [
             '-']
        formatString = (',').join(['%s'] * len(self.downpaymentMethods))
        orderStatusFormatString = (',').join(['%s'] * len(self.mOrderStatus))
        self.queries.listMDownPaymentsSQL = self.queries.listMDownPaymentsSQL.format(paymentMethods=formatString, mOrderStatus=orderStatusFormatString)
        params = self.downpaymentMethods + self.mOrderStatus
        self.dstCursor.execute(self.queries.listMDownPaymentsSQL, params)
        mDownPayments = self.dstCursor.fetchall()
        mDownPayments = list(mDownPayments)
        return mDownPayments

    def updateMDownPayment(self, eDownPayment):
        print eDownPayment
        sql, values = self.getReplaceSqlnValues('e_downpayment', eDownPayment)
        self.dstCursor.execute(sql, values)

    def syncDownPayment(self):
        try:
            for mDownPayment in self.getMDownPayments():
                eDownPayment = self.insertEDownPayment(mDownPayment)
                log = 'e_downpayment_inc_id: ' + str(eDownPayment['e_downpayment_inc_id']) + ' inserted.'
                self.logger.info(log)
                self.updateMDownPayment(eDownPayment)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()

    def getECust(self, mCustomer):
        f = lambda mCustomer: eval(self.functs.eCustFunct)
        customer, exist = f(mCustomer)
        f = lambda customer, mCustomer: eval(self.functs.eCustExtFunct)
        f(customer, mCustomer)
        i = 0
        for address in mCustomer['addresses']:
            f = lambda i, customer, address, mCustomer: eval(self.functs.eCustAddrFunct)
            f(i, customer, address, mCustomer)
            f = lambda i, customer, address, mCustomer: eval(self.functs.eCustAddrExtFunct)
            f(i, customer, address, mCustomer)
            i = i + 1

        i = 0
        if 'contacts' not in mCustomer:
            mCustomer['contacts'] = []
        for contact in mCustomer['contacts']:
            f = lambda i, customer, contact, mCustomer: eval(self.functs.eCustContFunct)
            f(i, customer, contact, mCustomer)
            f = lambda i, customer, contact, mCustomer: eval(self.functs.eCustContExtFunct)
            f(i, customer, contact, mCustomer)
            i = i + 1

        return (customer, exist)

    def insertECustomer(self, mCustomer):
        eCustomer = {}
        eCustomer['m_cust_inc_id'] = mCustomer['m_cust_inc_id']
        eCustomer['e_cust_inc_id'] = mCustomer['e_cust_inc_id']
        eCustomer['sync_status'] = 'F'
        eCustomer['sync_notes'] = 'DST to ' + self.appName
        if eCustomer['e_cust_inc_id'] is None or eCustomer['e_cust_inc_id'] == 0:
            try:
                customer, exist = self.getECust(mCustomer)
                f = lambda customer, exist: eval(self.functs.addUpdateECustFunct)
                eCustIncId = f(customer, exist)
                eCustomer['sync_status'] = 'O'
                eCustomer['e_cust_inc_id'] = eCustIncId
            except Exception as e:
                log = traceback.format_exc()
                eCustomer['sync_notes'] = log
                self.logger.exception(e)

        else:
            eCustomer['sync_status'] = 'O'
        return eCustomer

    def getMCustomers(self):
        self.dstCursor.execute(self.queries.listMCustsSQL)
        mCustomers = self.dstCursor.fetchall()
        formattedMCustomers = []
        for mCustomer in mCustomers:
            mageJsonData = json.loads(mCustomer['m_json_data'])
            for k, v in mCustomer.items():
                if k != 'm_json_data':
                    mageJsonData[k] = v

            formattedMCustomers.append(mageJsonData)

        return formattedMCustomers

    def updateMCustomer(self, eCustomer):
        columns = {'e_cust_inc_id': eCustomer['e_cust_inc_id'], 
           'sync_status': eCustomer['sync_status'], 
           'sync_notes': eCustomer['sync_notes'], 
           'sync_dt': datetime.now()}
        keys = {'m_cust_inc_id': eCustomer['m_cust_inc_id']}
        sql, values = self.getUpdateSqlnValues('m_customer', columns, keys)
        self.dstCursor.execute(sql, values)

    def syncCustomer(self):
        try:
            for mCustomer in self.getMCustomers():
                eCustomer = self.insertECustomer(mCustomer)
                log = 'm_cust_inc_id/e_cust_inc_id: ' + str(eCustomer['m_cust_inc_id']) + '/' + str(eCustomer['e_cust_inc_id']) + ' inserted.'
                self.logger.info(log)
                self.updateMCustomer(eCustomer)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()

    def getEInvoice(self, mInvoice):
        f = lambda mInvoice: eval(self.functs.eShipRFunct)
        shipment, shipItemCount = f(mInvoice)
        f = lambda shipment, mInvoice: eval(self.functs.eInvoiceFunct)
        invoice = f(shipment, mInvoice)
        f = lambda invoice, shipment: eval(self.functs.eInvoiceExtFunct)
        f(invoice, shipment)
        for i in range(0, shipItemCount):
            f = lambda i, invoice, shipment: eval(self.functs.eInvoiceLineFunct)
            f(i, invoice, shipment)
            f = lambda i, invoice, shipment: eval(self.functs.eInvoiceLineExtFunct)
            f(i, invoice, shipment)

        return (invoice, shipment)

    def insertEInvoice(self, mInvoice):
        f = lambda mInvoice: eval(self.functs.eInvoiceIncIdFunct)
        eInvoice = {}
        eInvoice['m_order_inc_id'] = mInvoice['m_order_inc_id']
        eInvoice['m_invoice_inc_id'] = mInvoice['m_invoice_inc_id']
        eInvoice['e_shipment_inc_id'] = mInvoice['e_shipment_inc_id']
        eInvoice['e_invoice_inc_id'] = f(mInvoice)
        eInvoice['sync_status'] = 'F'
        eInvoice['sync_notes'] = 'DST to ' + self.appName
        eInvoice['sync_dt'] = datetime.now()
        if eInvoice['e_invoice_inc_id'] is None:
            try:
                invoice, shipment = self.getEInvoice(mInvoice)
                f = lambda invoice, shipment: eval(self.functs.addEInvoiceFunct)
                eInvoiceIncId = f(invoice, shipment)
                eInvoice['sync_status'] = 'O'
                eInvoice['e_invoice_inc_id'] = eInvoiceIncId
            except Exception as e:
                log = traceback.format_exc()
                eInvoice['sync_notes'] = log
                self.logger.exception(e)

        else:
            eInvoice['sync_notes'] = 'O'
        return eInvoice

    def getMInvoices(self):
        self.dstCursor.execute(self.queries.listMInvoicesSQL)
        mInvoices = self.dstCursor.fetchall()
        mInvoices = list(mInvoices)
        return mInvoices

    def updateMInvoice(self, eInvoice):
        print eInvoice
        sql, values = self.getReplaceSqlnValues('e_invoice', eInvoice)
        self.dstCursor.execute(sql, values)

    def syncInvoice(self):
        try:
            for mInvoice in self.getMInvoices():
                eInvoice = self.insertEInvoice(mInvoice)
                log = 'm_invoice_inc_id/e_invoice_inc_id: ' + str(eInvoice['m_invoice_inc_id']) + '/' + str(eInvoice['e_invoice_inc_id']) + ' inserted.'
                self.logger.info(log)
                self.updateMInvoice(eInvoice)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()

    def getMShip(self, eShip):
        f = lambda eShip: eval(self.functs.mShipFunct)
        shipment, shipItemCount = f(eShip)
        f = lambda shipment, eShip: eval(self.functs.mShipExtFunct)
        f(shipment, eShip)
        for i in range(0, shipItemCount):
            f = lambda i, shipment, eShip: eval(self.functs.mShipItemFunct)
            f(i, shipment, eShip)
            f = lambda i, shipment, eShip: eval(self.functs.mShipItemExtFunct)
            f(i, shipment, eShip)

        return shipment

    def insertMShip(self, eShip):
        shipment = self.getMShip(eShip)
        shipment['sync_status'] = 'N'
        shipment['sync_dt'] = datetime.now()
        shipment['sync_notes'] = 'Sync to DST'
        items = shipment.pop('items')
        sql, values = self.getInsertSqlnValues('e_shipment', shipment)
        self.dstCursor.execute(sql, values)
        eShipmentId = self.dstCursor.lastrowid
        for item in items:
            item['e_shipment_id'] = eShipmentId
            sql, values = self.getInsertSqlnValues('e_shipment_item', item)
            self.dstCursor.execute(sql, values)

    def getEShips(self):
        f = lambda : eval(self.functs.eShipsFunct)
        eShips = f()
        return eShips

    def syncShip(self):
        try:
            for eShip in self.getEShips():
                self.insertMShip(eShip)

            self.dstDb.commit()
        except MySQLdb.Error as e:
            self.logger.exception(e)
            self.dstDb.rollback()
            self.dstDb.close()

    def syncProductMaster(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productmaster_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProduct in self.getEProducts(task):
                mProduct = self.insertMProduct(eProduct)
                log = ('id/sku/e_product_id:{0}/{1}/{2}').format(mProduct['id'], mProduct['sku'], mProduct['e_product_id'])
                self.logger.info(log)
                if mProduct['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProduct['id']

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

    def getEProducts(self, task):
        f = lambda task: eval(self.functs.eProductsFunct)
        eProducts = f(task)
        return eProducts

    def insertMProduct(self, eProduct):
        try:
            product = self.getMProduct(eProduct)
            f = lambda product: eval(self.functs.addUpdateMProductFunct)
            mProductId = f(product)
            mProduct = product
            mProduct['id'] = mProductId
            return mProduct
        except Exception as e:
            log = traceback.format_exc()
            mProduct = eProduct
            mProduct['sync_status'] = 'F'
            mProduct['sync_notes'] = log
            self.logger.exception(e)
            return mProduct

    def getMProduct(self, eProduct):
        f = lambda eProduct: eval(self.functs.mProductFunct)
        product = f(eProduct)
        f = lambda product, eProduct: eval(self.functs.mProductExtFunct)
        f(product, eProduct)
        return product

    def syncProductInventory(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productstock_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductInventory in self.getEProductsInventory(task):
                mProductInventory = self.insertMProductInventory(eProductInventory)
                log = ('id/sku/website_code/qty:{0}/{1}/{2}/{3}').format(mProductInventory['id'], mProductInventory['sku'], mProductInventory['website_code'], mProductInventory['qty'])
                self.logger.info(log)
                if mProductInventory['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductInventory['id']

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

    def getEProductsInventory(self, task):
        f = lambda task: eval(self.functs.eProductsInventoryFunct)
        eProductsInventory = f(task)
        return eProductsInventory

    def insertMProductInventory(self, eProductInventory):
        try:
            productInventory = self.getMProductInventory(eProductInventory)
            f = lambda productInventory: eval(self.functs.addUpdateMProductInventoryFunct)
            mProductInventoryId = f(productInventory)
            mProductInventory = productInventory
            mProductInventory['id'] = mProductInventoryId
            return mProductInventory
        except Exception as e:
            log = traceback.format_exc()
            mProductInventory = eProductInventory
            mProductInventory['sync_status'] = 'F'
            mProductInventory['sync_notes'] = log
            self.logger.exception(e)
            return mProductInventory

    def getMProductInventory(self, eProductInventory):
        f = lambda eProductInventory: eval(self.functs.mProductInventoryFunct)
        productInventory = f(eProductInventory)
        f = lambda productInventory, eProductInventory: eval(self.functs.mProductInventoryExtFunct)
        f(productInventory, eProductInventory)
        return productInventory

    def syncProductPrice(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productprice_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductPrice in self.getEProductsPrice(task):
                mProductPrice = self.insertMProductPrice(eProductPrice)
                log = ('id/sku/store_code/price:{0}/{1}/{2}/{3}').format(mProductPrice['id'], mProductPrice['sku'], mProductPrice['store_code'], mProductPrice['price'])
                self.logger.info(log)
                if mProductPrice['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductPrice['id']

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

    def getEProductsPrice(self, task):
        f = lambda task: eval(self.functs.eProductsPriceFunct)
        eProductsPrice = f(task)
        return eProductsPrice

    def insertMProductPrice(self, eProductPrice):
        try:
            productPrice = self.getMProductPrice(eProductPrice)
            f = lambda productPrice: eval(self.functs.addUpdateMProductPriceFunct)
            mProductPriceId = f(productPrice)
            mProductPrice = productPrice
            mProductPrice['id'] = mProductPriceId
            return mProductPrice
        except Exception as e:
            log = traceback.format_exc()
            mProductPrice = eProductPrice
            mProductPrice['sync_status'] = 'F'
            mProductPrice['sync_notes'] = log
            self.logger.exception(e)
            return mProductPrice

    def getMProductPrice(self, eProductPrice):
        f = lambda eProductPrice: eval(self.functs.mProductPriceFunct)
        productPrice = f(eProductPrice)
        f = lambda productPrice, eProductPrice: eval(self.functs.mProductPriceExtFunct)
        f(productPrice, eProductPrice)
        return productPrice

    def syncProductTierPrice(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'producttierprice_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductTierPrice in self.getEProductsTierPrice(task):
                mProductTierPrice = self.insertMProductTierPrice(eProductTierPrice)
                log = ('id/sku/customer_group/qty/price:{0}/{1}/{2}/{3}/{4}').format(mProductTierPrice['id'], mProductTierPrice['sku'], mProductTierPrice['customer_group'], mProductTierPrice['qty'], mProductTierPrice['price'])
                self.logger.info(log)
                if mProductTierPrice['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductTierPrice['id']

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

    def getEProductsTierPrice(self, task):
        f = lambda task: eval(self.functs.eProductsTierPriceFunct)
        eProductsTierPrice = f(task)
        return eProductsTierPrice

    def insertMProductTierPrice(self, eProductTierPrice):
        try:
            productTierPrice = self.getMProductTierPrice(eProductTierPrice)
            f = lambda productTierPrice: eval(self.functs.addUpdateMProductTierPriceFunct)
            mProductTierPriceId = f(productTierPrice)
            mProductTierPrice = productTierPrice
            mProductTierPrice['id'] = mProductTierPriceId
            return mProductTierPrice
        except Exception as e:
            log = traceback.format_exc()
            mProductTierPrice = eProductTierPrice
            mProductTierPrice['sync_status'] = 'F'
            mProductTierPrice['sync_notes'] = log
            self.logger.exception(e)
            return mProductTierPrice

    def getMProductTierPrice(self, eProductTierPrice):
        f = lambda eProductTierPrice: eval(self.functs.mProductTierPriceFunct)
        productTierPrice = f(eProductTierPrice)
        f = lambda productTierPrice, eProductTierPrice: eval(self.functs.mProductTierPriceExtFunct)
        f(productTierPrice, eProductTierPrice)
        return productTierPrice

    def syncProductGroupPrice(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productgroupprice_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductGroupPrice in self.getEProductsGroupPrice(task):
                mProductGroupPrice = self.insertMProductGroupPrice(eProductGroupPrice)
                log = ('id/sku/customer_group/price:{0}/{1}/{2}/{3}').format(mProductGroupPrice['id'], mProductGroupPrice['sku'], mProductGroupPrice['customer_group'], mProductGroupPrice['price'])
                self.logger.info(log)
                if mProductGroupPrice['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductGroupPrice['id']

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

    def getEProductsGroupPrice(self, task):
        f = lambda task: eval(self.functs.eProductsGroupPriceFunct)
        eProductsGroupPrice = f(task)
        return eProductsGroupPrice

    def insertMProductGroupPrice(self, eProductGroupPrice):
        try:
            productGroupPrice = self.getMProductGroupPrice(eProductGroupPrice)
            f = lambda productGroupPrice: eval(self.functs.addUpdateMProductGroupPriceFunct)
            mProductGroupPriceId = f(productGroupPrice)
            mProductGroupPrice = productGroupPrice
            mProductGroupPrice['id'] = mProductGroupPriceId
            return mProductGroupPrice
        except Exception as e:
            log = traceback.format_exc()
            mProductGroupPrice = eProductGroupPrice
            mProductGroupPrice['id'] = None
            mProductGroupPrice['sync_status'] = 'F'
            mProductGroupPrice['sync_notes'] = log
            self.logger.exception(e)
            return mProductGroupPrice

        return

    def getMProductGroupPrice(self, eProductGroupPrice):
        f = lambda eProductGroupPrice: eval(self.functs.mProductGroupPriceFunct)
        productGroupPrice = f(eProductGroupPrice)
        f = lambda productGroupPrice, eProductGroupPrice: eval(self.functs.mProductGroupPriceExtFunct)
        f(productGroupPrice, eProductGroupPrice)
        return productGroupPrice

    def getMCustomer(self, eCustomer):
        f = lambda eCustomer: eval(self.functs.mCustomerFunct)
        customer, addressCount = f(eCustomer)
        f = lambda customer, eCustomer: eval(self.functs.mCustomerExtFunct)
        f(customer, eCustomer)
        for i in range(0, addressCount):
            f = lambda i, customer, eCustomer: eval(self.functs.mCustomerAddressFunct)
            f(i, customer, eCustomer)
            f = lambda i, customer, eCustomer: eval(self.functs.mCustomerAddressExtFunct)
            f(i, customer, eCustomer)

        return customer

    def insertMCustomer(self, eCustomer):
        customer = self.getMCustomer(eCustomer)
        customer['e_json_data'] = json.dumps(customer)
        for key, value in customer.items():
            if key not in ('id', 'email', 'website_code', 'e_json_data'):
                del customer[key]

        customer['sync_status'] = 'N'
        customer['sync_dt'] = datetime.now()
        customer['sync_notes'] = 'Sync to DST'
        updateColumns = {'e_json_data': customer['e_json_data'], 
           'sync_status': 'N', 
           'sync_dt': datetime.now(), 
           'sync_notes': 'Sync to DST'}
        sql, values = self.getInsertOnDupldateUpdateSqlnValues('e_customer', customer, updateColumns)
        self.dstCursor.execute(sql, values)
        eCustomerId = self.dstCursor.lastrowid
        customer['id'] = eCustomerId
        return customer

    def getECustomers(self, task):
        f = lambda task: eval(self.functs.eCustomersFunct)
        eCustomers = f(task)
        return eCustomers

    def syncCustomerToDST(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'customer_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eCustomer in self.getECustomers(task):
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

    def syncConfigProduct(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'configproduct_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eConfigProduct in self.getEConfigProducts(task):
                mConfigProduct = self.insertMConfigProduct(eConfigProduct)
                log = ('id/parent sku/child sku:{0}/{1}/{2}').format(mConfigProduct['id'], mConfigProduct['parent_sku'], mConfigProduct['child_sku'])
                self.logger.info(log)
                if mConfigProduct['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mConfigProduct['id']

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

    def getEConfigProducts(self, task):
        f = lambda task: eval(self.functs.eConfigProductsFunct)
        eConfigProducts = f(task)
        return eConfigProducts

    def insertMConfigProduct(self, eConfigProduct):
        try:
            configProduct = self.getMConfigProduct(eConfigProduct)
            f = lambda configProduct: eval(self.functs.addUpdateMConfigProductFunct)
            mConfigProductId = f(configProduct)
            mConfigProduct = configProduct
            mConfigProduct['id'] = mConfigProductId
            return mConfigProduct
        except Exception as e:
            log = traceback.format_exc()
            mProduct = eConfigProduct
            mConfigProduct['id'] = None
            mConfigProduct['sync_status'] = 'F'
            mConfigProduct['sync_notes'] = log
            self.logger.exception(e)
            return mConfigProduct

        return

    def getMConfigProduct(self, eConfigProduct):
        f = lambda eConfigProduct: eval(self.functs.mConfigProductFunct)
        configProduct = f(eConfigProduct)
        f = lambda configProduct, eConfigProduct: eval(self.functs.mConfigProductExtFunct)
        f(configProduct, eConfigProduct)
        return configProduct

    def syncProductCompanyPrice(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productcompanyprice_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductCompanyPrice in self.getEProductsCompanyPrice(task):
                mProductCompanyPrice = self.insertMProductCompanyPrice(eProductCompanyPrice)
                log = ('id/sku/company_code/qty/price:{0}/{1}/{2}/{3}/{4}').format(mProductCompanyPrice['id'], mProductCompanyPrice['sku'], mProductCompanyPrice['company_code'], mProductCompanyPrice['qty'], mProductCompanyPrice['price'])
                self.logger.info(log)
                if mProductCompanyPrice['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductCompanyPrice['id']

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

    def getEProductsCompanyPrice(self, task):
        f = lambda task: eval(self.functs.eProductsCompanyPriceFunct)
        eProductsCompanyPrice = f(task)
        return eProductsCompanyPrice

    def insertMProductCompanyPrice(self, eProductCompanyPrice):
        try:
            productCompanyPrice = self.getMProductCompanyPrice(eProductCompanyPrice)
            f = lambda productCompanyPrice: eval(self.functs.addUpdateMProductCompanyPriceFunct)
            mProductCompanyPriceId = f(productCompanyPrice)
            mProductCompanyPrice = productCompanyPrice
            mProductCompanyPrice['id'] = mProductCompanyPriceId
            return mProductCompanyPrice
        except Exception as e:
            log = traceback.format_exc()
            mProductCompanyPrice = eProductCompanyPrice
            mProductCompanyPrice['sync_status'] = 'F'
            mProductCompanyPrice['sync_notes'] = log
            self.logger.exception(e)
            return mProductCompanyPrice

    def getMProductCompanyPrice(self, eProductCompanyPrice):
        f = lambda eProductCompanyPrice: eval(self.functs.mProductCompanyPriceFunct)
        productCompanyPrice = f(eProductCompanyPrice)
        f = lambda productCompanyPrice, eProductCompanyPrice: eval(self.functs.mProductCompanyPriceExtFunct)
        f(productCompanyPrice, eProductCompanyPrice)
        return productCompanyPrice

    def syncProductCategory(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'productcategory_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eProductCategory in self.getEProductCategory(task):
                mProductCategory = self.insertMProductCategory(eProductCategory)
                log = ('id/sku/category:{0}/{1}/{2}').format(mProductCategory['id'], mProductCategory['sku'], mProductCategory['path'])
                self.logger.info(log)
                if mProductCategory['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mProductCategory['id']

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

    def getEProductCategory(self, task):
        f = lambda task: eval(self.functs.eProductsCategoryFunct)
        eProductCategorys = f(task)
        return eProductCategorys

    def insertMProductCategory(self, eProductCategory):
        try:
            productCategory = self.getMProductCategory(eProductCategory)
            f = lambda productCategory: eval(self.functs.addUpdateMProductCategoryFunct)
            mProductCategoryId = f(productCategory)
            mProductCategory = productCategory
            mProductCategory['id'] = mProductCategoryId
            return mProductCategory
        except Exception as e:
            log = traceback.format_exc()
            mProduct = eProductCategory
            mProductCategory['id'] = None
            mProductCategory['sync_status'] = 'F'
            mProductCategory['sync_notes'] = log
            self.logger.exception(e)
            return mProductCategory

        return

    def getMProductCategory(self, eProductCategory):
        f = lambda eProductCategory: eval(self.functs.mProductCategoryFunct)
        productCategory = f(eProductCategory)
        f = lambda productCategory, eProductCategory: eval(self.functs.mProductCategoryExtFunct)
        f(productCategory, eProductCategory)
        return productCategory

    def getMCompany(self, eCompany):
        f = lambda eCompany: eval(self.functs.mCompanyFunct)
        company, addressCount, contactCount = f(eCompany)
        f = lambda company, eCompany: eval(self.functs.mCompanyExtFunct)
        f(company, eCompany)
        for i in range(0, addressCount):
            f = lambda i, company, eCompany: eval(self.functs.mCompanyAddressFunct)
            f(i, company, eCompany)
            f = lambda i, company, eCompany: eval(self.functs.mCompanyAddressExtFunct)
            f(i, company, eCompany)

        for i in range(0, contactCount):
            f = lambda i, company, eCompany: eval(self.functs.mCompanyContactFunct)
            f(i, company, eCompany)
            f = lambda i, company, eCompany: eval(self.functs.mCompanyContactExtFunct)
            f(i, company, eCompany)

        return company

    def insertMCompany(self, eCompany):
        company = self.getMCompany(eCompany)
        company['e_data'] = json.dumps(company)
        for key, value in company.items():
            if key not in ('id', 'company_code', 'website_code', 'e_data'):
                del company[key]

        print company
        company['sync_status'] = 'N'
        company['sync_dt'] = datetime.now()
        company['sync_notes'] = 'Sync to DST'
        updateColumns = {'e_data': company['e_data'], 
           'sync_status': 'N', 
           'sync_dt': datetime.now(), 
           'sync_notes': 'Sync to DST'}
        sql, values = self.getInsertOnDupldateUpdateSqlnValues('e_company', company, updateColumns)
        print sql
        print values
        self.dstCursor.execute(sql, values)
        print self.dstCursor._last_executed
        eCompanyId = self.dstCursor.lastrowid
        company['id'] = eCompanyId
        return company

    def getECompanys(self, task):
        f = lambda task: eval(self.functs.eCompanysFunct)
        eCompanys = f(task)
        return eCompanys

    def syncCompanyToDST(self):
        start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task = 'company_erp_to_dst'
        lastCutoffEntityId = None
        syncStatus = 'I'
        syncNotes = 'Nothing needs to sync'
        try:
            for eCompany in self.getECompanys(task):
                mCompany = self.insertMCompany(eCompany)
                log = ('id/company_code/:{0}/{1}').format(mCompany['id'], mCompany['company_code'])
                self.logger.info(log)
                if mCompany['id'] > lastCutoffEntityId:
                    lastCutoffEntityId = mCompany['id']

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
# okay decompiling ERPSyncAbstract.pyc
