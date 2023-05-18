# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/MagentoCustomerAgent.py
# Compiled at: 2017-02-17 06:25:03
import sys
sys.path.insert(0, '..')
from MAGE2.MagentoCustomer import MagentoCustomer
from MAGE2.MagentoCommon import MagentoApi
import json

class MagentoCustomerAstro(MagentoCustomer):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoCustomer.__init__(self, mageConf, mageConn, mageApi, dstCursor)
        self._createNewCustomer = True
        self._eCustomerAttributesMap = {'website_code': 'website_code', 
           'email': 'email', 
           'group_id': 'ListName', 
           'firstname': 'FirstName', 
           'lastname': 'LastName'}
        self._eCustomerAddressAttributesMap = {'increment_id': 'unique_id', 
           'region_id': 'State', 
           'city': 'City', 
           'country_id': 'Country', 
           'postcode': 'ZipCode', 
           'street': 'Street', 
           'telephone': 'telephone'}

    def eCustomerToMCustomerExt(self, mCustomer, eCustomer, eCustomerAttributesMap={}, eCustomerAddressAttributesMap={}):
        groupId = self.getCustomerGroupIdByCode(mCustomer['group_id'])
        mCustomer['group_id'] = groupId
        mCustomer['store_id'] = 0
        mCustomer['created_in'] = 'Default Store View'
        mCustomer['website_code'] = 'base'
        mCustomer['website_id'] = 1
        if len(mCustomer['firstname'].strip()) <= 0:
            mCustomer['firstname'] = '(no first name)'
        if len(mCustomer['lastname'].strip()) <= 0:
            mCustomer['lastname'] = '(no last name)'
        return mCustomer

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
            else:
                if (mCustomerId == 0 or mCustomerId is None) and createNew == False:
                    syncResult['action'] = ''
                    log = ("Customer: {0} does not existed. But it's config to not create automatically!").format(email)
                    self.logger.info(log)
                    syncResult['action'] = 'ignore'
                    syncResult['sync_status'] = self._customerIgnoreSyncStatus
                    syncResult['sync_notes'] = log
                    return syncResult
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

    getRegionIdSQL = '\n        SELECT * FROM directory_country_region WHERE country_id = %s AND code = %s\n    '

    def eCustomerAddressToMCustomerAddressExt(self, mCustomerAddress, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap):
        mCustomerAddress['firstname'] = mCustomer['firstname']
        mCustomerAddress['lastname'] = mCustomer['lastname']
        if 'telephone' not in mCustomerAddress or mCustomerAddress['telephone'] is None or len(mCustomerAddress['telephone'].strip()) <= 0:
            mCustomerAddress['telephone'] = '000-000-0000'
        self.mageCursor.execute(self.getRegionIdSQL, [mCustomerAddress['country_id'], mCustomerAddress['region_id']])
        result = self.mageCursor.fetchone()
        if result is not None and len(result) > 0:
            mCustomerAddress['region_id'] = result[0]
        else:
            del mCustomerAddress['region_id']
        if eCustomerAddress['Address'] is not None:
            mCustomerAddress['company'] = eCustomerAddress['Address']
        return mCustomerAddress

    def importCustomerAddress(self, mCustomer, eCustomerAddress, eCustomerAddressAttributesMap={}):
        mCustomerAddress = self.eCustomerAddressToMCustomerAddress(mCustomer, eCustomerAddress, eCustomerAddressAttributesMap)
        if 'action' not in mCustomerAddress or mCustomerAddress['action'] == '':
            mCustomerAddress['action'] = 'insertOrUpdate'
        mCustomerId = mCustomer['id']
        uniqueValue = eCustomerAddress['unique_id']
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