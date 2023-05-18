# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/MAGE2/MageDSTSync.py
# Compiled at: 2021-04-20 08:24:51
__author__ = 'sandy.tu'
import MySQLdb, sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import json
from MagentoCommon import *
from MagentoProduct import MagentoProduct
from MagentoProductImage import MagentoProductImage
from MagentoOrder import MagentoOrder
from MagentoCustomer import MagentoCustomer

class MagentoDSTSync(object):

    def __init__(self, mageConf, dstConf):
        if dstConf['dbEngine'] == 'mssql':
            self.dstDbEngine = __import__('pymssql')
        else:
            self.dstDbEngine = MySQLdb
        if 'logFileName' not in mageConf or mageConf['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            updatedAt = '%s-%s-%s %s:%s:%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
            logFileName = 'log/magento_dst_sync_' + updatedAt + '.' + 'log'
            mageConf['logFileName'] = logFileName
        if 'logPath' in mageConf and mageConf['logPath'] != '':
            mageConf['logFileName'] = mageConf['logPath'] + mageConf['logFileName']
        self.logger = Logger('Magento', mageConf['logFileName'])
        self.mageConf = mageConf
        if 'edition' not in mageConf or mageConf['edition'] == '':
            self.mageConf['edition'] = 'community'
        self.dstConf = dstConf
        self.commitCount = 500
        self.eShipmentItemJoinColumn = 'e_shipment_id'
        self.eCreditMemoItemJoinColumn = 'e_credit_memo_id'
        self.dstQueries = {'getTaskLastCutOffDateSQL': 'SELECT max(last_cutoff_dt) FROM sync_control WHERE task = %s', 'listEProducts': '\n                SELECT id, sku, e_product_id, raw_data\n                FROM e_product_master\n                WHERE sync_status = %s\n            ', 
           'updateEProduct': '\n                UPDATE e_product_master\n                SET m_product_id = %s,\n                formatted_data = %s,\n                sync_status = %s,\n                sync_dt = now(),\n                sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEProductImages': '\n                SELECT * FROM e_product_image WHERE sync_status = %s\n            ', 
           'updateEProductImage': '\n                UPDATE e_product_image\n                SET http_response_code = %s,\n                attempt_count = attempt_count + 1,\n                media_url = %s,\n                sync_status = %s,\n                sync_dt = now(),\n                sync_notes = %s\n                WHERE\n                id = %s\n            ', 
           'listEProductInventorySQL': 'SELECT * FROM e_product_inventory WHERE sync_status = %s', 
           'updateEProductInventorySQL': '\n                UPDATE e_product_inventory\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEProductPriceSQL': 'SELECT * FROM e_product_price WHERE sync_status = %s', 
           'updateEProductPriceSQL': '\n                UPDATE e_product_price\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listECreditMemoSQL': 'SELECT * FROM e_credit_memo WHERE sync_status = %s', 
           'listECreditMemoItemsSQL': 'SELECT * FROM e_credit_memo_item WHERE ' + self.eCreditMemoItemJoinColumn + ' = %s', 
           'updateECreditMemoSQL': '\n                UPDATE e_credit_memo\n                SET m_credit_memo_inc_id = %s, sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEShipmentSQL': '\n                SELECT *\n                FROM e_shipment\n                WHERE sync_status = %s\n            ', 
           'listEShipmentItemSQL': 'SELECT * FROM e_shipment_item WHERE ' + self.eShipmentItemJoinColumn + ' = %s', 
           'updateEShipmentSQL': '\n                UPDATE e_shipment\n                SET m_shipment_inc_id=%s, m_invoice_inc_id = %s, sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'clearMProductInventorySQL': 'DELETE FROM m_product_inventory', 
           'listEProductGroupPriceSQL': 'SELECT * FROM e_product_group_price WHERE sync_status = %s', 
           'updateEProductGroupPriceSQL': '\n                UPDATE e_product_group_price\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEProductGroupTierPriceSQL': 'SELECT * FROM e_product_tier_price WHERE sync_status = %s', 
           'updateEProductGroupTierPriceSQL': '\n                UPDATE e_product_tier_price\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listNeedUpdateStatusOrderSQL': "\n                SELECT * FROM m_order WHERE m_order_status in (%s) AND sync_status = 'N'\n            ", 
           'updateMOrderStatusSQL': '\n                UPDATE m_order\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEConfigProductsSQL': '\n                SELECT *\n                FROM e_config_product\n                WHERE sync_status = %s\n            ', 
           'updateEConfigProductSQL': '\n                UPDATE e_config_product\n                SET\n                formatted_data = %s,\n                sync_status = %s,\n                sync_dt = now(),\n                sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEProductCompanyPriceSQL': 'SELECT * FROM e_product_company_price WHERE sync_status = %s', 
           'updateEProductCompanyPriceSQL': '\n                UPDATE e_product_company_price\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listEProductCategoriesSQL': 'SELECT * FROM e_product_category WHERE sync_status = %s', 
           'updateEProductCategorySQL': '\n                UPDATE e_product_category\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listECompaniesSQL': '\n                SELECT *\n                FROM e_company\n                WHERE sync_status = %s\n            ', 
           'updateECompanySQL': '\n                UPDATE e_company\n                SET m_data = %s, sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'listECustomersSQL': '\n                SELECT *\n                FROM e_customer\n                WHERE sync_status = %s\n            ', 
           'updateECustomerSQL': '\n                UPDATE e_customer\n                SET m_json_data = %s, sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            '}
        self.mageQueries = {'cleanNoChildConfigProductSQL': "\n                DELETE FROM catalog_product_entity\n                WHERE entity_id NOT IN\n                (SELECT DISTINCT parent_id AS entity_id FROM catalog_product_super_link)\n                AND type_id = 'configurable'\n            "}
        self._needUpdateOrderStatusMatrix = {}
        self.openMagentoDb()
        self.openDstDb()

    def __del__(self):
        self.closeMagentoDb()
        self.closeDstDb()
        self.logoutMagentoApi()

    def openMagentoDb(self, connection=None):
        if connection and connection.open:
            self.mageConn = connection
        else:
            try:
                host = self.mageConf['host']
                user = self.mageConf['user']
                pwd = self.mageConf['password']
                db = self.mageConf['db']
                self.mageConn = MySQLdb.connect(host, user, pwd, db, charset='utf8', use_unicode=False)
                self.logger.info('Open Magento database connection')
            except Exception as e:
                log = 'Failed to connect to Magento Database with error: %s' % str(e)
                self.logger.exception(log)
                raise

        self.mageCursor = self.mageConn.cursor()

    def closeMagentoDb(self):
        self.mageConn.close()
        self.logger.info('Disconnect from Magento Database')

    def openDstDb(self, connection=None):
        if connection and connection.open:
            self.dstConn = connection
        else:
            try:
                self.dstConn = self.dstDbEngine.connect(self.dstConf['host'], self.dstConf['user'], self.dstConf['password'], self.dstConf['db'], charset='utf8')
                self.logger.info('Open DST database connection')
            except Exception as e:
                log = ('Failed to connect to DST Database with error: {0}').format(str(e))
                self.logger.exception(log)
                raise

        self.dstCursor = self.dstConn.cursor()
        if self.dstDbEngine == MySQLdb:
            self.dstCursor.execute('SET NAMES utf8')

    def closeDstDb(self):
        self.dstConn.close()
        self.logger.info('Disconnect from DST Database')

    def loginMagentoApi(self):
        self.mageApi = MagentoApi(self.mageConf)

    def logoutMagentoApi(self):
        del self.mageApi

    def generateDstQueryParams(self, params, dbEngine=''):
        if dbEngine == '':
            dbEngine = self.dstConf['dbEngine']
        if dbEngine == '':
            dbEngine = 'mysql'
        if dbEngine == 'mysql':
            if isinstance(params, tuple):
                params = list(params)
        if dbEngine == 'mssql':
            if isinstance(params, list):
                params = tuple(params)
        return params

    def getSyncTaskLastCutOffDate(self, task):
        params = self.generateDstQueryParams([task])
        self.dstCursor.execute(self.dstQueries['getTaskLastCutOffDateSQL'], params)
        res = self.dstCursor.fetchone()
        if res is not None and len(res) > 0 and res[0] is not None:
            lastCutoffDt = str(res[0])
        else:
            lastCutoffDt = '2000-01-01 00:00:00'
        return lastCutoffDt

    def fetchCursorResultAsDict(self, cursor):
        result = []
        columns = tuple([ d[0].decode('utf8') for d in cursor.description ])
        for row in cursor:
            result.append(dict(zip(columns, row)))

        return result

    def importModule(self, moduleName):
        try:
            projectName = self.mageConf['projectName']
            module = __import__(moduleName + 'Agent')
            moduleClass = getattr(module, moduleName + projectName)
            instance = moduleClass(self.mageConf, self.mageConn, self.mageApi, self.dstCursor)
        except Exception as e:
            print e
            module = __import__(moduleName)
            moduleClass = getattr(module, moduleName)
            instance = moduleClass(self.mageConf, self.mageConn, self.mageApi, self.dstCursor)

        return instance

    def syncProductMaster(self, productAttributesMap={}, syncCategoryThroughAPI=False, refreshUrlRewriteThroughAPI=False):
        try:
            if syncCategoryThroughAPI or refreshUrlRewriteThroughAPI:
                self.mageApi = Magento2RestApi(self.mageConf)
            else:
                self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams(['N'])
            self.dstCursor.execute(self.dstQueries['listEProducts'], params)
            res = self.dstCursor.fetchall()
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    id, eSku, eProductId, rawData = product
                    syncResult = magentoProduct.importProduct(rawData, productAttributesMap, syncCategoryThroughAPI)
                    syncResult['id'] = id
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            if syncCategoryThroughAPI == True:
                for syncResult in syncResults:
                    if syncResult['sync_status'] == 'O' and syncResult['action'] != 'delete':
                        try:
                            productId = syncResult['product_id']
                            formattedProductJsonObj = json.loads(syncResult['formatted_data'])
                            magentoProduct.catalogCategoryAssignProduct(productId, formattedProductJsonObj)
                        except Exception as e:
                            log = traceback.format_exc()
                            syncResult['sync_status'] = 'F'
                            syncResult['sync_notes'] = syncResult['sync_notes'] + log

            if refreshUrlRewriteThroughAPI == True:
                for syncResult in syncResults:
                    if syncResult['sync_status'] == 'O' and syncResult['action'] != 'delete':
                        try:
                            productId = syncResult['product_id']
                            formattedProductJsonObj = json.loads(syncResult['formatted_data'])
                            magentoProduct.refreshUrlRewriteThroughAPI(productId, formattedProductJsonObj)
                        except Exception as e:
                            log = traceback.format_exc()
                            syncResult['sync_status'] = 'F'
                            syncResult['sync_notes'] = syncResult['sync_notes'] + log

            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['product_id'], syncResult['formatted_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProduct'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductInventory(self, syncStatus='N', multiLocationModule=''):
        try:
            self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductInventorySQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    if multiLocationModule == 'aitoc':
                        syncResult = magentoProduct.importAitocMultiLocationInventory(product)
                    else:
                        syncResult = magentoProduct.importInventory(product)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductInventorySQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductPrice(self, syncStatus='N'):
        try:
            self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductPriceSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    syncResult = magentoProduct.importProductPrice(product)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductPriceSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductImage(self, syncThroughAPI=False):
        try:
            if syncThroughAPI:
                self.mageApi = MagentoApi(self.mageConf)
            else:
                self.mageApi = None
            magentoProductImage = self.importModule('MagentoProductImage')
            params = self.generateDstQueryParams(['N'])
            self.dstCursor.execute(self.dstQueries['listEProductImages'], params)
            rows = self.fetchCursorResultAsDict(self.dstCursor)
            for eProductImage in rows:
                if syncThroughAPI:
                    syncResult = magentoProductImage.createProductImageThroughAPI(eProductImage)
                else:
                    syncResult = magentoProductImage.importImage(eProductImage)
                param = self.generateDstQueryParams([
                 syncResult['http_response_code'],
                 syncResult['media_url'],
                 syncResult['sync_status'],
                 syncResult['sync_notes'],
                 eProductImage['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductImage'], param)

            self.mageConn.commit()
            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def exportProductsToJson(self, fileName='products.json', attributeSetName='', limits=1, storeId=0):
        self.mageApi = None
        magentoProduct = self.importModule('MagentoProduct')
        magentoProduct.exportProductsToJson(fileName, attributeSetName, limits, storeId)
        return

    def exportProductsToCsv(self, fileName='products.csv', attributeSetName='', limits=1, storeId=0):
        self.mageApi = None
        magentoProduct = self.importModule('MagentoProduct')
        magentoProduct.exportProductsToCsv(fileName, attributeSetName, limits, storeId)
        return

    def syncMagentoOrderToDst(self):
        self.mageApi = None
        magentoOrder = self.importModule('MagentoOrder')
        syncResult = magentoOrder.syncMagentoOrderToDst()
        if syncResult['sync_status'] == 'O':
            self.dstConn.commit()
        else:
            self.dstConn.rollback()
        return

    def syncShipmentToMagento(self, syncStatus):
        self.mageApi = Magento2RestApi(self.mageConf)
        magentoOrder = self.importModule('MagentoOrder')
        params = self.generateDstQueryParams([syncStatus])
        self.dstCursor.execute(self.dstQueries['listEShipmentSQL'], params)
        eShipments = self.fetchCursorResultAsDict(self.dstCursor)
        syncResults = []
        for eShipment in eShipments:
            itemParams = self.generateDstQueryParams([eShipment['id']])
            self.dstCursor.execute(self.dstQueries['listEShipmentItemSQL'], itemParams)
            eShipment['lines'] = self.fetchCursorResultAsDict(self.dstCursor)
            try:
                syncResult = magentoOrder.importShipment(eShipment)
                syncResults.append(syncResult)
            except Exception as e:
                log = traceback.format_exc()
                self.logger.exception(log)

        self.mageConn.commit()
        for syncResult in syncResults:
            param = self.generateDstQueryParams([
             syncResult['m_shipment_inc_id'],
             syncResult['m_invoice_inc_id'],
             syncResult['sync_status'],
             syncResult['sync_notes'],
             syncResult['id']])
            self.dstCursor.execute(self.dstQueries['updateEShipmentSQL'], param)

        self.dstConn.commit()

    def syncCreditMemoToMagento(self, syncStatus):
        self.mageApi = MagentoApi(self.mageConf)
        magentoOrder = self.importModule('MagentoOrder')
        params = self.generateDstQueryParams([syncStatus])
        self.dstCursor.execute(self.dstQueries['listECreditMemoSQL'], params)
        eCreditMemos = self.fetchCursorResultAsDict(self.dstCursor)
        syncResults = []
        for eCreditMemo in eCreditMemos:
            itemParams = self.generateDstQueryParams(eCreditMemo['id'])
            self.dstCursor.execute(self.dstQueries['listECreditMemoItemsSQL'], itemParams)
            eCreditMemo['lines'] = self.fetchCursorResultAsDict(self.dstCursor)
            try:
                syncResult = magentoOrder.importCreditMemo(eCreditMemo)
                syncResults.append(syncResult)
            except Exception as e:
                log = traceback.format_exc()
                self.logger.exception(log)

        self.mageConn.commit()
        for syncResult in syncResults:
            param = self.generateDstQueryParams([
             syncResult['m_credit_memo_inc_id'],
             syncResult['sync_status'],
             syncResult['sync_notes'],
             syncResult['id']])
            self.dstCursor.execute(self.dstQueries['updateECreditMemoSQL'], param)

        self.dstConn.commit()

    def exportCustomersToJson(self, fileName='customers.json', lastCutoffDt='2015-11-01', limits=1):
        self.mageApi = None
        magentoCustomer = self.importModule('MagentoCustomer')
        magentoCustomer.exportCustomersToJson(fileName, lastCutoffDt, limits)
        return

    def syncMagentoCustomersToDst(self, lastCutoffDt='', limits=1):
        self.mageApi = None
        magentoCustomer = self.importModule('MagentoCustomer')
        syncResult = magentoCustomer.syncMagentoCustomersToDst(lastCutoffDt, limits)
        self.dstConn.commit()
        return

    def syncMagentoProductsToDst(self, attributeSetName='', lastCutoffDt='', limits=1, allStores=0):
        self.mageApi = None
        magentoProduct = self.importModule('MagentoProduct')
        syncResult = magentoProduct.syncMagentoProductsToDst(attributeSetName, lastCutoffDt, limits, allStores)
        self.dstConn.commit()
        return

    def clearMProductInventory(self):
        self.logger.info('Clear m_product_inventory start...')
        self.dstCursor.execute(self.dstQueries['clearMProductInventorySQL'])
        self.logger.info('Clear m_product_inventory done.')

    def syncMagentoInventoryToDST(self, multiLocationModule=''):
        self.mageApi = None
        self.clearMProductInventory()
        magentoProduct = self.importModule('MagentoProduct')
        syncResult = magentoProduct.syncMagentoInventoryToDST(multiLocationModule)
        self.dstConn.commit()
        return

    def syncMagentoOrderStatusHistoryToDst(self):
        self.mageApi = None
        magentoOrder = self.importModule('MagentoOrder')
        syncResult = magentoOrder.syncMagentoOrderStatusHistoryToDst()
        if syncResult['sync_status'] == 'O':
            self.dstConn.commit()
        else:
            self.dstConn.rollback()
        return

    def importAttributeOptions(self, attributeCode, entityTypeCode, optionsData):
        self.mageApi = None
        try:
            magentoCore = MagentoCore(self.mageConf, self.mageConn)
            for option in optionsData:
                optionData = {}
                for k, v in option.items():
                    optionData[int(k)] = v

                magentoCore.setAttributeOptionValues(attributeCode, optionData, entityTypeCode)
                info = ('Options import successfully for entity_type_code/attribute_code/data: {0}/{1}/{2}').format(entityTypeCode, attributeCode, option)

            log = ('Options import successfully for entity_type_code/attribute_code: {0}/{1}').format(entityTypeCode, attributeCode)
            self.logger.info(log)
            self.mageConn.commit()
        except Exception as e:
            error = ('Options failed to import for entity_type_code/attribute_code: {0}/{1} with error: {2}').format(entityTypeCode, attributeCode, traceback.format_exc())
            self.logger.exception(error)
            self.mageConn.rollback()

        return

    def syncProductGroupPrice(self, syncStatus='N'):
        try:
            self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductGroupPriceSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    syncResult = magentoProduct.importGroupPrice(product)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductGroupPriceSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductGroupTierPrice(self, syncStatus='N'):
        try:
            self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductGroupTierPriceSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    syncResult = magentoProduct.importGroupTierPrice(product)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductGroupTierPriceSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncMagentoOrderStatusFromDST(self, syncStatus):
        self.mageApi = MagentoApi(self.mageConf)
        magentoOrder = self.importModule('MagentoOrder')
        if len(self._needUpdateOrderStatusMatrix) == 0:
            self._needUpdateOrderStatusMatrix = {'--': '--'}
        srcOrderStatusList = self._needUpdateOrderStatusMatrix.keys()
        format_strings = (',').join(['%s'] * len(srcOrderStatusList))
        listNeedUpdateStatusOrderSQL = self.queries['listNeedUpdateStatusOrderSQL'] % format_strings
        self.dstCursor.execute(listNeedUpdateStatusOrderSQL, srcOrderStatusList)
        orders = self.fetchCursorResultAsDict(self.dstCursor)
        syncResults = []
        for order in orders:
            try:
                targetOrderStatus = self._needUpdateOrderStatusMatrix[order['m_order_status']]
                syncResult = magentoProduct.updateMagentoOrderStatus(order, targetOrderStatus)
                syncResults.append(syncResult)
            except Exception as e:
                log = traceback.format_exc()
                self.logger.exception(log)

        for syncResult in syncResults:
            param = self.generateDstQueryParams([
             syncResult['sync_status'],
             syncResult['sync_notes'],
             syncResult['id']])
            self.dstCursor.execute(self.dstQueries['updateMOrderStatusSQL'], param)

        self.dstConn.commit()

    def cleanNoChildConfigProduct(self):
        self.mageCursor.execute(self.mageQueries['cleanNoChildConfigProductSQL'])
        self.logger.info('Clean up no child config products')

    def syncConfigProduct(self, syncStatus='N'):
        try:
            self.mageApi = None
            magentoConfigProduct = self.importModule('MagentoConfigProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEConfigProductsSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    sourceProduct = product['raw_data']
                    syncResult = magentoConfigProduct.importConfigProduct(sourceProduct)
                    syncResult['id'] = product['id']
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.cleanNoChildConfigProduct()
            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['formatted_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEConfigProductSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductCompanyPrice(self, syncStatus='N'):
        try:
            self.mageApi = None
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductCompanyPriceSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    syncResult = magentoProduct.importCompanyTierPrice(product)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductCompanyPriceSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncProductCategory(self, syncStatus='N', througApi=False):
        try:
            self.mageApi = None
            if througApi == True:
                self.mageApi = Magento2RestApi(self.mageConf)
            magentoProduct = self.importModule('MagentoProduct')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listEProductCategoriesSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for product in res:
                try:
                    syncResult = magentoProduct.importProductCategory(product, througApi)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateEProductCategorySQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncCompanyToMage(self, syncStatus='N', througApi=False):
        try:
            self.mageApi = None
            if througApi == True:
                self.mageApi = Magento2RestApi(self.mageConf)
            magentoCustomer = self.importModule('MagentoCustomer')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listECompaniesSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for company in res:
                try:
                    syncResult = magentoCustomer.importCompany(company)
                    syncResults.append(syncResult)
                    if syncResult['sync_status'] == 'F':
                        self.mageConn.rollback()
                    else:
                        self.mageConn.commit()
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)
                    self.mageConn.rollback()

            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['m_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateECompanySQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def syncCustomerToMage(self, syncStatus='N', througApi=False):
        try:
            self.mageApi = None
            if througApi == True:
                self.mageApi = Magento2RestApi(self.mageConf)
            magentoCustomer = self.importModule('MagentoCustomer')
            params = self.generateDstQueryParams([syncStatus])
            self.dstCursor.execute(self.dstQueries['listECustomersSQL'], params)
            res = self.fetchCursorResultAsDict(self.dstCursor)
            syncResults = []
            dstParams = []
            for customer in res:
                try:
                    eCustomer = customer['e_json_data']
                    syncResult = magentoCustomer.importCustomer(eCustomer)
                    syncResult['id'] = customer['id']
                    syncResults.append(syncResult)
                    if syncResult['sync_status'] == 'F':
                        self.mageConn.rollback()
                    else:
                        self.mageConn.commit()
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)
                    self.mageConn.rollback()

            for syncResult in syncResults:
                param = self.generateDstQueryParams([syncResult['m_customer_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']])
                self.dstCursor.execute(self.dstQueries['updateECustomerSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return