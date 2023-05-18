# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoConfigProduct.py
# Compiled at: 2017-01-17 14:48:02
__author__ = 'sandy.tu'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import json
from MagentoCommon import MagentoCore
from MagentoProduct import MagentoProduct

class MagentoConfigProduct(MagentoProduct):

    def __init__(self, mageConf, mageConn=None, mageApi=None):
        MagentoProduct.__init__(self, mageConf, mageConn, mageApi)
        self.mageApi = mageApi
        queries = {'replaceCatalogProductRelationSQL': '\n                REPLACE INTO catalog_product_relation\n                (parent_id,child_id)\n                VALUES (%s,%s)\n            ', 
           'replaceCatalogProductSuperAttributeSQL': '\n                INSERT IGNORE INTO catalog_product_super_attribute\n                (product_id,attribute_id)\n                VALUES (%s,%s)\n            ', 
           'replaceCatalogProductSuperLinkSQL': '\n                REPLACE INTO catalog_product_super_link\n                (product_id,parent_id)\n                VALUES (%s,%s)\n            ', 
           'deleteCatalogProductRelationSQL': '\n                DELETE FROM catalog_product_relation\n                WHERE parent_id = %s and child_id = %s\n            ', 
           'deleteCatalogProductSuperLinkSQL': '\n                DELETE FROM catalog_product_super_link\n                WHERE product_id = %s and parent_id = %s\n            ', 
           'getProductAttributeSetSQL': '\n                SELECT t1.attribute_set_name\n                FROM catalog_product_entity t0\n                INNER JOIN eav_attribute_set t1 ON t0.attribute_set_id = t1.attribute_set_id\n                WHERE t0.entity_id = %s\n            ', 
           'clearNoConfigurableAttributeProductSQL': '\n                DELETE FROM catalog_product_entity\n                WHERE entity_id = %s\n            ', 
           'getConfigProductSimpleProductsSQL': '\n                SELECT b.parent_id, a.attribute_id, b.product_id as child_id, d.value\n                FROM catalog_product_super_attribute a\n                INNER JOIN catalog_product_super_link b ON a.product_id = b.parent_id\n                INNER JOIN eav_attribute_option c ON a.attribute_id = c.attribute_id\n                INNER JOIN eav_attribute_option_value d ON c.option_id = d.option_id AND d.store_id = 0\n                WHERE a.product_id = %s\n            '}
        self.queries = dict(self.queries, **queries)
        self._configProductAttributesMapping = {}

    def preFormatConfigProductJson(self, sourceProduct):
        return sourceProduct

    def getValueFromSourceObj(self, sourceProductObject, configProductAttributesMapping, key):
        value = None
        if configProductAttributesMapping[key] in sourceProductObject:
            value = sourceProductObject[configProductAttributesMapping[key]]
        return value

    def formatConfigProductJson(self, sourceProduct, configProductAttributesMapping={}):
        sourceProduct = self.preFormatConfigProductJson(sourceProduct)
        sourceProductObject = json.loads(sourceProduct)
        formattedConfigProductJsonObj = {}
        formattedConfigProductJsonObj['action'] = self.getValueFromSourceObj(sourceProductObject, configProductAttributesMapping, 'action')
        if formattedConfigProductJsonObj['action'] is None:
            formattedConfigProductJsonObj['action'] = 'insert'
        formattedConfigProductJsonObj['parent_sku'] = self.getValueFromSourceObj(sourceProductObject, configProductAttributesMapping, 'parent_sku')
        formattedConfigProductJsonObj['child_sku'] = self.getValueFromSourceObj(sourceProductObject, configProductAttributesMapping, 'child_sku')
        formattedConfigProductJsonObj['attribute_set_name'] = self.getValueFromSourceObj(sourceProductObject, configProductAttributesMapping, 'attribute_set_name')
        formattedConfigProductJsonObj['configurable_attributes'] = self.getValueFromSourceObj(sourceProductObject, configProductAttributesMapping, 'configurable_attributes')
        configurableAttributes = []
        if formattedConfigProductJsonObj['attribute_set_name'] in configProductAttributesMapping['attribute_sets']:
            if len(formattedConfigProductJsonObj['configurable_attributes']) > 0:
                for attr in formattedConfigProductJsonObj['configurable_attributes'].split(configProductAttributesMapping['configurable_attributes_delimiter']):
                    if attr.strip() == '':
                        continue
                    configurableAttributes.append(configProductAttributesMapping['attribute_sets'][formattedConfigProductJsonObj['attribute_set_name']][attr.strip()])

        formattedConfigProductJsonObj['configurable_attributes'] = configurableAttributes
        return formattedConfigProductJsonObj

    def formatConfigProductJsonExt(self, formattedConfigProductJsonObj, sourceProduct, configProductAttributesMapping={}):
        return formattedConfigProductJsonObj

    def deleteConfigProductRelation(self, parentProductId, childProductId, formattedConfigProductJsonObj):
        self.mageCursor.execute(self.queries['deleteConfigProductRelation'], [parentProductId, childProductId])
        self.mageCursor.execute(self.queries['deleteCatalogProductSuperLinkSQL'], [childProductId, parentProductId])
        return True

    def getProductAttributeSet(self, productId):
        self.mageCursor.execute(self.queries['getProductAttributeSetSQL'], [productId])
        item = self.mageCursor.fetchone()
        if item is not None and len(item) > 0:
            return item[0]
        else:
            return

    def getConfigProductAssociatedSimpleProducts(self, parentProductId):
        self.mageCursor.execute(self.queries['getConfigProductSimpleProductsSQL'], [parentProductId])
        results = self.fetchCursorResultAsDict(self.mageCursor)
        simpleProducts = {}
        for res in results:
            if res['child_id'] in simpleProducts:
                simpleProducts[res['child_id']][res['attribute_id']] = res['value']
            else:
                simpleProducts[res['child_id']] = {res['attribute_id']: res['value']}

        return simpleProducts

    def importConfigProduct(self, sourceProduct, configProductAttributesMapping={}):
        syncResult = {'action': '', 
           'parent_sku': '', 
           'child_sku': '', 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento', 
           'formatted_data': ''}
        try:
            if len(configProductAttributesMapping) == 0:
                configProductAttributesMapping = self._configProductAttributesMapping
            formattedConfigProductJsonObj = self.formatConfigProductJson(sourceProduct, configProductAttributesMapping)
            formattedConfigProductJsonObj = self.formatConfigProductJsonExt(formattedConfigProductJsonObj, sourceProduct, configProductAttributesMapping)
            parentSku = formattedConfigProductJsonObj['parent_sku']
            childSku = formattedConfigProductJsonObj['child_sku']
            syncResult['parent_sku'] = parentSku
            syncResult['child_sku'] = childSku
            syncResult['formatted_data'] = json.dumps(formattedConfigProductJsonObj)
            parentProductId = self.getProductIdBySku(parentSku)
            childProductId = self.getProductIdBySku(childSku)
            action = formattedConfigProductJsonObj['action']
            if parentProductId == 0:
                syncResult['action'] = action
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = ('Ignore config product parent: {0}, child: {1}').format(parentSku, childSku)
                syncResult['sync_notes'] = syncResult['sync_notes'] + ('\nParent SKU: {0} not exist').format(parentSku)
                self.logger.info(syncResult['sync_notes'])
                return syncResult
            if childProductId == 0:
                syncResult['action'] = action
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = ('Ignore config product parent: {0}, child: {1}').format(parentSku, childSku)
                syncResult['sync_notes'] = syncResult['sync_notes'] + ('\nChild SKU: {0} not exist').format(childSku)
                self.logger.info(syncResult['sync_notes'])
                return syncResult
            if action == 'ignore':
                syncResult['action'] = action
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = ('Ignore config product parent: {0}, child: {1}').format(parentSku, childSku)
                self.logger.info(syncResult['sync_notes'])
                return syncResult
            if action == 'delete':
                self.deleteConfigProductRelation(parentProductId, childProductId, formattedConfigProductJsonObj)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Delete config product parent: {0}, child: {1}').format(parentSku, childSku)
                self.logger.info(syncResult['sync_notes'])
                return syncResult
            if len(formattedConfigProductJsonObj['configurable_attributes']) > 0:
                existingSimpleProducts = self.getConfigProductAssociatedSimpleProducts(parentProductId)
                parentAttributeSet = self.getProductAttributeSet(parentProductId)
                childAttributeSet = self.getProductAttributeSet(childProductId)
                if parentAttributeSet != childAttributeSet:
                    syncResult['action'] = action
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = ('Failed to link config product parent: {0}/{1}, child: {2}/{3}').format(parentSku, parentAttributeSet, childSku, childAttributeSet)
                    self.logger.info(syncResult['sync_notes'])
                    return syncResult
                configValues = {}
                for attributeCode in formattedConfigProductJsonObj['configurable_attributes']:
                    childAttributeValue = self.getAttributeValue('catalog_product', attributeCode, childProductId)
                    if childAttributeValue is None:
                        syncResult['action'] = action
                        syncResult['sync_status'] = 'F'
                        syncResult['sync_notes'] = ('Failed to link config product parent: {0}, child: {1}').format(parentSku, childSku)
                        syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n child product attribute {0} is null').format(attributeCode)
                        self.logger.info(syncResult['sync_notes'])
                        return syncResult
                    attributeMetadata = self.getAttributeMetadata(attributeCode, 'catalog_product')
                    if attributeMetadata['frontend_input'] != 'select':
                        syncResult['action'] = action
                        syncResult['sync_status'] = 'F'
                        syncResult['sync_notes'] = ('Failed to link config product parent: {0}, child: {1}').format(parentSku, childSku)
                        syncResult['sync_notes'] = syncResult['sync_notes'] + ('/n child product attribute {0} is not select').format(attributeCode)
                        self.logger.info(syncResult['sync_notes'])
                        return syncResult
                    attributeId = attributeMetadata['attribute_id']
                    self.mageCursor.execute(self.queries['replaceCatalogProductSuperAttributeSQL'], [parentProductId, attributeId])
                    configValues[attributeId] = childAttributeValue

                for simpleProduct, simpleConfigValues in existingSimpleProducts.items():
                    if simpleConfigValues == configValues and simpleProduct != childProductId:
                        syncResult['action'] = action
                        syncResult['sync_status'] = 'F'
                        syncResult['sync_notes'] = ('Failed to link config product parent: {0}, child: {1}').format(parentSku, childSku)
                        syncResult['sync_notes'] = syncResult['sync_notes'] + ('/n {0} has the same config values {1}').format(simpleProduct, configValues)
                        self.logger.info(syncResult['sync_notes'])
                        return syncResult

                self.mageCursor.execute(self.queries['replaceCatalogProductRelationSQL'], [parentProductId, childProductId])
                self.mageCursor.execute(self.queries['replaceCatalogProductSuperLinkSQL'], [childProductId, parentProductId])
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Link config product parent: {0}, child: {1}').format(parentSku, childSku)
            else:
                self.mageCursor.execute(self.queries['clearNoConfigurableAttributeProductSQL'], [parentProductId])
                syncResult['action'] = action
                syncResult['sync_status'] = 'I'
                syncResult['sync_notes'] = ('Ignore config product parent: {0}, child: {1}').format(parentSku, childSku)
                syncResult['sync_notes'] = syncResult['sync_notes'] + '\n no configurable attributes set'
            self.logger.info(syncResult['sync_notes'])
        except Exception as e:
            error = traceback.format_exc()
            self.logger.exception(error)
            syncResult['sync_notes'] = error

        return syncResult
# okay decompiling MagentoConfigProduct.pyc
