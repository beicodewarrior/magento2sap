# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoCustomer.py
# Compiled at: 2016-06-18 20:45:10
__author__ = 'sandy.tu'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import json, csv
from MagentoCommon import MagentoCore
from MagentoEntity import MagentoEntity
from utility.DSTControl import DSTControl

class MagentoCustomer(MagentoCore):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoCore.__init__(self, mageConf, mageConn)
        self.mageApi = mageApi
        self.dstCursor = dstCursor
        self.dstControl = DSTControl(dstCursor)
        queries = {'getCustomersSQL': '\n                SELECT * FROM customer_entity\n                WHERE updated_at >= %s\n                ORDER BY entity_id DESC LIMIT %s\n            ', 
           'getCustomerByIdsSQL': '\n                SELECT * FROM customer_entity\n                WHERE entity_id in (%s)\n                ORDER BY entity_id DESC\n            ', 
           'getCustomerAddressesSQL': '\n                SELECT * FROM customer_address_entity WHERE parent_id = %s\n            ', 
           'insertMCustomerSQL': '\n                REPLACE INTO m_customer\n                (id, email, website_code, m_cust_inc_id, create_at, m_json_data, sync_status, sync_dt, sync_notes)\n                VALUES\n                (%s, %s, %s, %s, now(), %s, %s, now(), %s)\n            ', 
           'getCustomerGroupCodeByIdSQL': 'SELECT customer_group_code FROM customer_group WHERE customer_group_id = %s', 
           'getCustomerGroupIdByCodeSQL': 'SELECT customer_group_id FROM customer_group WHERE customer_group_code = %s', 
           'getRegionCodeByIdSQL': '\n                SELECT code FROM directory_country_region WHERE region_id = %s\n            ', 
           'getCompanyByCodeSQL': '\n                SELECT a.id FROM silk_b2bcompany a\n                INNER JOIN store_website b on a.website_id = b.website_id\n                WHERE a.company_code = %s and b.code = %s\n            ', 
           'getCustomerByEmailSQL': '\n                SELECT\n                a.entity_id, a.email, a.group_id, b.customer_group_code, c.code as website_code, d.code as store_code\n                FROM customer_entity a\n                INNER JOIN customer_group b ON group_id = b.customer_group_id\n                INNER JOIN store_website c on a.website_id = c.website_id\n                INNER JOIN store d on a.store_id = d.store_id\n                WHERE a.email = %s AND\n                c.code = %s;\n            ', 
           'isCustomerInCompanySQL': '\n                SELECT id FROM silk_b2bcompany_account\n                WHERE company_id = %s AND\n                customer_id = %s\n            ', 
           'insertCompanyAccountSQL': '\n                INSERT INTO silk_b2bcompany_account\n                (company_id,customer_id,role_id,status,updated_at)\n                VALUES\n                (%s,%s,%s,%s,now())\n            ', 
           'updateCompanyAccountSQL': '\n                UPDATE silk_b2bcompany_account\n                SET role_id = %s ,\n                status = %s,\n                updated_at = now()\n                WHERE id = %s\n            ', 
           'updateCustomerFlatGridAddressSQL': '\n                UPDATE customer_grid_flat T\n                INNER JOIN (\n                select\n                ce.entity_id,\n                concat(ifnull(billing.street,"") , ifnull(billing.city,"") , ifnull(billing.region,"") , ifnull(billing.postcode,"")) as billing_full,\n                billing.firstname as billing_firstname,\n                billing.lastname as billing_lastname,\n                billing.telephone as billing_telephone,\n                billing.postcode as billing_postcode,\n                billing.country_id as billing_country_id,\n                billing.region as billing_region,\n                billing.street as billing_street,\n                billing.city as billing_city,\n                billing.fax as billing_fax ,\n                billing.vat_id as billing_vat_id,\n                billing.company as billing_company,\n                concat(ifnull(shipping.street,"") , ifnull(shipping.city,"") , ifnull(shipping.region,"") , ifnull(shipping.postcode,"")) as shipping_full\n                from customer_entity ce\n                left join customer_address_entity billing on ce.default_billing = billing.entity_id\n                left join customer_address_entity shipping on ce.default_shipping = shipping.entity_id\n                where ce.entity_id = %s\n                ) AS S ON T.entity_id = S.entity_id\n                SET\n                T.billing_full = S.billing_full,\n                T.billing_firstname = S.billing_firstname ,\n                T.billing_lastname = S.billing_lastname ,\n                T.billing_telephone = S.billing_telephone ,\n                T.billing_postcode = S.billing_postcode ,\n                T.billing_country_id = S.billing_country_id ,\n                T.billing_region = S.billing_region ,\n                T.billing_street = S.billing_street ,\n                T.billing_city = S.billing_city ,\n                T.billing_fax = S.billing_fax ,\n                T.billing_vat_id = S.billing_vat_id ,\n                T.billing_company = S.billing_company ,\n                T.shipping_full = S.shipping_full\n                WHERE T.entity_id = %s\n            ', 
           'updateCustomerFlatGridSQL': "\n                UPDATE customer_grid_flat T\n                INNER JOIN customer_entity S ON T.entity_id = S.entity_id AND T.entity_id = %s\n                SET T.name = ifnull(concat(S.firstname, ' ', S.lastname),T.name),\n                T.email = S.email,\n                T.group_id = S.group_id,\n                T.website_id = S.website_id,\n                T.created_in = S.created_in,\n                T.dob = S.dob,\n                T.gender = S.gender,\n                T.taxvat = S.taxvat\n                WHERE T.entity_id = %s\n            ", 
           'disableCompanyByIdSQL': '\n                UPDATE silk_b2bcompany SET status = 0 WHERE id = %s\n            ', 
           'disableCompanyAccountSQL': '\n                UPDATE silk_b2bcompany_account SET status = 0 WHERE company_id = %s\n            '}
        self.queries = dict(self.queries, **queries)
        self.dstQueries = {'setMCustomerErpDataSQL': '\n                UPDATE m_customer\n                SET e_json_data = %s\n                WHERE id = %s\n            ', 
           'isMCustomerExistSQL': '\n                SELECT count(*) FROM m_customer WHERE id = %s\n            '}
        self.excludeAttributes = [
         'entity_id', 'email']
        self.needCleanAttributes = []
        self.eCustomerAttributesMap = {}
        self._exportMCustomerAttributes = []
        self._exportMCustomerAddressAttributes = []
        self._eCustomerAttributesMap = {}
        self._eCustomerAddressAttributesMap = {}
        self._eCompanyAttributesMap = {}
        self._customerStaticAttributes = [
         'website_id', 'email', 'group_id', 'increment_id', 'store_id',
         'created_at', 'updated_at', 'is_active',
         'created_in', 'prefix', 'firstname', 'middlename', 'lastname', 'suffix',
         'dob', 'default_billing', 'default_shipping', 'gender']
        self._customerGridFlatAttributes = [
         'entity_id', 'name', 'email', 'group_id', 'created_at', 'created_in',
         'dob', 'gender', 'website_id']
        self._customerAddressStaticAttributes = [
         'increment_id', 'parent_id', 'created_at', 'updated_at', 'city',
         'company', 'country_id', 'fax', 'firstname', 'middlename', 'lastname',
         'postcode', 'prefix', 'region', 'region_id', 'street', 'suffix',
         'telephone']
        self._companyStaticAttributes = [
         'company_code', 'status', 'company_name', 'group_id', 'company_description',
         'payment_info', 'company_url', 'website_id', 'created_at',
         'updated_at', 'shipping_info']
        self._mCompanyDefaults = {'status': '1', 
           'website_code': 'base', 
           'created_at': self.getNowStr('UTC'), 
           'updated_at': self.getNowStr('UTC'), 
           'action': 'addOrUpdate'}
        self._customerDefaults = {'website_code': 'base', 
           'store_code': 'default', 
           'action': 'InsertOrUpdate'}
        self._createNewCompany = True
        self._contactUniqeAttribute = 'unique_id'
        self._contactRoleAttribute = 'U_Role'
        self._contactStatusAttribute = 'Status'
        self._attributeValuesMatrix = {}
        self._eCustomerAddressUniqueKey = 'increment_id'
        self._companyAccountRoleMatrix = {'Admin': 0, 
           'Manager': 1, 
           'Salesperson': 2}
        self._companyRequiredAttributes = [
         'company_code', 'status', 'company_name', 'group_id',
         'payment_info', 'website_id', 'created_at',
         'updated_at', 'shipping_info']
        self._customerRequiredAttributes = [
         'website_id', 'email', 'group_id', 'store_id',
         'created_in', 'firstname', 'lastname']
        self._addressRequiredAttributes = [
         'city',
         'country_id', 'firstname', 'lastname',
         'postcode', 'street', 'telephone']
        self._createNewCustomer = False
        self._defaultCustomerGroupId = 1
        self._customerIgnoreSyncStatus = 'I'

    def getNowStr(self, timezone=''):
        if timezone == 'UTC':
            now = datetime.utcnow()
        else:
            now = datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        return nowstr

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
            customerGroupId = self._defaultCustomerGroupId
        return customerGroupId

    def getRegionCodeById(self, regionId):
        self.mageCursor.execute(self.queries['getRegionCodeByIdSQL'], [regionId])
        res = self.mageCursor.fetchone()
        regionCode = None
        if res is not None and len(res) > 0:
            regionCode = res[0]
        return regionCode

    def processMAddressExt(self, address, customerId):
        pass

    def getCustomerAddressesByCustomerId(self, customerId):
        customerAddressAttributes = self.getAttributesByEntityType('customer_address')
        if len(self._exportMCustomerAddressAttributes) > 0:
            needExportAttributes = list(set(self._exportMCustomerAddressAttributes) & set(customerAddressAttributes.keys()))
        else:
            needExportAttributes = customerAddressAttributes
        self.mageCursor.execute(self.queries['getCustomerAddressesSQL'], [customerId])
        addresses = self.fetchCursorResultAsDict(self.mageCursor)
        for address in addresses:
            for attributeCode, attributeValue in address.items():
                if attributeValue is not None:
                    address[attributeCode] = str(address[attributeCode])

            for attributeCode in needExportAttributes:
                if attributeCode in address:
                    continue
                attributeValue = self.getAttributeValue('customer_address', attributeCode, address['entity_id'])
                if attributeValue is not None:
                    attributeValue = str(attributeValue)
                address[attributeCode] = attributeValue

            if 'region_id' in address:
                address['region_id'] = self.getRegionCodeById(address['region_id'])
            self.processMAddressExt(address, customerId)

        return addresses

    def getMCustomers(self, lastCutoffDt, limits=0, customerIds=[]):
        customerAttributes = self.getAttributesByEntityType('customer')
        if len(self._exportMCustomerAttributes) > 0:
            needExportAttributes = list(set(self._exportMCustomerAttributes) & set(customerAttributes.keys()))
        else:
            needExportAttributes = customerAttributes
        if len(customerIds) > 0:
            formatStrings = (',').join(['%s'] * len(customerIds))
            sql = self.queries['getCustomerByIdsSQL'] % formatStrings
            self.mageCursor.execute(sql, customerIds)
        else:
            self.mageCursor.execute(self.queries['getCustomersSQL'], [lastCutoffDt, limits])
        customers = self.fetchCursorResultAsDict(self.mageCursor)
        allCustomers = []
        cnt = 1
        for customer in customers:
            for attributeCode, attributeValue in customer.items():
                if attributeValue is not None:
                    customer[attributeCode] = str(customer[attributeCode])

            customer['website_code'] = self.getWebsiteCodeById(customer['website_id'])
            customer['customer_group'] = self.getCustomerGroupCodeById(customer['group_id'])
            for attributeCode in needExportAttributes:
                if attributeCode in customer:
                    continue
                attributeValue = self.getAttributeValue('customer', attributeCode, customer['entity_id'])
                if attributeValue is not None:
                    attributeValue = str(attributeValue)
                customer[attributeCode] = attributeValue

            customer['addresses'] = self.getCustomerAddressesByCustomerId(customer['entity_id'])
            allCustomers.append(customer)
            cnt = cnt + 1

        return allCustomers

    def exportMagentoCustomerExt(self, mCustomer):
        pass

    def convertMCustomerToErpData(self, mCustomer):
        return ''

    def setMCustomerErpData(self, mCustomer):
        erpData = self.convertMCustomerToErpData(mCustomer)
        self.dstCursor.execute(self.dstQueries['setMCustomerErpDataSQL'], [erpData, mCustomer['entity_id']])

    def isCustomerExistedInDstById(self, customerId):
        self.dstCursor.execute(self.dstQueries['isMCustomerExistSQL'], [customerId])
        res = self.dstCursor.fetchone()
        exist = False
        if res is not None and len(res) > 0 and int(res[0]) > 0:
            exist = True
        return exist

    def syncMagentoCustomersToDst(self, lastCutoffDt='', limits=0, customerIds=[]):
        syncResult = {'sync_status': 'F', 
           'sync_notes': ''}
        try:
            start = self.getNowStr()
            newCutoffDt = self.getNowStr('UTC')
            task = 'customer_mage_to_dst'
            if len(customerIds) > 0:
                task = 'cust_mage_to_dst_by_ids'
                lastCutoffDt = self.dstControl.defaultCutoffDt
            if lastCutoffDt == '':
                lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
            mCustomers = self.getMCustomers(lastCutoffDt, limits, customerIds)
            lastCutoffEntityId = None
            for mCustomer in mCustomers:
                customerId = mCustomer['entity_id']
                email = mCustomer['email']
                websiteCode = mCustomer['website_code']
                self.exportMagentoCustomerExt(mCustomer)
                mJsonData = json.dumps(mCustomer)
                mCustomer['m_json_data'] = mJsonData
                syncStatus = 'N'
                syncNotes = 'Magento to DST'
                if customerId > lastCutoffEntityId:
                    lastCutoffEntityId = customerId
                self.dstCursor.execute(self.queries['insertMCustomerSQL'], [
                 customerId, email, websiteCode, customerId, mJsonData, syncStatus, syncNotes])
                self.logger.info(('{0} Magento to DST').format(email))

            if lastCutoffEntityId:
                syncStatus = 'O'
                lastCutoffDt = newCutoffDt
                lastStartDt = start
                lastEndDt = self.getNowStr()
                syncNotes = 'Sync from Magento to DST'
                self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
            else:
                syncStatus = 'I'
                syncNotes = 'No customer needs to sync'
            syncResult['sync_status'] = syncStatus
            syncResult['sync_notes'] = syncNotes
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def exportCustomersToJson(self, fileName='', lastCutoffDt='2015-01-01', limits=1):
        mCustomers = self.getMCustomers(lastCutoffDt, limits)
        jsonFile = open(fileName, 'wb')
        json.dump(mCustomers, jsonFile, sort_keys=True, indent=4, separators=(',',
                                                                              ': '))
        cnt = len(mCustomers)
        self.logger.info(('{0} customers saved to {1}').format(cnt, fileName))
        return mCustomers

    def preECustomerToMCustomer(self, eCustomer):
        return eCustomer

    def eCustomerToMCustomer(self, eCustomer, eCustomerAttributesMap={}, eCustomerAddressAttributesMap={}):
        eCustomer = self.preECustomerToMCustomer(eCustomer)
        mCustomer = {}
        if type(eCustomer) == str or type(eCustomer) == unicode:
            eCustomerObject = json.loads(eCustomer)
        else:
            eCustomerObject = eCustomer
        if len(eCustomerAttributesMap) == 0:
            eCustomerAttributesMap = self._eCustomerAttributesMap
        for k, v in eCustomerAttributesMap.items():
            if v in eCustomerObject:
                if v == 'addresses':
                    pass
                elif eCustomerObject[v] is not None:
                    if k in self._attributeValuesMatrix and eCustomerObject[v] in self._attributeValuesMatrix[k]:
                        mCustomer[k] = self._attributeValuesMatrix[k][eCustomerObject[v]]
                    elif type(eCustomerObject[v]) == unicode:
                        mCustomer[k] = eCustomerObject[v]
                    else:
                        mCustomer[k] = str(eCustomerObject[v])
                else:
                    mCustomer[k] = None

        mCustomer = self.setMCustomerDefault(mCustomer, 'website_code')
        mCustomer = self.setMCustomerDefault(mCustomer, 'store_code')
        mCustomer = self.setMCustomerDefault(mCustomer, 'action')
        if 'addresses' in eCustomerObject:
            mCustomer['addresses'] = eCustomerObject['addresses']
        else:
            mCustomer['addresses'] = []
        mCustomer = self.eCustomerToMCustomerExt(mCustomer, eCustomer, eCustomerAttributesMap, eCustomerAddressAttributesMap)
        return mCustomer

    def setMCustomerDefault(self, mCustomer, attributeCode):
        if attributeCode in self._customerDefaults:
            attributeDefaultValue = self._customerDefaults[attributeCode]
        else:
            attributeDefaultValue = ''
        if attributeCode in mCustomer:
            if mCustomer[attributeCode] is not None:
                if str(mCustomer[attributeCode]).strip() != '':
                    return mCustomer
                mCustomer[attributeCode] = attributeDefaultValue
            else:
                mCustomer[attributeCode] = attributeDefaultValue
        else:
            mCustomer[attributeCode] = attributeDefaultValue
        return mCustomer

    def eCustomerToMCustomerExt(self, mCustomer, eCustomer, eCustomerAttributesMap={}, eCustomerAddressAttributesMap={}):
        return mCustomer

    def preEcustomerAddressToMCustomerAddress(self, eCustomerAddress):
        return eCustomerAddress

    def eCustomerAddressToMCustomerAddress(self, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap={}):
        eCustomerAddress = self.preEcustomerAddressToMCustomerAddress(eCustomerAddress)
        mCustomerAddress = {}
        if type(eCustomerAddress) == str or type(eCustomerAddress) == unicode:
            eCustomerAddressObject = json.loads(eCustomerAddress)
        else:
            eCustomerAddressObject = eCustomerAddress
        if len(eCustomerAddressAttributesMap) == 0:
            eCustomerAddressAttributesMap = self._eCustomerAddressAttributesMap
        for k, v in eCustomerAddressAttributesMap.items():
            if v in eCustomerAddressObject:
                if eCustomerAddressObject[v] is not None:
                    if type(eCustomerAddressObject[v]) == unicode:
                        mCustomerAddress[k] = eCustomerAddressObject[v]
                    else:
                        mCustomerAddress[k] = str(eCustomerAddressObject[v])
                else:
                    mCustomerAddress[k] = None

        mCustomerAddress = self.eCustomerAddressToMCustomerAddressExt(mCustomerAddress, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap)
        return mCustomerAddress

    def eCustomerAddressToMCustomerAddressExt(self, mCustomerAddress, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap):
        return mCustomerAddress

    def deleteCustomerAddressByCustomerId(self, customerId):
        pass

    def getCustomerByEmail(self, email, websiteCode, storeCode):
        self.mageCursor.execute(self.queries['getCustomerByEmailSQL'], [email, websiteCode])
        res = self.mageCursor.fetchone()
        customer = {'entity_id': None, 
           'email': email, 
           'group_id': None, 
           'customer_group': None, 
           'website_code': websiteCode, 
           'store_code': websiteCode}
        if res is not None:
            customer = {'entity_id': res[0], 'email': res[1], 
               'group_id': res[2], 
               'customer_group': res[3], 
               'website_code': res[4], 
               'store_code': res[5]}
        return customer

    def isValueProtected(self, customerId, k):
        return False

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

    def checkRequiredData(self, requiredAttributes, data):
        flag = True
        for requiredAttribute in requiredAttributes:
            if requiredAttribute not in data or data[requiredAttribute] is None or str(data[requiredAttribute]) == '':
                flag = False
                self.logger.warning(('Required Attribute {0} is not in {1}').format(requiredAttribute, data))
                break

        return flag

    def importCustomer(self, eCustomer, eCustomerAttributesMap={}, createNew=None):
        if createNew == None:
            createNew = self._createNewCustomer
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        mCustomer = self.eCustomerToMCustomer(eCustomer, eCustomerAttributesMap)
        email = mCustomer['email']
        websiteCode = mCustomer['website_code']
        storeCode = mCustomer['store_code']
        syncResult = {'action': '', 
           'email': email, 
           'm_customer_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento', 
           'm_customer_data': json.dumps(mCustomer)}
        try:
            existingCustomer = self.getCustomerByEmail(email, websiteCode, storeCode)
            action = mCustomer['action']
            mCustomerId = existingCustomer['entity_id']
            mCustomer['id'] = mCustomerId
            if action == 'delete':
                self.deleteCustomerById(mCustomerId, mCustomer)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Delete customer {0} from website {1}').format(email, websiteCode)
                return syncResult
            staticAttributeValues = {}
            for attributeCode in self._customerStaticAttributes:
                if attributeCode in mCustomer:
                    staticAttributeValues[attributeCode] = mCustomer[attributeCode]

            if (mCustomerId == 0 or mCustomerId is None) and createNew == True:
                hasAllRequiredData = self.checkRequiredData(self._customerRequiredAttributes, staticAttributeValues)
                if hasAllRequiredData == False:
                    syncResult['action'] = action
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = ('Failed to create customer {0} from website {1}').format(email, websiteCode)
                    syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n Not all required attributes {0} are in source').format(self._customerRequiredAttributes)
                    return syncResult
                insertSQL, insertValues = self.getInsertSqlnValues('customer_entity', staticAttributeValues)
                self.mageCursor.execute(insertSQL, insertValues)
                mCustomerId = self.mageCursor.lastrowid
                mCustomer['id'] = mCustomerId
                syncResult['action'] = 'insert'
                if mCustomerId == 0 or mCustomerId is None:
                    log = ('Failed to create new customer: {0}').format(email)
                    self.logger.info(log)
                    mCustomer['action'] = 'insert'
                    syncResult['action'] = mCustomer['action']
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = log
                    return syncResult
            elif (mCustomerId == 0 or mCustomerId is None) and createNew == False:
                syncResult['action'] = ''
                log = ("Customer: {0} does not existed. But it's config to not create automatically!").format(email)
                self.logger.info(log)
                syncResult['action'] = 'ignore'
                syncResult['sync_status'] = self._customerIgnoreSyncStatus
                syncResult['sync_notes'] = log
                return syncResult
            else:
                mCustomer['action'] = 'update'
                updateSQL, updateValues = self.getUpdateSqlnValues('customer_entity', staticAttributeValues, {'entity_id': mCustomerId})
                self.mageCursor.execute(updateSQL, updateValues)

            customerGridInsertColumns = {}
            customerGridUpdateColumns = {}
            for attributeCode in self._customerGridFlatAttributes:
                if attributeCode in mCustomer:
                    customerGridInsertColumns[attributeCode] = mCustomer[attributeCode]
                    if attributeCode not in ('created_at', ):
                        customerGridUpdateColumns[attributeCode] = mCustomer[attributeCode]

            customerGridInsertColumns['entity_id'] = mCustomerId
            customerGridInsertColumns['created_at'] = self.getNowStr('UTC')
            if 'firstname' in mCustomer and 'lastname' in mCustomer:
                name = mCustomer['firstname'] + ' ' + mCustomer['lastname']
                customerGridInsertColumns['name'] = name
                customerGridUpdateColumns['name'] = name
            customerGridSQL, customerGridValues = self.getInsertOnDupldateUpdateSqlnValues('customer_grid_flat', customerGridInsertColumns, customerGridUpdateColumns)
            self.mageCursor.execute(customerGridSQL, customerGridValues)
            if 'addresses' in mCustomer:
                for address in mCustomer['addresses']:
                    addressSyncResult = self.importCustomerAddress(mCustomer, address)
                    syncResult['sync_notes'] = syncResult['sync_notes'] + addressSyncResult['sync_notes']

            self.updateCustomerFlatGrid(mCustomerId)
            log = ('Customer {0} {1} successfully').format(email, mCustomer['action'])
            syncResult['sync_status'] = 'O'
            self.logger.info(log)
            syncResult['m_customer_id'] = mCustomerId
            syncResult['sync_notes'] = log
            self.importCustomerExt(eCustomer, mCustomer, eCustomerAttributesMap)
        except Exception as e:
            log = ('Customer {0} {1} failed with error {2}').format(email, mCustomer['action'], str(e))
            self.logger.exception(log)
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = log

        return syncResult

    def importCustomerExt(self, eCustomer, mCustomer, eCustomerAttributesMap={}):
        pass

    def updateCustomerFlatGridAddress(self, mCustomerId):
        self.mageCursor.execute(self.queries['updateCustomerFlatGridAddressSQL'], [mCustomerId, mCustomerId])
        self.logger.info(('Update customer flat grid address for: {0}').format(mCustomerId))

    def updateCustomerFlatGrid(self, mCustomerId):
        self.mageCursor.execute(self.queries['updateCustomerFlatGridSQL'], [mCustomerId, mCustomerId])
        self.logger.info(('Update customer flat grid for: {0}').format(mCustomerId))

    def deleteCustomerAddressById(self, mCustomerAddressId, mCustomerAddress):
        pass

    def getCustomerAddressByUniqueValue(self, uniqueValues):
        sql = 'SELECT entity_id FROM customer_address_entity WHERE '
        values = []
        wheres = []
        for key, value in uniqueValues.items():
            wheres.append(key + ' = %s')
            values.append(value)

        where = (' and ').join(wheres)
        sql = sql + where
        self.mageCursor.execute(sql, values)
        res = self.mageCursor.fetchone()
        addressId = None
        if res is not None and len(res) > 0:
            addressId = int(res[0])
        return addressId

    def importCustomerAddress(self, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap={}):
        mCustomerAddress = self.eCustomerAddressToMCustomerAddress(mCustomer, eCustomerAddress, eCustomerAddressAttributesMap)
        if 'action' not in mCustomerAddress or mCustomerAddress['action'] == '':
            mCustomerAddress['action'] = 'insertOrUpdate'
        mCustomerId = mCustomer['id']
        uniqueValue = mCustomerAddress[self._eCustomerAddressUniqueKey]
        syncResult = {'action': '', 
           'unique_id': uniqueValue, 
           'customer_id': mCustomerId, 
           'm_address_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        try:
            mCustomerAddressId = self.getCustomerAddressByUniqueValue({self._eCustomerAddressUniqueKey: uniqueValue, 
               'parent_id': mCustomerId})
            action = mCustomerAddress['action']
            if action == 'delete':
                self.deleteCustomerAddressById(mCustomerAddressId, mCustomerAddress)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Delete customer address {0} ').format(uniqueValue)
                return syncResult
            staticAttributeValues = {}
            for attributeCode in self._customerAddressStaticAttributes:
                if attributeCode in mCustomerAddress:
                    staticAttributeValues[attributeCode] = mCustomerAddress[attributeCode]

            staticAttributeValues['parent_id'] = mCustomerId
            if mCustomerAddressId == 0 or mCustomerAddressId is None:
                hasAllRequiredData = self.checkRequiredData(self._addressRequiredAttributes, staticAttributeValues)
                if hasAllRequiredData == False:
                    syncResult['action'] = action
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = ('Failed to create address {0} from customer {1}').format(uniqueValue, mCustomerId)
                    syncResult['sync_notes'] = syncResult['sync_notes'] + ('\nNot all required attributes {0} are in the source.').format(self._addressRequiredAttributes)
                    return syncResult
                insertSQL, insertValues = self.getInsertSqlnValues('customer_address_entity', staticAttributeValues)
                self.mageCursor.execute(insertSQL, insertValues)
                mCustomerAddressId = self.mageCursor.lastrowid
                syncResult['action'] = 'insert'
                if mCustomerAddressId == 0:
                    log = ('Failed to create new address: {0}').format(uniqueValue)
                    self.logger.info(log)
                    mCustomerAddress['action'] = 'insert'
                    syncResult['action'] = mCustomerAddress['action']
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = log
                    return syncResult
            else:
                mCustomerAddress['action'] = 'update'
                updateSQL, updateValues = self.getUpdateSqlnValues('customer_address_entity', staticAttributeValues, {'entity_id': mCustomerAddressId})
                self.mageCursor.execute(updateSQL, updateValues)
            if 'is_default_billing' in mCustomerAddress and mCustomerAddress['is_default_billing'] == 1:
                self.setCustomerDefaultAddress(mCustomerId, mCustomerAddressId, 'default_billing')
            if 'is_default_shipping' in mCustomerAddress and mCustomerAddress['is_default_shipping'] == 1:
                self.setCustomerDefaultAddress(mCustomerId, mCustomerAddressId, 'default_shipping')
            log = ('Customer address {0} {1} successfully').format(uniqueValue, mCustomerAddress['action'])
            syncResult['sync_status'] = 'O'
            self.logger.info(log)
            syncResult['m_address_id'] = mCustomerAddressId
            syncResult['sync_notes'] = log
            self.importCustomerAddressExt(mCustomer, mCustomerAddress, eCustomerAddress, eCustomerAddressAttributesMap={})
        except Exception as e:
            log = ('Customer address {0} {1} failed with error {2}').format(uniqueValue, mCustomer['action'], str(e))
            self.logger.exception(log)
            syncResult['m_address_id'] = mCustomerAddressId
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = log

        return syncResult

    def importCustomerAddressExt(self, mCustomer, mCustomerAddress, eCustomerAddress, eCustomerAddressAttributesMap={}):
        pass

    def setCustomerDefaultAddress(self, mCustomerId, mCustomerAddressId, addressType):
        sql = ('\n            UPDATE customer_entity\n            SET {0} = %s\n            WHERE entity_id = %s\n        ').format(addressType)
        self.mageCursor.execute(sql, [mCustomerAddressId, mCustomerId])
        self.logger.info(('Assign address: customer_id/address_id/address_type: {0}/{1}/{2}').format(mCustomerId, mCustomerAddressId, addressType))
        self.updateCustomerFlatGridAddress(mCustomerId)

    def preECompanyToMCompany(self, eCompany):
        return eCompany

    def eCompanyToMCompany(self, eCompany, eCompanyAttributesMap={}):
        eCompany = self.preECompanyToMCompany(eCompany)
        mCompany = {}
        if type(eCompany) == str or type(eCompany) == unicode:
            eCompanyObject = json.loads(eCompany)
        else:
            eCompanyObject = eCompany
        if len(eCompanyAttributesMap) == 0:
            eCompanyAttributesMap = self._eCompanyAttributesMap
        for k, v in eCompanyAttributesMap.items():
            if v in eCompanyObject:
                if eCompanyObject[v] is not None:
                    if type(eCompanyObject[v]) == unicode:
                        mCompany[k] = eCompanyObject[v]
                    else:
                        mCompany[k] = str(eCompanyObject[v])
                else:
                    mCompany[k] = None

        mCompany['contacts'] = []
        if 'contacts' in eCompanyObject:
            adminContacts = {}
            managerContacts = {}
            salespersonContacts = {}
            for contact in eCompanyObject['contacts']:
                if contact[self._contactRoleAttribute] == 'Admin':
                    if 'addresses' in eCompanyObject:
                        contact['addresses'] = eCompanyObject['addresses']
                    adminContacts[contact[self._contactUniqeAttribute]] = contact
                if contact[self._contactRoleAttribute] == 'Manager':
                    managerContacts[contact[self._contactUniqeAttribute]] = contact
                if contact[self._contactRoleAttribute] == 'Salesperson':
                    salespersonContacts[contact[self._contactUniqeAttribute]] = contact

            contacts = []
            uniqeContacts = []
            for key, contact in adminContacts.items():
                if key not in uniqeContacts:
                    contacts.append(contact)
                    uniqeContacts.append(key)

            for key, contact in managerContacts.items():
                if key not in uniqeContacts:
                    contacts.append(contact)
                    uniqeContacts.append(key)

            for key, contact in salespersonContacts.items():
                if key not in uniqeContacts:
                    contacts.append(contact)
                    uniqeContacts.append(key)

            mCompany['contacts'] = contacts
        mCompany = self.setMCompanyDefault(mCompany, 'status')
        mCompany = self.setMCompanyDefault(mCompany, 'website_code')
        mCompany = self.setMCompanyDefault(mCompany, 'created_at')
        mCompany = self.setMCompanyDefault(mCompany, 'updated_at')
        groupId = self.getCustomerGroupIdByCode(mCompany['company_group'])
        mCompany['group_id'] = groupId
        mCompany = self.eCompanyToMCompanyExt(eCompanyObject, mCompany, eCompanyAttributesMap)
        return mCompany

    def eCompanyToMCompanyExt(self, eCompany, mCompany, eCompanyAttributesMap):
        return mCompany

    def getCompanyByCode(self, companyCode, websiteCode):
        self.mageCursor.execute(self.queries['getCompanyByCodeSQL'], [companyCode, websiteCode])
        res = self.mageCursor.fetchone()
        existingCompany = {'id': 0}
        if res is not None and len(res) > 0:
            existingCompany['id'] = int(res[0])
        return existingCompany

    def disableCompanyById(self, companyId, mCompany):
        self.mageCursor.execute(self.queries['disableCompanyByIdSQL'], [companyId])
        self.mageCursor.execute(self.queries['disableCompanyAccountSQL'], [companyId])
        self.logger.info(('Disable company id:{0} name:{1}').format(companyId, mCompany['company_name']))

    def importCompany(self, eCompany, eCompanyAttributesMap={}):
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        mCompany = self.eCompanyToMCompany(eCompany['e_data'], eCompanyAttributesMap)
        companyCode = mCompany['company_code']
        websiteCode = mCompany['website_code']
        syncResult = {'id': eCompany['id'], 
           'action': '', 
           'company_code': companyCode, 
           'm_company_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento', 
           'm_data': json.dumps(mCompany)}
        try:
            existingCompany = self.getCompanyByCode(companyCode, websiteCode)
            action = mCompany['action']
            if action == 'delete':
                self.deleteCompanyById(existingCompany['id'], mCompany)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Delete company {0} from website {1}').format(companyCode, websiteCode)
                return syncResult
            if action == 'ignore':
                syncResult['action'] = action
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = ('Ignore company {0} from website {1}').format(companyCode, websiteCode)
                return syncResult
            if action == 'disable':
                self.disableCompanyById(existingCompany['id'], mCompany)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Disable company {0} from website {1}').format(companyCode, websiteCode)
                return syncResult
            eavData = {}
            companyStaticAttributeValues = {}
            for attributeCode in self._companyStaticAttributes:
                if attributeCode in mCompany:
                    companyStaticAttributeValues[attributeCode] = mCompany[attributeCode]

            if existingCompany['id'] == 0 and self._createNewCompany == True:
                hasAllRequiredData = self.checkRequiredData(self._companyRequiredAttributes, companyStaticAttributeValues)
                if hasAllRequiredData == False:
                    syncResult['action'] = action
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = ('Failed to create company {0} from website {1}').format(companyCode, websiteCode)
                    syncResult['sync_notes'] = syncResult['sync_notes'] + ('\nNot all required attributes {0} are in the source.').format(self._companyRequiredAttributes)
                    return syncResult
                insertSQL, insertValue = self.getInsertSqlnValues('silk_b2bcompany', companyStaticAttributeValues)
                self.mageCursor.execute(insertSQL, insertValue)
                companyId = self.mageCursor.lastrowid
                mCompany['action'] = 'insert'
                if companyId == 0:
                    self.logger.info(('Failed to create new company: {0}').format(companyCode))
                    syncResult['action'] = mCustomer['action']
                    syncResult['sync_status'] = 'F'
                    return syncResult
            elif self._createNewCompany == False:
                log = ("Company: {0} does not existed. But it's config to not create automatically!").format(companyCode)
                self.logger.info(log)
                syncResult['action'] = ignore
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = log
                return syncResult
            else:
                mCompany['action'] = 'update'
                companyId = existingCompany['id']
                del companyStaticAttributeValues['created_at']
                updateSQL, updateValues = self.getUpdateSqlnValues('silk_b2bcompany', companyStaticAttributeValues, {'id': companyId})
                self.mageCursor.execute(updateSQL, updateValues)
                log = ('Update company {0} basic information').format(companyCode)

            for eContact in mCompany['contacts']:
                role = eContact[self._contactRoleAttribute]
                if role in self._companyAccountRoleMatrix:
                    role = self._companyAccountRoleMatrix[role]
                print role
                contactSyncResult = self.importCustomer(eContact, {}, True)
                mCustomerId = contactSyncResult['m_customer_id']
                if contactSyncResult['sync_status'] == 'F' or mCustomerId is None:
                    if role == 0:
                        syncResult['sync_status'] = 'F'
                        syncResult['sync_notes'] = syncResult['sync_notes'] + contactSyncResult['sync_notes']
                        return syncResult
                    syncResult['sync_notes'] = syncResult['sync_notes'] + contactSyncResult['sync_notes']
                    continue
                if self._contactStatusAttribute in eContact:
                    status = eContact[self._contactStatusAttribute]
                else:
                    status = 'Y'
                self.linkCustomerToCompany(companyId, mCustomerId, role, status)

            log = ('Company {0} {1} successfully').format(companyCode, mCompany['action'])
            syncResult['sync_status'] = 'O'
            self.logger.info(log)
            syncResult['m_company_id'] = companyId
            syncResult['sync_notes'] = syncResult['sync_notes'] + log
            self.importCompanyExt(eCompany, mCompany, eCompanyAttributesMap)
        except Exception as e:
            log = ('Company {0} {1} failed with error {2}').format(companyCode, mCompany['action'], str(e))
            self.logger.exception(log)
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = log

        return syncResult

    def importCompanyExt(self, eCompany, mCompany, eCompanyAttributesMap):
        pass

    def isCustomerInCompany(self, mCompanyId, mCustomerId):
        self.mageCursor.execute(self.queries['isCustomerInCompanySQL'], [mCompanyId, mCustomerId])
        accountId = None
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            accountId = int(res[0])
        return accountId

    def linkCustomerToCompany(self, mCompanyId, mCustomerId, role, status):
        accountId = self.isCustomerInCompany(mCompanyId, mCustomerId)
        if role in self._companyAccountRoleMatrix:
            role = self._companyAccountRoleMatrix[role]
        if status == 'Y':
            status = 1
        else:
            status = 0
        if accountId is None:
            self.mageCursor.execute(self.queries['insertCompanyAccountSQL'], [mCompanyId, mCustomerId, role, status])
        else:
            self.mageCursor.execute(self.queries['updateCompanyAccountSQL'], [role, status, accountId])
        return

    def setMCompanyDefault(self, mCompany, attributeCode):
        if attributeCode in self._mCompanyDefaults:
            attributeDefaultValue = self._mCompanyDefaults[attributeCode]
        else:
            attributeDefaultValue = ''
        if attributeCode in mCompany:
            if mCompany[attributeCode] is not None:
                if str(mCompany[attributeCode]).strip() != '':
                    return mCompany
                mCompany[attributeCode] = attributeDefaultValue
            else:
                mCompany[attributeCode] = attributeDefaultValue
        else:
            mCompany[attributeCode] = attributeDefaultValue
        return mCompany
# okay decompiling MagentoCustomer.pyc
