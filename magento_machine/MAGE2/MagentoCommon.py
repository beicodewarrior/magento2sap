# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/MAGE2/MagentoCommon.py
# Compiled at: 2021-04-20 08:24:51
__author__ = 'sandy.tu'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import MySQLdb
from suds.plugin import MessagePlugin
import ssl, logging, requests, json
from requests.auth import HTTPBasicAuth
if hasattr(ssl, '_create_default_https_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

class MagentoCore(object):

    def __init__(self, mageConf, mageConn=None):
        if 'logFileName' not in mageConf or mageConf['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            updatedAt = '%s-%s-%s-%s-%s-%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
            logFileName = 'log/magento_sync_' + updatedAt + '.' + 'log'
            mageConf['logFileName'] = logFileName
        self.queries = {'getWebsitesSQL': 'SELECT website_id,code,name FROM core_website', 'getStoresSQL': '\n                SELECT s.store_id, s.code as store_code, s.name as store_name, w.website_id, w.code as website_code, g.root_category_id\n                FROM core_store s, core_website w, core_store_group g\n                WHERE s.website_id = w.website_id and s.group_id = g.group_id;\n            ', 'getWebsiteIdByCodeSQL': 'SELECT website_id FROM core_website WHERE code = %s', 'getWebsiteCodeByIdSQL': 'SELECT code FROM core_website WHERE website_id = %s', 
           'getStoreIdByWebsiteCodeSQL': 'SELECT store_id FROM core_store s INNER JOIN core_website w ON s.website_id = w.website_id AND w.code = %s', 
           'getAttributeMetadataSQL': '\n                SELECT DISTINCT t1.attribute_id, t2.entity_type_id, t1.backend_type, t1.frontend_input\n                FROM eav_attribute t1, eav_entity_type t2\n                WHERE t1.entity_type_id = t2.entity_type_id\n                AND t1.attribute_code = %s\n                AND t2.entity_type_code = %s;\n            ', 
           'getOptionIdSQL': '\n                SELECT t1.option_id\n                FROM eav_attribute_option t1, eav_attribute_option_value t2\n                WHERE t1.option_id = t2.option_id\n                AND t1.attribute_id = %s AND t2.value = %s AND t2.store_id = %s\n            ', 
           'insertEavAttributeOptionSQL': 'INSERT INTO eav_attribute_option (attribute_id) VALUES (%s)', 
           'insertOptionValueSQL': 'INSERT INTO eav_attribute_option_value (option_id,store_id,value) VALUES (%s,%s,%s)', 
           'updateOptionValueSQL': 'UPDATE eav_attribute_option_value SET value = %s WHERE option_id = %s AND store_id = %s', 
           'getAttributeValueSQL': 'SELECT value FROM {0}_entity_{1} WHERE attribute_id = %s AND entity_id = %s', 
           'getAttributeOptionValueSQL': '\n                SELECT\n                t3.value\n                FROM\n                eav_attribute_option t2,\n                eav_attribute_option_value t3\n                WHERE\n                t2.option_id = t3.option_id\n                AND t2.attribute_id = %s\n                AND t3.option_id = %s\n                AND t3.store_id = %s\n                ', 
           'getAttributesByEntityTypeAndAttributeSetSQL': '\n                SELECT\n                a.entity_type_id, b.entity_type_code,\n                d.attribute_set_id, d.attribute_set_name,\n                a.attribute_id, a.attribute_code,\n                a.backend_type, a.frontend_input, a.frontend_label, a.is_required, a.is_user_defined\n                FROM eav_attribute a\n                INNER JOIN eav_entity_attribute c on (a.attribute_id = c.attribute_id and a.entity_type_id = c.entity_type_id)\n                INNER JOIN eav_attribute_set d on (c.attribute_set_id = d.attribute_set_id)\n                INNER JOIN eav_entity_type b on (a.entity_type_id = b.entity_type_id)\n                WHERE b.entity_type_code = %s and d.attribute_set_name = %s\n            ', 
           'getAttributesByEntityTypeSQL': '\n                SELECT\n                a.entity_type_id, b.entity_type_code,\n                a.attribute_id, a.attribute_code,\n                a.backend_type, a.frontend_input, a.frontend_label, a.is_required, a.is_user_defined\n                FROM eav_attribute a\n                INNER JOIN eav_entity_type b on (a.entity_type_id = b.entity_type_id)\n                WHERE b.entity_type_code = %s\n            ', 
           'optionValueExistSQL': '\n                SELECT COUNT(*) FROM eav_attribute_option_value\n                WHERE option_id = %s\n                AND store_id = %s\n            ', 
           'getCustomerGroupCodeByIdSQL': 'SELECT customer_group_code FROM customer_group WHERE customer_group_id = %s', 
           'getCustomerGroupIdByCodeSQL': 'SELECT customer_group_id FROM customer_group WHERE customer_group_code = %s', 
           'getTaxClassIdByNameSQL': 'SELECT class_id FROM tax_class WHERE class_name = %s and class_type = %s'}
        self.queries['getWebsitesSQL'] = 'SELECT website_id,code,name FROM store_website'
        self.queries['getStoresSQL'] = '\n            SELECT s.store_id, s.code as store_code, s.name as store_name, w.website_id, w.code as website_code, g.root_category_id\n            FROM store s, store_website w, store_group g\n            WHERE s.website_id = w.website_id and s.group_id = g.group_id;\n        '
        self.queries['getWebsiteIdByCodeSQL'] = 'SELECT website_id FROM store_website WHERE code = %s'
        self.queries['getWebsiteCodeByIdSQL'] = 'SELECT code FROM store_website WHERE website_id = %s'
        self.queries['getStoreIdByWebsiteCodeSQL'] = 'SELECT store_id FROM store s INNER JOIN core_website w ON s.website_id = w.website_id AND w.code = %s'
        self.queries['insertCatalogProductSQL'] = '\n            INSERT INTO catalog_product_entity\n            (attribute_set_id, type_id, sku, has_options, required_options, created_at, updated_at)\n            VALUES(%s, %s, %s, 0, 0, now(), now())\n        '
        self.queries['updateCatalogProductSQL'] = '\n            UPDATE catalog_product_entity\n            SET attribute_set_id = %s,\n            type_id = %s,\n            updated_at = now(),\n            WHERE entity_id = %s\n        '
        self.logger = logging.getLogger('Magento')
        self.mageConf = mageConf
        self.openMagentoDb(mageConn)
        self.adminStoreId = 0

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

    def fetchCursorResultAsDict(self, cursor):
        result = []
        columns = tuple([ d[0].decode('utf8') for d in cursor.description ])
        for row in cursor:
            result.append(dict(zip(columns, row)))

        return result

    def getWebsites(self):
        self.mageCursor.execute(self.queries['getWebsitesSQL'])
        res = self.mageCursor.fetchall()
        websites = {}
        if res is not None and len(res) > 0:
            for site in res:
                websites[site[1]] = {'id': site[0], 'name': site[2]}
                if site[1] == 'admin':
                    self.adminWebsiteId = site[0]

        return websites

    def getStores(self):
        self.mageCursor.execute(self.queries['getStoresSQL'])
        res = self.mageCursor.fetchall()
        stores = {}
        if res is not None and len(res) > 0:
            for s in res:
                stores[s[1]] = {'id': s[0], 'name': s[2], 
                   'website_id': s[3], 
                   'website_code': s[4], 
                   'root_category_id': s[5]}
                if s[1] == 'admin':
                    self.adminStoreId = s[0]

        return stores

    def getWebsiteIdByCode(self, websiteCode):
        self.mageCursor.execute(self.queries['getWebsiteIdByCodeSQL'], [websiteCode])
        res = self.mageCursor.fetchone()
        if res is not None:
            websiteId = int(res[0])
        else:
            websiteId = 0
        return websiteId

    def getWebsiteCodeById(self, websiteId):
        self.mageCursor.execute(self.queries['getWebsiteCodeByIdSQL'], [websiteId])
        res = self.mageCursor.fetchone()
        if res is not None:
            websiteCode = res[0]
        else:
            websiteCode = ''
        return websiteCode

    def getStoreIdByWebsiteCode(self, websiteCode):
        self.mageCursor.execute(self.queries['getStoreIdByWebsiteCodeSQL'], [websiteCode])
        res = self.mageCursor.fetchone()
        if res is not None:
            storeId = int(res[0])
        else:
            storeId = 0
        return storeId

    def getAttributeMetadata(self, attributeCode, entityTypeCode='catalog_product'):
        self.mageCursor.execute(self.queries['getAttributeMetadataSQL'], [attributeCode, entityTypeCode])
        item = self.mageCursor.fetchone()
        if item is not None and len(item) > 0:
            attributeMetadata = {'attribute_code': attributeCode, 'attribute_id': item[0], 'entity_type_id': item[1], 'backend_type': item[2], 
               'frontend_input': item[3]}
            return attributeMetadata
        else:
            return
            return

    def setAttributeOptionValues(self, attributeCode, options, entityTypeCode='catalog_product', updateExistingOption=False):
        if not options:
            self.logger.info(('Options is empty for {0}').format(attributeCode))
            return
        else:
            attributeMetadata = self.getAttributeMetadata(attributeCode, entityTypeCode)
            if attributeMetadata is None:
                self.logger.info(('Attribute metadata is not found for {0}').format(attributeCode))
                return
            if attributeMetadata['frontend_input'] not in ('select', 'multiselect'):
                self.logger.info(('Attribute {0} frontend input is {1}. No option needs to set.').format(attributeCode, attributeMetadata['frontend_input']))
                return
            attributeId = attributeMetadata['attribute_id']
            self.mageCursor.execute(self.queries['getOptionIdSQL'], (attributeId, options[self.adminStoreId], self.adminStoreId))
            res = self.mageCursor.fetchone()
            optionId = 0
            if res is not None and len(res) > 0:
                optionId = int(res[0])
            if optionId == 0:
                self.mageCursor.execute(self.queries['insertEavAttributeOptionSQL'], [attributeId])
                optionId = self.mageCursor.lastrowid
            for storeId, optionValue in options.items():
                self.mageCursor.execute(self.queries['optionValueExistSQL'], [optionId, storeId])
                exist = self.mageCursor.fetchone()
                if exist[0] == 0:
                    self.mageCursor.execute(self.queries['insertOptionValueSQL'], [optionId, storeId, optionValue])
                elif exist[0] > 0 and updateExistingOption == True:
                    self.mageCursor.execute(self.queries['updateOptionValueSQL'], [optionValue, optionId, storeId])

            return
            return

    def getAttributeValue(self, entityTypeCode, attributeCode, entityId, storeId=0):
        attributeMetadata = self.getAttributeMetadata(attributeCode, entityTypeCode)
        if attributeMetadata is None:
            self.logger.info(('Attribute metadata is not found for {0}').format(attributeCode))
            return
        else:
            attributeId = attributeMetadata['attribute_id']
            if entityId and attributeMetadata['backend_type'] in ('varchar', 'text',
                                                                  'int', 'decimal',
                                                                  'datetime') and entityId != '':
                if entityTypeCode in ('catalog_category', 'catalog_product'):
                    getAttributeValueSQL = self.queries['getAttributeValueSQL'] + (' AND store_id = {0}').format(storeId)
                else:
                    getAttributeValueSQL = self.queries['getAttributeValueSQL']
                getAttributeValueSQL = getAttributeValueSQL.format(entityTypeCode, attributeMetadata['backend_type'])
                self.mageCursor.execute(getAttributeValueSQL, [attributeId, entityId])
                res = self.mageCursor.fetchone()
                value = None
                if res is not None:
                    value = res[0]
                if value is not None and attributeMetadata['frontend_input'] == 'select' and attributeMetadata['backend_type'] == 'int':
                    optionValue = self.getAttributeOptionValue(attributeId, value)
                    if optionValue is not None:
                        value = optionValue
                if value is not None and attributeMetadata['frontend_input'] == 'multiselect':
                    valueIdsList = [ v.strip() for v in value.split(',') ]
                    values = []
                    for v in valueIdsList:
                        vStr = self.getAttributeOptionValue(attributeId, v)
                        if vStr is not None:
                            values.append(vStr)

                    value = (',').join(values)
                return value
            return
            return

    def getAttributeOptionValue(self, attributeId, entityId, storeId=0):
        self.mageCursor.execute(self.queries['getAttributeOptionValueSQL'], [attributeId, entityId, storeId])
        item = self.mageCursor.fetchone()
        if item is not None:
            value = item[0]
            return value
        else:
            return
            return

    def getAttributesByEntityTypeAndAttributeSet(self, entityTypeCode, attributeSetName):
        self.mageCursor.execute(self.queries['getAttributesByEntityTypeAndAttributeSetSQL'], [
         entityTypeCode, attributeSetName])
        res = self.fetchCursorResultAsDict(self.mageCursor)
        attributes = {}
        for row in res:
            attributes[row['attribute_code']] = row

        return attributes

    def getAttributesByEntityType(self, entityTypeCode):
        self.mageCursor.execute(self.queries['getAttributesByEntityTypeSQL'], [
         entityTypeCode])
        res = self.fetchCursorResultAsDict(self.mageCursor)
        attributes = {}
        for row in res:
            attributes[row['attribute_code']] = row

        return attributes

    def getCustomerGroupCodeById(self, groupId):
        self.mageCursor.execute(self.queries['getCustomerGroupCodeByIdSQL'], [groupId])
        res = self.mageCursor.fetchone()
        if res is not None:
            customerGroupCode = res[0]
        else:
            customerGroupCode = ''
        return customerGroupCode

    def getCustomerGroupIdByCode(self, groupCode):
        self.mageCursor.execute(self.queries['getCustomerGroupIdByCodeSQL'], [groupCode])
        res = self.mageCursor.fetchone()
        if res is not None:
            customerGroupId = int(res[0])
        else:
            customerGroupId = 0
        return customerGroupId

    def getTaxClassIdByName(self, taxClassName, taxClassType):
        self.mageCursor.execute(self.queries['getTaxClassIdByNameSQL'], [taxClassName, taxClassType])
        res = self.mageCursor.fetchone()
        if res is not None:
            taxClassId = int(res[0])
        else:
            taxClassId = 0
        return taxClassId


class MagentoApiMessagePlugin(MessagePlugin):

    def marshalled(self, context):
        body = context.envelope.getChild('Body')
        call = context.envelope.childAtPath('Body/call')
        if call:
            resourcePath = call.getChild('resourcePath')
            if resourcePath is not None and (str(resourcePath.getText()) == 'sales_order_shipment.create' or str(resourcePath.getText()) == 'sales_order_invoice.create'):
                args = call.getChild('args')
                if args:
                    item = args.getChild('item')
                    if item:
                        item.set('xsi:type', 'http://xml.apache.org/xml-soap:Map')
        return context


class MagentoApi(object):

    def __init__(self, mageConf):
        if 'logFileName' not in mageConf or mageConf['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            updatedAt = '%s-%s-%s-%s-%s-%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
            logFileName = 'log/magento_api_call_' + updatedAt + '.' + 'log'
            mageConf['logFileName'] = logFileName
        self.logger = Logger('MagentoApi', mageConf['logFileName'])
        self.mageConf = mageConf
        self.mageApiSessionId = ''
        self.mageApiClient = None
        self.loginMagentoApi()
        return

    def __del__(self):
        self.logoutMagentoApi()
        self.logger.info('End Magento API session')

    def loginMagentoApi(self):
        if self.mageApiSessionId == '':
            try:
                suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
                imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
                imp.filter.add('urn:Magento')
                doctor = ImportDoctor(imp)
                if 'apiHttpUsername' in self.mageConf:
                    self.mageApiClient = Client(self.mageConf['mage_wsdl'], doctor=doctor, plugins=[MagentoApiMessagePlugin()], username=self.mageConf['apiHttpUsername'], password=self.mageConf['apiHttpPassword'])
                else:
                    self.mageApiClient = Client(self.mageConf['mage_wsdl'], doctor=doctor, plugins=[MagentoApiMessagePlugin()])
                self.mageApiSessionId = self.mageApiClient.service.login(self.mageConf['apiuser'], self.mageConf['apikey'])
                self.logger.info('Login Magento API')
            except Exception as e:
                log = ('Failed to login Magento API with error: {0}').format(str(e))
                self.logger.exception(log)
                raise

    def logoutMagentoApi(self):
        if self.mageApiSessionId != '' and self.mageApiClient is not None:
            try:
                result = self.mageApiClient.service.endSession(self.mageApiSessionId)
            except Exception as e:
                log = ('Failed to logout Magento API with error: {0}').format(str(e))
                self.logger.exception(log)
                raise

        return

    def createMagentoShipment(self, mOrderIncId, itemsQty, comment, emailFlag=1, includeComment=0):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            mShipmentIncId = self.mageApiClient.service.salesOrderShipmentCreate(self.mageApiSessionId, mOrderIncId, itemsQty, comment, emailFlag, includeComment)
            log = ('m_order_inc_id/m_shipment_inc_id : {0}/{1}').format(mOrderIncId, mShipmentIncId)
            self.logger.info(log)
            return str(mShipmentIncId)
        except Exception as e:
            log = ('Failed to create shipment for order {0} with error {1}').format(mOrderIncId, str(e))
            self.logger.exception(log)
            return ''

    def createMagentoInvoice(self, mOrderIncId, itemsQty, comment='', emailFlag=1, includeComment=0):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            mInvoiceIncId = self.mageApiClient.service.salesOrderInvoiceCreate(self.mageApiSessionId, mOrderIncId, itemsQty, comment, emailFlag, includeComment)
            log = ('m_order_inc_id/m_invoice_inc_id : {0}/{1}').format(mOrderIncId, mInvoiceIncId)
            self.logger.info(log)
            return str(mInvoiceIncId)
        except Exception as e:
            log = ('Failed to create invoice for order {0} with error {1}').format(mOrderIncId, str(e))
            self.logger.exception(log)
            return ''

    def captureMagentoInvoice(self, mInvoiceIncId):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.salesOrderInvoiceCapture(self.mageApiSessionId, mInvoiceIncId)
            log = ('capture invoice {0}').format(mInvoiceIncId)
            self.logger.info(log)
            return str(mInvoiceIncId)
        except Exception as e:
            log = ('Failed to capture invoice {0} with error {1}').format(mInvoiceIncId, str(e))
            self.logger.exception(log)
            return ''

    def generateTrackComment(self, carrier='custom', title='', tracking=''):
        if tracking is None:
            tracking = ''
        if title is None:
            title = ''
        if carrier is None:
            carrier = ''
        comment = ('|').join([carrier, title, tracking])
        return comment

    def catalogCategoryAssignProduct(self, productId, categoryId):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.catalogCategoryAssignProduct(self.mageApiSessionId, categoryId, productId)
            log = ('Assigned CategoryID/ProductId : {0}/{1}').format(categoryId, productId)
            self.logger.info(log)
        except Exception as e:
            log = ('Failed to assign CategoryID/ProductId : {0}/{1} with error {2}').format(categoryId, productId, str(e))
            self.logger.exception(log)

    def catalogCategoryRemoveProduct(self, productId, categoryId):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.catalogCategoryRemoveProduct(self.mageApiSessionId, categoryId, productId)
            log = ('Remove CategoryID/ProductId : {0}/{1}').format(categoryId, productId)
            self.logger.info(log)
        except Exception as e:
            log = ('Failed to Remove CategoryID/ProductId : {0}/{1} with error {2}').format(categoryId, productId, str(e))
            self.logger.exception(log)

    def catalogProductAttributeMediaCreate(self, product, data, storeView=0, identifierType='sku'):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.catalogProductAttributeMediaCreate(self.mageApiSessionId, product, data, storeView, identifierType)
            log = ('Image created sku/types/media_url : {0}/{1}/{2}').format(product, data['types'], result)
            self.logger.info(log)
            return result
        except Exception as e:
            log = ('Image failed to created sku/types : {0}/{1} with error {2}').format(product, data['types'], e)
            self.logger.exception(log)
            return

    def createSalesOrderCreditmemo(self, mOrderIncId, creditMemoData, comment='', notifyCustomer=1, includeComment=0, refundToStoreCreditAmount='0'):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.salesOrderCreditmemoCreate(self.mageApiSessionId, mOrderIncId, creditMemoData, comment, notifyCustomer, includeComment, refundToStoreCreditAmount)
            log = ('order_increment_id/credit_memo_inc_id : {0}/{1}').format(mOrderIncId, result)
            self.logger.info(log)
            return result
        except Exception as e:
            log = ('Failed to create credit memo for order: {0} with error {1}').format(mOrderIncId, e)
            self.logger.exception(log)
            return

    def addSalesOrderComment(self, mOrderIncId, orderStatus, comment='', notifyCustomer=0):
        if self.mageApiSessionId == '':
            self.loginMagentoApi()
        try:
            suds.bindings.binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
            result = self.mageApiClient.service.salesOrderAddComment(self.mageApiSessionId, mOrderIncId, orderStatus, comment, notifyCustomer)
            log = ('order_increment_id {0} add comment : {1}').format(mOrderIncId, comment)
            self.logger.info(log)
            return result
        except Exception as e:
            log = ('Failed to add comment for order: {0} with error {1}').format(mOrderIncId, e)
            self.logger.exception(log)
            return


class Magento2RestApi(object):

    def __init__(self, mageConf):
        if 'logFileName' not in mageConf or mageConf['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            updatedAt = '%s-%s-%s-%s-%s-%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
            logFileName = 'magento_rest_api_' + updatedAt + '.' + 'log'
            mageConf['logFileName'] = logFileName
        self.logger = Logger('Magento2Rest', mageConf['logFileName'])
        self._mageConf = mageConf
        self._endpoint = mageConf['restApiEndpoint']
        self._restApiEndpoints = {'createShipment': '/V1/shipment/', 'createShipmentTrack': '/V1/shipment/track/', 
           'createCategory': '/V1/categories/', 
           'linkCatalogCategory': '/V1/categories/{entityId}/products', 
           'getProductData': '/V1/products/{entityId}', 
           'updateProductData': '/V1/products/{entityId}', 
           'getCategoryData': '/V1/categories/', 
           'getOrderById': '/V1/orders/{entityId}', 
           'createInvoice': '/V1/invoices/', 
           'captureInvoice': '/V1/invoices/{entityId}/capture'}
        self.getAuthentication()
        self.getHeaders()

    def getAuthentication(self):
        self._auth = None
        if 'apiHttpUsername' in self._mageConf and self._mageConf['apiHttpUsername'] != '':
            username = self._mageConf['apiHttpUsername']
            password = self._mageConf['apiHttpPassword']
            self._auth = HTTPBasicAuth(username, password)
        return

    def getHeaders(self):
        self._headers = {'Authorization': 'Bearer ' + self._mageConf['restApiAccessToken'], 'Accept': 'application/json', 
           'Content-Type': 'application/json'}

    def getRequest(self, endpoint, entityId=None, params={}):
        url = self._endpoint + self._restApiEndpoints[endpoint]
        if entityId is not None:
            url = url.format(entityId=entityId)
        print url
        response = requests.get(url, auth=self._auth, headers=self._headers, params=params)
        if response.status_code == 200:
            return response
        else:
            print response.url
            self.logger.error(response.content)
            raise Exception(response.content)
            return
            return

    def postRequest(self, endpoint, payload, entityId=None, method='post'):
        headers = {'Content-type': 'application/json;charset=utf-8'}
        url = self._endpoint + self._restApiEndpoints[endpoint]
        if entityId is not None:
            url = url.format(entityId=entityId)
        if method == 'put':
            response = requests.put(url, data=json.dumps(payload), headers=self._headers, auth=self._auth)
        else:
            response = requests.post(url, data=json.dumps(payload), headers=self._headers, auth=self._auth)
        if response.status_code in (200, 201):
            return response
        else:
            self.logger.error(response.content)
            raise Exception(response.content)
            return
            return

    def createShipment(self, shipmentData):
        response = self.postRequest('createShipment', shipmentData)
        return json.loads(response.content)

    def createShipmentTrack(self, trackData):
        response = self.postRequest('createShipmentTrack', trackData)
        return json.loads(response.content)

    def createCategory(self, categoryData):
        response = self.postRequest('createCategory', categoryData)
        return json.loads(response.content)

    def linkCatalogCategory(self, productCategoryData, categoryId):
        response = self.postRequest('linkCatalogCategory', productCategoryData, categoryId)
        return json.loads(response.content)

    def getProductData(self, sku):
        response = self.getRequest('getProductData', sku)
        return json.loads(response.content)

    def updateProductData(self, sku, productData):
        response = self.postRequest('updateProductData', productData, sku, 'put')
        return json.loads(response.content)

    def getCategoryData(self, depth, parentId):
        params = {'rootCategoryId': parentId, 'depth': depth}
        response = self.getRequest('getCategoryData', params=params)
        return json.loads(response.content)

    def createInvoice(self, invoiceData):
        response = self.postRequest('createInvoice', invoiceData)
        print response
        return json.loads(response.content)

    def getOrderById(self, orderId):
        response = self.getRequest('getOrderById', orderId)
        return json.loads(response.content)

    def captureInvoice(self, invoiceId):
        response = self.postRequest('captureInvoice', {}, invoiceId)
        print response
        return json.loads(response.content)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    mage_conf = {'host': '192.168.119.93', 'user': 'mkpl', 
       'password': '12345abc', 
       'db': 'ce_m2e', 
       'mage_wsdl': 'http://mkpl.silksoftware.net/index.php/api/v2_soap/?wsdl', 
       'apiuser': 'sapb1_dst', 
       'apikey': 'dev4silk', 
       'logFileName': 'mage_dst.log', 
       'projectName': 'M2E', 
       'storeCode': 'silk', 
       'apiHttpUsername': 'silkdev', 
       'apiHttpPassword': 'devsitego'}
    mageApi = MagentoApi(mage_conf)
    mOrderIncId = '100031969'
    comment = 'custom|Fedex Ground|TEST00001'
    items = [{'qty': '1.0', 'order_item_id': '56128'}]
    params = mageApi.mageApiClient.factory.create('{http://schemas.xmlsoap.org/soap/encoding/}Array')
    params = {'item': items}
    mShipmentIncId = mageApi.createMagentoShipment(mOrderIncId, params, comment, 1, 0)
    print mShipmentIncId