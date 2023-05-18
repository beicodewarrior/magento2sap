# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoProduct.py
# Compiled at: 2016-07-25 10:52:09
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
import re

class MagentoProduct(MagentoCore):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoCore.__init__(self, mageConf, mageConn)
        self.mageApi = mageApi
        self.dstCursor = dstCursor
        queries = {'getProductIdBySkuSQL': 'SELECT distinct entity_id FROM catalog_product_entity WHERE sku = %s', 
           'getAttributeSetIdEntityTypeIdSQL': '\n                SELECT eet.entity_type_id,eas.attribute_set_id\n                FROM eav_entity_type eet, eav_attribute_set eas\n                WHERE eet.entity_type_id = eas.entity_type_id\n                AND eet.entity_type_code = %s\n                AND eas.attribute_set_name = %s\n            ', 
           'insertCatalogProductSQL': '\n                INSERT INTO catalog_product_entity\n                (entity_type_id, attribute_set_id, type_id, sku, has_options, required_options, created_at, updated_at)\n                VALUES(%s, %s, %s, %s, 0, 0, now(), now())\n            ', 
           'deleteProductSQL': 'DELETE FROM catalog_product_entity WHERE entity_id = %s', 
           'updateCatalogProductSQL': '\n                UPDATE catalog_product_entity\n                SET entity_type_id = %s,\n                attribute_set_id = %s,\n                type_id = %s,\n                updated_at = now(),\n                WHERE entity_id = %s\n            ', 
           'assignWebsiteSQL': 'REPLACE INTO catalog_product_website (product_id, website_id) VALUES (%s, %s)', 
           'getCategoryIdByAttributeValueSQL': '\n                SELECT t1.entity_id\n                FROM catalog_category_entity_data_type t1\n                WHERE t1.attribute_id = %s\n                AND t1.entity_type_id = %s\n                AND t1.store_id = %s\n                AND t1.value = %s\n            ', 
           'setProductCategorySQL': '\n                INSERT INTO catalog_category_product(category_id,product_id)\n                VALUES (%s,%s)\n                ON DUPLICATE KEY UPDATE\n                category_id = %s,\n                product_id = %s\n            ', 
           'updateCategoryChildrenCountSQL': 'UPDATE catalog_category_entity SET children_count = children_count + 1  where entity_id = %s', 
           'setStockStatuSQL': '\n                INSERT INTO cataloginventory_stock_status\n                (product_id,website_id,stock_id,qty,stock_status)\n                VALUES (%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                qty = %s,\n                stock_status = %s\n            ', 
           'setStockItemSQL': '\n                INSERT INTO  cataloginventory_stock_item\n                (product_id,stock_id,qty,is_in_stock,website_id)\n                VALUES (%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                qty = %s,\n                is_in_stock = %s\n            ', 
           'isProductBelongToCategorySQL': '\n                SELECT count(*) FROM catalog_category_product WHERE product_id = %s and category_id = %s\n            ', 
           'eProductImageInsertSQL': '\n                INSERT INTO e_product_image (image_label, position, sync_status, sync_notes,sku, image_url, image_type, sync_dt)\n                VALUES (%s, %s, %s, %s, %s, %s, %s, now())\n            ', 
           'eProductImangeScheduleUpdateSQL': '\n                UPDATE e_product_image\n                SET image_label = %s ,\n                position = %s ,\n                sync_status = %s ,\n                sync_notes = %s ,\n                sync_dt = now()\n                WHERE\n                sku = %s AND\n                image_url = %s AND\n                image_type = %s\n            ', 
           'isImageScheduledSQL': '\n                SELECT count(*) FROM e_product_image\n                WHERE sku = %s AND image_url = %s AND image_type = %s AND always_ignore = 0\n            ', 
           'exportProductSQL': 'SELECT * FROM catalog_product_entity WHERE updated_at >= %s LIMIT %s', 
           'updateEProductInventorySQL': '\n                UPDATE e_product_inventory\n                SET sync_dt = now(), sync_status = %s, sync_notes = %s\n                WHERE id = %s\n            ', 
           'insertAitocStockStatusSQL': '\n                INSERT INTO aitoc_cataloginventory_stock_status\n                (product_id,website_id,stock_id,qty,stock_status)\n                VALUES (%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                qty = %s,\n                stock_status = %s\n            ', 
           'insertAitocStockItemSQL': '\n                INSERT INTO aitoc_cataloginventory_stock_item\n                (website_id, product_id,stock_id,qty,is_in_stock,use_default_website_stock)\n                VALUES\n                (%s,%s,%s,%s,%s,0)\n                ON DUPLICATE KEY UPDATE\n                qty = %s,\n                is_in_stock = %s\n            ', 
           'insertMProductSQL': '\n                REPLACE INTO m_product_master\n                (id, sku, m_product_id, create_at, m_json_data, sync_status, sync_dt, sync_notes)\n                VALUES\n                (%s, %s, %s, now(), %s, %s, now(), %s)\n            ', 
           'exportAitocStockSQL': "\n                SELECT a.item_id,b.sku,c.code as website_code,a.qty,a.is_in_stock\n                FROM aitoc_cataloginventory_stock_item a\n                INNER JOIN catalog_product_entity b on a.product_id = b.entity_id\n                INNER JOIN core_website c on a.website_id = c.website_id\n                WHERE c.code != 'aitoccode'\n            ", 
           'exportStockSQL': "\n                SELECT a.item_id,b.sku,'admin' as website_code,a.qty,a.is_in_stock\n                FROM cataloginventory_stock_item a\n                INNER JOIN catalog_product_entity b on a.product_id = b.entity_id\n            ", 
           'insertMInventorySQL': '\n                REPLACE INTO m_product_inventory\n                (id, sku, website_code, qty, is_in_stock, stock_status,\n                sync_status, sync_dt, sync_notes,create_at)\n                VALUES\n                (%s, %s, %s, %s, %s, %s, %s, now(), %s, now())\n            ', 
           'getProductWebsitesSQL': '\n                SELECT b.code AS website_code\n                FROM catalog_product_website a\n                INNER JOIN core_website b ON a.website_id = b.website_id\n                WHERE a.product_id = %s\n            ', 
           'insOrUpdGroupPriceSQL': '\n                INSERT INTO catalog_product_entity_group_price\n                (entity_id,all_groups,customer_group_id,website_id,value)\n                VALUES (%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                value = %s\n            ', 
           'insOrUpdGroupTierPriceSQL': '\n                INSERT INTO catalog_product_entity_tier_price\n                (entity_id,all_groups,customer_group_id,website_id,qty,value)\n                VALUES (%s,%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                value = %s\n            ', 
           'getProductOutOfStockQtySQL': '\n                SELECT min_qty\n                FROM cataloginventory_stock_item\n                WHERE product_id = %s AND stock_id = %s AND use_config_min_qty = 0\n            ', 
           'getDefaultOutOfStockQtySQL': "\n                SELECT value\n                FROM core_config_data\n                WHERE path = 'cataloginventory/item_options/min_qty' and scope = 'default'\n            ", 
           'getCompanyIdByCodeSQL': '\n                SELECT id\n                FROM silk_b2bcompany\n                WHERE company_code = %s\n            ', 
           'insOrUpdCompanyPriceSQL': '\n                INSERT INTO silk_b2bcompany_tier_price\n                (entity_id,company_code,website_id,qty,value)\n                VALUES (%s,%s,%s,%s,%s)\n                ON DUPLICATE KEY UPDATE\n                value = %s\n            ', 
           'getCategoryIdByAttributeValueAndPathSQL': "\n                SELECT a.entity_id\n                FROM catalog_category_entity a\n                INNER JOIN catalog_category_entity_{dataType} b ON a.entity_id = b.entity_id\n                INNER JOIN eav_attribute c ON b.attribute_id = c.attribute_id AND c.attribute_code = 'name' and c.entity_type_id = 3\n                WHERE a.level = %s and a.parent_id = %s and b.value = %s;\n            ", 
           'getCategoryIdByAttributeValueAndPathSQLxx': "\n                SELECT a.entity_id\n                FROM catalog_category_entity a\n                INNER JOIN catalog_category_entity_{dataType} b ON a.entity_id = b.entity_id\n                INNER JOIN eav_attribute c ON b.attribute_id = c.attribute_id AND c.attribute_code = 'name' and c.entity_type_id = 3\n                WHERE a.path like %s and b.value = %s;\n            ", 
           'getMaxCategoryIdSQL': '\n                SELECT max(entity_id) FROM catalog_category_entity\n            ', 
           'getRootCategoryByStoreSQL': '\n                SELECT b.root_category_id\n                FROM store a, store_group b\n                WHERE a.group_id = b.group_id\n                AND a.code = %s\n            ', 
           'insertCatalogCategoryEntitySQL': '\n                INSERT INTO catalog_category_entity\n                (entity_id, attribute_set_id, parent_id, created_at, updated_at, path, level, children_count,position)\n                VALUES (%s, %s, %s, now(), now(), %s, %s, %s,%s)\n            ', 
           'getProductUrlkeyCommunitySQL': "\n                SELECT\n                b.value as url_key\n                FROM\n                (\n                SELECT c.attribute_id\n                FROM\n                eav_attribute c\n                INNER JOIN eav_entity_type d on c.entity_type_id = d.entity_type_id and d.entity_type_code = 'catalog_product'\n                WHERE c.attribute_code = 'url_key'\n                ) AS attribute,\n                catalog_product_entity a\n                INNER JOIN catalog_product_entity_varchar b on a.entity_id = b.entity_id\n                WHERE\n                b.attribute_id = attribute.attribute_id\n                AND a.entity_id = %s\n                AND b.store_id = %s\n            ", 
           'insertUrlRewriteSQL': '\n                INSERT IGNORE INTO url_rewrite\n                (entity_type,entity_id,request_path,target_path,redirect_type,store_id,is_autogenerated,metadata)\n                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)\n            ', 
           'getCustomOptionIdByTitleSQL': '\n                SELECT a.option_id\n                FROM catalog_product_option a\n                INNER JOIN catalog_product_option_title b ON a.option_id = b.option_id\n                WHERE a.product_id = %s AND b.title = %s\n            ', 
           'insertCatalogProductOptionSQL': '\n                INSERT INTO catalog_product_option\n                (product_id,type,is_require,sku,max_characters,file_extension,image_size_x,image_size_y,sort_order)\n                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)\n            ', 
           'insertCustomOptionTitleSQL': '\n                INSERT IGNORE INTO catalog_product_option_title\n                (option_id,store_id,title)\n                VALUES (%s,%s,%s)\n            ', 
           'insertCustomOptionPriceSQL': '\n                INSERT IGNORE INTO catalog_product_option_price\n                (option_id,store_id,price,price_type)\n                VALUES (%s,%s,%s,%s)\n            ', 
           'updateProductCustomOptionSQL': '\n                UPDATE catalog_product_entity\n                SET has_options = %s,\n                required_options = %s\n                WHERE entity_id = %s\n            ', 
           'deleteProductCustomOptionSQL': '\n                DELETE FROM catalog_product_option\n                WHERE product_id = %s\n            '}
        self.queries = dict(self.queries, **queries)
        self.queries['insertCatalogProductSQL'] = '\n            INSERT INTO catalog_product_entity\n            (attribute_set_id, type_id, sku, has_options, required_options, created_at, updated_at)\n            VALUES(%s, %s, %s, 0, 0, now(), now())\n        '
        self.queries['updateCatalogProductSQL'] = '\n            UPDATE catalog_product_entity\n            SET attribute_set_id = %s,\n            type_id = %s,\n            updated_at = now()\n            WHERE entity_id = %s\n        '
        self.dstQueries = {'setMProductErpDataSQL': '\n                UPDATE m_product_master\n                SET erp_data = %s\n                WHERE id = %s\n            '}
        self.excludeAttributes = [
         'sku', 'action', 'website_code', 'entity_id', 'image',
         'small_image', 'slider_image', 'thumbnail', 'gallery',
         'type_id', 'attribute_set_name', 'qty', 'images',
         'store_code', 'url_key', 'custom_options']
        self.needCleanAttributes = []
        self.categoryAttribute = {}
        self.protectedAttributes = {}
        self.aitocWebsiteCode = 'aitoccode'
        self.productDefaults = {'attribute_set_name': 'Default', 
           'website_code': 'admin', 
           'store_code': 'admin', 
           'status': '1', 
           'type_id': 'simple', 
           'visibility': '4', 
           'tax_class_id': '2', 
           'qty': 0, 
           'is_in_stock': 1, 
           'stock_status': 1}
        self.priceAttributes = [
         'price', 'special_price', 'special_from_date', 'special_to_date', 'msrp']
        self.productAttributesMap = {}
        self._updateOptionValueAttributes = []
        self._createNewProduct = True
        self._updateAttributeSet = False
        self.dstControl = DSTControl(dstCursor)
        self._entityLogConf = {'enableLog': True, 
           'logPath': self.mageConf['logPath'] + '/entity_log/', 
           'logFileName': ''}
        self._inventoryDefaultConfig = {'min_qty': 0, 
           'use_config_min_qty': 1, 
           'max_sale_qty': 10000, 
           'use_config_max_sale_qty': 1, 
           'min_sale_qty': 0, 
           'use_config_min_sale_qty': 1, 
           'default_website_id': 1}
        self._alwaysInStock = False
        self._multiSelectValueDelimiter = ','
        self._includeRootCategory = False
        self._categoryPathDelimeter = '->'
        self._createCategoryDynamic = False
        self._assignProductToAllLevels = False
        self._categoryValueAttributeCode = 'name'
        self._rootCategories = ''
        self._categoryEavDataDefaults = {'is_active': '1', 
           'is_anchor': '1', 
           'include_in_menu': '0', 
           'custom_use_parent_settings': '0', 
           'custom_apply_to_products': '0', 
           'display_mode': 'PRODUCTS'}
        self._createProductUrlrewirte = False
        self._urlkeyExt = '.html'
        self._urlkeyPrefix = ''
        self._importCustomOption = False
        self._removeCustomOptions = False
        self._disableZeroPriceProduct = False
        self._deleteZeroPriceProduct = True
        self._updatePriceInMasterSync = False

    def getNowStr(self):
        now = datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        return nowstr

    def getProductIdBySku(self, sku):
        self.mageCursor.execute(self.queries['getProductIdBySkuSQL'], [sku])
        res = self.mageCursor.fetchone()
        if res is not None:
            entityId = int(res[0])
        else:
            entityId = 0
        return entityId

    def getAttributeSetIdEntityTypeId(self, entityTypeCode='catalog_product', attributeSetName='Default'):
        self.mageCursor.execute(self.queries['getAttributeSetIdEntityTypeIdSQL'], [entityTypeCode, attributeSetName])
        item = self.mageCursor.fetchone()
        if item is not None and len(item) >= 2:
            return {'entity_type_id': item[0], 'attribute_set_id': item[1]}
        else:
            exception = ('attribute_set/entity_type_code: {0}/{1} not existed').format(attributeSetName, entityTypeCode)
            self.logger.exception(exception)
            return
            return

    def insertCatalogProductEntity(self, sku, attributeSetName='Default', typeId='simple'):
        ids = self.getAttributeSetIdEntityTypeId('catalog_product', attributeSetName)
        if ids == None:
            return 0
        else:
            self.mageCursor.execute(self.queries['insertCatalogProductSQL'], (ids['attribute_set_id'], typeId, sku))
            productId = self.mageCursor.lastrowid
            return productId

    def updateCatalogProductEntity(self, productId, attributeSetName='Default', typeId='simple'):
        ids = self.getAttributeSetIdEntityTypeId('catalog_product', attributeSetName)
        if ids == None:
            return 0
        else:
            self.mageCursor.execute(self.queries['updateCatalogProductSQL'], [ids['attribute_set_id'], typeId, productId])
            return

    def deleteProductById(self, productId, formattedProductJsonObj={}):
        if productId == 0:
            return
        if formattedProductJsonObj:
            self.removeProductFromCategory(productId, formattedProductJsonObj)
        self.mageCursor.execute(self.queries['deleteProductSQL'], [productId])

    def catalogCategoryAssignProduct(self, productId, formattedProductJsonObj):
        if not self.categoryAttribute:
            return
        else:
            categoryName = formattedProductJsonObj[self.categoryAttribute['productAttributeName']]
            categoryId = self.getCategoryIdByAttributeValue(self.categoryAttribute['categoryAttributeName'], categoryName)
            if categoryId is None or categoryId == 0:
                pass
            else:
                self.logger.info(('Assign Category by API: Category Name: {0}, Category ID: {1}').format(categoryName, categoryId))
                self.mageApi.catalogCategoryAssignProduct(productId, categoryId)
            return

    def removeProductFromCategory(self, productId, formattedProductJsonObj):
        if not self.categoryAttribute:
            return
        else:
            categoryName = formattedProductJsonObj[self.categoryAttribute['productAttributeName']]
            categoryId = self.getCategoryIdByAttributeValue(self.categoryAttribute['categoryAttributeName'], categoryName)
            if categoryId is None or categoryId == 0:
                pass
            elif self.isProductBelongToCategory(productId, categoryId):
                pass
            else:
                self.logger.info(('Remove Category by API: Category Name: {0}, Category ID: {1}').format(categoryName, categoryId))
                self.mageApi.catalogCategoryRemoveProduct(productId, categoryId)
            return

    def setProductJsonDefault(self, productObject, attributeCode):
        if attributeCode in self.productDefaults:
            attributeDefaultValue = self.productDefaults[attributeCode]
        else:
            attributeDefaultValue = ''
        if attributeCode in productObject:
            if productObject[attributeCode] is not None:
                if str(productObject[attributeCode]).strip() != '':
                    return productObject
                productObject[attributeCode] = attributeDefaultValue
            else:
                productObject[attributeCode] = attributeDefaultValue
        else:
            productObject[attributeCode] = attributeDefaultValue
        return productObject

    def getWebsiteCodesByStoreCodes(self, storeCodes):
        if type(storeCodes) != list:
            storeCodes = [ code.strip() for code in storeCodes.split(',') ]
        websiteCodes = []
        for storeCode in storeCodes:
            if storeCode in self.stores:
                websiteCodes.append(self.stores[storeCode]['website_code'])

        if len(websiteCodes) == 0:
            websiteCodes = [
             self.productDefaults['website_code']]
        return (',').join(websiteCodes)

    def preFormatProductJson(self, sourceProduct):
        return sourceProduct

    def getTaxClassId(self, taxClass):
        if taxClass is None or taxClass.strip() == '':
            return taxClass
        taxClassId = self.getTaxClassIdByName(taxClass, 'PRODUCT')
        if taxClassId is None:
            return taxClassId
        else:
            return str(taxClassId)
            return

    def setFormattedProductUrlKey(self, formattedProductJsonObj):
        if 'url_key' in formattedProductJsonObj and formattedProductJsonObj['url_key'] != '':
            return formattedProductJsonObj
        else:
            name = formattedProductJsonObj['name']
            sku = formattedProductJsonObj['sku']
            if name is not None:
                name = re.sub('[^0-9a-zA-Z ]+', ' ', name).replace(' ', '-').lower()
                sku = re.sub('[^0-9a-zA-Z ]+', ' ', sku).replace(' ', '-').lower()
                formattedProductJsonObj['url_key'] = self._urlkeyPrefix + name + '-' + sku
            return formattedProductJsonObj

    def formatProductJson(self, sourceProduct, productAttributesMap={}):
        sourceProduct = self.preFormatProductJson(sourceProduct)
        sourceProductObject = json.loads(sourceProduct)
        formattedProductJsonObj = {}
        for k, v in productAttributesMap.items():
            if v in sourceProductObject:
                if sourceProductObject[v] is not None:
                    if k == 'tax_class_id':
                        formattedProductJsonObj[k] = self.getTaxClassId(sourceProductObject[v])
                    elif type(sourceProductObject[v]) == unicode:
                        formattedProductJsonObj[k] = sourceProductObject[v]
                    else:
                        formattedProductJsonObj[k] = str(sourceProductObject[v])
                else:
                    formattedProductJsonObj[k] = None

        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'attribute_set_name')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'type_id')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'status')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'visibility')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'tax_class_id')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'qty')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'store_code')
        formattedProductJsonObj = self.setProductJsonDefault(formattedProductJsonObj, 'website_code')
        formattedProductJsonObj = self.setFormattedProductUrlKey(formattedProductJsonObj)
        return formattedProductJsonObj

    def formatProductJsonExt(self, formattedProductJsonObj, sourceProduct, productAttributesMap):
        return formattedProductJsonObj

    def assignWebsite(self, productId, formattedProductJsonObj):
        if 'website_code' in formattedProductJsonObj and formattedProductJsonObj['website_code'] != '':
            websites = self.getWebsites()
            websiteCodes = [ websiteCode.strip() for websiteCode in formattedProductJsonObj['website_code'].split(',') ]
            for websiteCode in websiteCodes:
                if websiteCode in websites:
                    websiteId = websites[websiteCode]['id']
                    self.mageCursor.execute(self.queries['assignWebsiteSQL'], [productId, websiteId])
                    self.logger.info(('product_id/website_code: {0}/{1}').format(productId, websiteCode))

        elif 'storeCode' in self.mageConf:
            stores = self.getStores()
            if self.mageConf['storeCode'] in stores:
                websiteId = stores[self.mageConf['storeCode']]['website_id']
                self.mageCursor.execute(self.queries['assignWebsiteSQL'], [productId, websiteId])
                self.logger.info(('product_id/website_code: {0}/{1}').format(productId, stores[self.mageConf['storeCode']]['website_code']))

    def getCategoryIdByAttributeValue(self, attributeCode, attributeValue, storeId=0):
        attributeMetadata = self.getAttributeMetadata(attributeCode, 'catalog_category')
        categoryId = None
        if attributeMetadata:
            data_type = attributeMetadata['backend_type']
            self.queries['getCategoryIdByAttributeValueSQL'] = self.queries['getCategoryIdByAttributeValueSQL'].replace('data_type', data_type)
            self.mageCursor.execute(self.queries['getCategoryIdByAttributeValueSQL'], [
             attributeMetadata['attribute_id'], attributeMetadata['entity_type_id'], storeId, attributeValue])
            res = self.mageCursor.fetchone()
            if res is not None:
                categoryId = int(res[0])
        return categoryId

    def isProductBelongToCategory(self, productId, categoryId):
        self.mageCursor.execute(self.queries['isProductBelongToCategorySQL'], [productId, categoryId])
        res = self.mageCursor.fetchone()
        if res is None or res[0] == 0:
            return False
        return True

    def setProductCategory(self, productId, categoryId):
        if productId is None or categoryId is None:
            pass
        else:
            self.mageCursor.execute(self.queries['setProductCategorySQL'], [categoryId, productId, categoryId, productId])
            self.mageCursor.execute(self.queries['updateCategoryChildrenCountSQL'], [categoryId])
        return

    def assignCategory(self, productId, formattedProductJsonObj, syncCategoryThroughAPI=False):
        pass

    def isImageScheduled(self, sku, imageUrl, imageType):
        self.dstCursor.execute(self.queries['isImageScheduledSQL'], [sku, imageUrl, imageType])
        res = self.dstCursor.fetchone()
        if res is None or res[0] == 0:
            return False
        return True

    def scheduleImages(self, productId, formattedProductJsonObj):
        sku = formattedProductJsonObj['sku']
        syncResult = {'sku': sku, 
           'product_id': productId, 
           'sync_status': '', 
           'sync_notes': ''}
        try:
            imageTypes = ['image', 'small_image', 'thumbnail', 'swatch_image', 'slider_image', 'media_gallery']
            mainImage = ''
            mainImagePosition = 0
            position = 0
            imageLabel = ''
            syncStatus = 'N'
            uniqueImages = {}
            for imageType in imageTypes:
                if imageType not in formattedProductJsonObj:
                    log = ('{0} is not in product json').format(imageType)
                    self.logger.info(log)
                    continue
                imageUrl = formattedProductJsonObj[imageType]
                if imageUrl is None or imageUrl.strip() == '' or imageUrl.strip() == 'no_selection':
                    continue
                imageUrl = imageUrl.strip()
                if imageType == 'image':
                    mainImage = imageUrl
                if imageType == 'media_gallery':
                    images = [ image.strip() for image in imageUrl.split(',') ]
                    for image in images:
                        if image not in uniqueImages:
                            uniqueImages[image] = [
                             imageType]
                        else:
                            uniqueImages[image].append(imageType)

                elif imageUrl not in uniqueImages:
                    uniqueImages[imageUrl] = [
                     imageType]
                else:
                    uniqueImages[imageUrl].append(imageType)

            for uImageUrl, imageTypes in uniqueImages.items():
                if uImageUrl == mainImage:
                    imagePosition = mainImagePosition
                else:
                    imagePosition = position
                    position = position + 1
                imageType = (',').join(imageTypes)
                syncNotes = ('Schedule Image sku/type/url : {0}/{1}/{2}').format(sku, imageType, uImageUrl)
                param = [imageLabel, imagePosition, syncStatus, syncNotes, sku, uImageUrl, imageType]
                isScheduled = self.isImageScheduled(sku, uImageUrl, imageType)
                if isScheduled:
                    log = ('sku/type/url : {0}/{1}/{2} already scheduled').format(sku, imageType, uImageUrl)
                    self.logger.info(log)
                else:
                    sql = self.queries['eProductImageInsertSQL']
                    self.dstCursor.execute(sql, param)
                    self.logger.info(syncNotes)

            syncResult['sync_status'] = 'O'
            syncResult['sync_Notes'] = ('Scheduled images for {0}').format(sku)
        except Exception as e:
            log = traceback.format_exc()
            self.logger.exception(log)
            syncResult['sync_status'] = 'F'
            syncResult['sync_Notes'] = ('Failed to scheduled images for {0} with error {1}').format(sku, log)

        return syncResult

    def assignStock(self, productId, formattedProductJsonObj):
        sku = formattedProductJsonObj['sku']
        syncResult = {'sku': sku, 
           'product_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        if productId is None:
            productId = self.getProductIdBySku(sku)
        if productId == 0:
            log = ('Product not existed: {0}').format(sku)
            self.logger.info(log)
            syncResult['sync_notes'] = log
            syncResult['sync_status'] = 'I'
            return syncResult
        else:
            try:
                qty = formattedProductJsonObj['qty']
                outOfStockQty = self.getProductOutOfStockQty(productId)
                if qty > int(outOfStockQty):
                    isInStock = 1
                    stockStatus = 1
                else:
                    isInStock = 0
                    stockStatus = 0
                websiteId = self._inventoryDefaultConfig['default_website_id']
                self.mageCursor.execute(self.queries['setStockStatuSQL'], [productId, websiteId, 1, qty, stockStatus, qty, stockStatus])
                self.mageCursor.execute(self.queries['setStockItemSQL'], [productId, 1, qty, isInStock, websiteId, qty, isInStock])
                syncResult['sync_notes'] = ('sku/qty : {0}/{1}').format(sku, qty)
                syncResult['sync_status'] = 'O'
                syncResult['product_id'] = productId
            except Exception as e:
                log = ('Failed to assign stock for {0} with error {1}').format(sku, str(e))
                self.logger.exception(log)
                syncResult['sync_notes'] = log
                syncResult['sync_status'] = 'F'
                syncResult['product_id'] = productId

            return syncResult
            return

    def disableProductById(self, productId, formattedProductJsonObj, syncResult):
        sku = formattedProductJsonObj['sku']
        if productId > 0:
            eavData = {}
            eavData['status'] = [
             [
              productId, '2']]
            self.processEavData(eavData, formattedProductJsonObj, True)
            syncResult['action'] = 'disable'
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('Disable product {0}').format(sku)
        else:
            syncResult['action'] = 'disable'
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('product {0} not existed').format(sku)
        return syncResult

    def getProductStores(self, product):
        storeCodes = []
        if 'store_code' in product:
            storeCodes = product['store_code']
            if type(storeCodes) != list:
                storeCodes = [ code.strip() for code in storeCodes.split(',') ]
        return storeCodes

    def importProduct(self, sourceProduct, productAttributesMap={}, syncCategoryThroughAPI=False):
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        if len(productAttributesMap) == 0:
            productAttributesMap = self.productAttributesMap
        formattedProductJsonObj = self.formatProductJson(sourceProduct, productAttributesMap)
        formattedProductJsonObj = self.formatProductJsonExt(formattedProductJsonObj, sourceProduct, productAttributesMap)
        sku = formattedProductJsonObj['sku']
        syncResult = {'action': '', 
           'sku': sku, 
           'product_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento', 
           'formatted_data': json.dumps(formattedProductJsonObj)}
        productId = self.getProductIdBySku(sku)
        action = formattedProductJsonObj['action']
        if action == 'ignore':
            syncResult['action'] = action
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Ignore product {0}').format(sku)
            return syncResult
        else:
            if action == 'disable':
                syncResult = self.disableProductById(productId, formattedProductJsonObj, syncResult)
                return syncResult
            if action == 'delete':
                self.deleteProductById(productId, formattedProductJsonObj)
                syncResult['action'] = action
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Delete product {0}').format(sku)
                return syncResult
            eavData = {}
            typeId = formattedProductJsonObj['type_id'].strip()
            attributeSetName = formattedProductJsonObj['attribute_set_name'].strip()
            productStores = self.getProductStores(formattedProductJsonObj)
            if productId == 0 and self._createNewProduct == True:
                productId = self.insertCatalogProductEntity(sku, attributeSetName, typeId)
                formattedProductJsonObj['action'] = 'insert'
                if productId == 0:
                    self.logger.info(('Failed to create new product: {0}').format(sku))
                    syncResult['action'] = formattedProductJsonObj['action']
                    syncResult['sync_status'] = 'O'
                    return syncResult
            else:
                formattedProductJsonObj['action'] = 'update'
                if self._updatePriceInMasterSync == False and 'price' in formattedProductJsonObj:
                    del formattedProductJsonObj['price']
                if self._updateAttributeSet == True:
                    self.updateCatalogProductEntity(productId, attributeSetName, typeId)
                try:
                    for k, v in formattedProductJsonObj.items():
                        if k in self.needCleanAttributes:
                            if (type(v) == str or type(v) == unicode) and v.strip() != '':
                                self.cleanAttributeData(productId, k)
                        if k not in self.excludeAttributes:
                            if k in self.protectedAttributes:
                                isProtected = self.isValueProtected(productId, k)
                                if isProtected:
                                    syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n {0} is protected in Magento').format(k)
                                else:
                                    eavData[k] = [
                                     [
                                      productId, v]]
                            else:
                                eavData[k] = [
                                 [
                                  productId, v]]
                            if k in self._updateOptionValueAttributes and 'admin' in productStores:
                                if (type(v) == str or type(v) == unicode) and v.strip() != '':
                                    attributeMetadata = self.getAttributeMetadata(k, 'catalog_product')
                                    if attributeMetadata is not None and attributeMetadata['frontend_input'] == 'select':
                                        attributeOptions = {0: v}
                                        self.setAttributeOptionValues(k, attributeOptions)
                                    elif attributeMetadata is not None and attributeMetadata['frontend_input'] == 'multiselect':
                                        values = v.strip('"').strip("'").strip('\n').strip()
                                        listValues = [ v.strip() for v in values.split(self._multiSelectValueDelimiter) ]
                                        for listValue in listValues:
                                            attributeOptions = {0: listValue}
                                            self.setAttributeOptionValues(k, attributeOptions)

                    if formattedProductJsonObj['action'] == 'insert':
                        updateAdmin = True
                    else:
                        updateAdmin = False
                    self.processEavData(eavData, formattedProductJsonObj, updateAdmin)
                    self.assignWebsite(productId, formattedProductJsonObj)
                    if self._createProductUrlrewirte == True:
                        self.createProductUrlRewrite(productId, formattedProductJsonObj)
                    imageScheduleResult = self.scheduleImages(productId, formattedProductJsonObj)
                    log = ('Product {0} {1} successfully').format(sku, formattedProductJsonObj['action'])
                    syncResult['sync_status'] = 'O'
                    if formattedProductJsonObj['action'] == 'insert':
                        stockSyncResult = self.assignStock(productId, formattedProductJsonObj)
                        log = log + '\n' + stockSyncResult['sync_notes']
                        syncResult['sync_status'] = stockSyncResult['sync_status']
                    if self._importCustomOption == True:
                        customOptionSyncResult = self.importCustomOptions(productId, formattedProductJsonObj, syncResult)
                        log = log + '\n' + customOptionSyncResult['sync_notes']
                        syncResult['sync_status'] = customOptionSyncResult['sync_status']
                    extSyncResult = self.importProductExt(productId, formattedProductJsonObj, syncResult)
                    log = log + '\n' + extSyncResult['sync_notes']
                    syncResult['sync_status'] = extSyncResult['sync_status']
                    self.logger.info(log)
                    syncResult['product_id'] = productId
                    syncResult['sync_notes'] = log
                except Exception as e:
                    log = ('Product {0} {1} failed with error {2}').format(sku, formattedProductJsonObj['action'], str(e))
                    self.logger.exception(log)
                    syncResult['product_id'] = productId
                    syncResult['sync_status'] = 'F'
                    syncResult['sync_notes'] = log

            return syncResult

    def importProductExt(self, productId, formattedProductJsonObj, syncResult):
        syncResult['sync_notes'] = ''
        return syncResult

    def getProductUrlkey(self, productId, storeId=0):
        if 'edition' in self.mageConf and self.mageConf['edition'] == 'enterprise':
            sql = self.queries['getProductUrlkeyEnterpriseSQL']
        else:
            sql = self.queries['getProductUrlkeyCommunitySQL']
        self.mageCursor.execute(sql, [productId, storeId])
        urlkey = None
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            urlkey = res[0]
        if urlkey is None and storeId != 0:
            urlkey = self.getProductUrlkey(productId, 0)
        return urlkey

    def createProductUrlRewrite(self, productId, mProduct):
        targetPath = ('catalog/product/view/id/{0}').format(productId)
        entityType = 'product'
        redirectType = 0
        isAutogenerated = 1
        metadata = None
        if 'store_code' in mProduct:
            storeCodes = mProduct['store_code']
            if type(storeCodes) != list:
                storeCodes = [ code.strip() for code in storeCodes.split(',') ]
        else:
            storeCodes = [
             self.productDefaults['store_code']]
        for storeCode in storeCodes:
            if storeCode in self.stores:
                storeId = self.stores[storeCode]['id']
                urlkey = self.getProductUrlkey(productId, storeId)
                if urlkey is None:
                    log = ('Urlkey is none for product_id: {0} in store {1}').format(productId, storeId)
                    self.logger.info(log)
                    continue
                requestPath = ('{urlkey}{urlkeyExt}').format(urlkey=urlkey, urlkeyExt=self._urlkeyExt)
                param = [entityType, productId, requestPath, targetPath, redirectType, storeId, isAutogenerated, metadata]
                self.mageCursor.execute(self.queries['insertUrlRewriteSQL'], param)
                log = ('product_id/request_path/target_path/store_id: {0}/{1}/{2}/{3}').format(productId, requestPath, targetPath, storeId)

        return

    def getProductWebsites(self, productId):
        self.mageCursor.execute(self.queries['getProductWebsitesSQL'], [productId])
        websiteCodes = self.fetchCursorResultAsDict(self.mageCursor)
        productWebsiteCodes = []
        for row in websiteCodes:
            productWebsiteCodes.append(row['website_code'])

        return productWebsiteCodes

    def getMProducts(self, attributeSetName='', lastCutoffDt='2015-01-01', limits=0, allStores=0):
        if attributeSetName != '':
            attributes = self.getAttributesByEntityTypeAndAttributeSet('catalog_product', attributeSetName)
        else:
            attributes = self.getAttributesByEntityType('catalog_product')
        self.mageCursor.execute(self.queries['exportProductSQL'], [lastCutoffDt, limits])
        print self.mageCursor._last_executed
        products = self.fetchCursorResultAsDict(self.mageCursor)
        allProducts = []
        cnt = 1
        if allStores == 1:
            stores = self.getStores()
        for product in products:
            productWebsiteCodes = self.getProductWebsites(product['entity_id'])
            product['website_code'] = (',').join(productWebsiteCodes)
            for attributeCode in attributes:
                if attributeCode in product:
                    if product[attributeCode] is not None:
                        product[attributeCode] = str(product[attributeCode])
                    continue
                if allStores == 1:
                    attributeValue = {}
                    for storeCode, storeInfo in stores.items():
                        storeId = storeInfo['id']
                        attributeStoreValue = self.getAttributeValue('catalog_product', attributeCode, product['entity_id'], storeId)
                        if attributeStoreValue is not None:
                            attributeStoreValue = str(attributeStoreValue)
                        attributeValue[storeCode] = attributeStoreValue

                else:
                    attributeValue = self.getAttributeValue('catalog_product', attributeCode, product['entity_id'])
                    if attributeValue is not None:
                        attributeValue = str(attributeValue)
                product[attributeCode] = attributeValue

            allProducts.append(product)
            cnt = cnt + 1

        return allProducts

    def exportMagentoProductExt(self, mProduct):
        pass

    def convertMProductToErpData(self, mProduct):
        return ''

    def setMProductErpData(self, mProduct):
        erpData = self.convertMProductToErpData(mProduct)
        self.dstCursor.execute(self.dstQueries['setMProductErpDataSQL'], [erpData, mProduct['entity_id']])

    def syncMagentoProductsToDst(self, attributeSetName='', lastCutoffDt='', limits=0, allStores=0):
        syncResult = {'sync_status': 'F', 
           'sync_notes': ''}
        try:
            start = self.getNowStr()
            task = 'product_mage_to_dst'
            if lastCutoffDt == '':
                lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
            mProducts = self.getMProducts(attributeSetName, lastCutoffDt, limits, allStores)
            lastCutoffEntityId = None
            for mProduct in mProducts:
                productId = mProduct['entity_id']
                sku = mProduct['sku']
                mJsonData = json.dumps(mProduct)
                mProduct['m_json_data'] = mJsonData
                syncStatus = 'N'
                syncNotes = 'Magento to DST'
                if productId > lastCutoffEntityId:
                    lastCutoffEntityId = productId
                self.dstCursor.execute(self.queries['insertMProductSQL'], [
                 productId, sku, productId, mJsonData, syncStatus, syncNotes])
                self.exportMagentoProductExt(mProduct)
                self.logger.info(('{0} Magento to DST').format(sku))

            if lastCutoffEntityId:
                syncStatus = 'O'
                lastCutoffDt = start
                lastStartDt = start
                lastEndDt = self.getNowStr()
                syncNotes = 'Sync from Magento to DST'
                self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
            else:
                syncStatus = 'I'
                syncNotes = 'No product needs to sync'
            syncResult['sync_status'] = syncStatus
            syncResult['sync_notes'] = syncNotes
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def exportProductsToJson(self, fileName='', attributeSetName='', limits=1, storeId=0):
        if attributeSetName != '':
            attributes = self.getAttributesByEntityTypeAndAttributeSet('catalog_product', attributeSetName)
        else:
            attributes = self.getAttributesByEntityType('catalog_product')
        self.mageCursor.execute(self.queries['exportProductSQL'], ['2015-01-01', limits])
        products = self.fetchCursorResultAsDict(self.mageCursor)
        allProducts = []
        cnt = 1
        for product in products:
            for attributeCode in attributes:
                if attributeCode in product:
                    if product[attributeCode] is not None:
                        product[attributeCode] = str(product[attributeCode])
                    continue
                attributeValue = self.getAttributeValue('catalog_product', attributeCode, product['entity_id'])
                if attributeValue is not None:
                    attributeValue = str(attributeValue)
                product[attributeCode] = attributeValue
                allProducts.append(product)

            cnt = cnt + 1

        jsonFile = open(fileName, 'wb')
        json.dump(allProducts, jsonFile, sort_keys=True, indent=4, separators=(',',
                                                                               ': '))
        self.logger.info(('{0} products saved to {1}').format(cnt, fileName))
        return

    def exportProductsToCsv(self, fileName='', attributeSetName='', limits=1, storeId=0):
        if attributeSetName != '':
            attributes = self.getAttributesByEntityTypeAndAttributeSet('catalog_product', attributeSetName)
        else:
            attributes = self.getAttributesByEntityType('catalog_product')
        self.mageCursor.execute(self.queries['exportProductSQL'], ['2015-01-01', limits])
        products = self.fetchCursorResultAsDict(self.mageCursor)
        allProducts = []
        cnt = 1
        for product in products:
            for attributeCode in attributes:
                if attributeCode in product:
                    continue
                attributeValue = self.getAttributeValue('catalog_product', attributeCode, product['entity_id'])
                if attributeValue is not None:
                    attributeValue = str(attributeValue)
                product[attributeCode] = attributeValue
                allProducts.append(product)

        theData = []
        for product in allProducts:
            if cnt == 1:
                keys = product.keys()
                theData.append(keys)
            row = []
            for k in keys:
                row.append(product[k])

            theData.append(row)
            cnt = cnt + 1

        with open(fileName, 'wb') as (f):
            writer = csv.writer(f)
            writer.writerows(theData)
        self.logger.info(('{0} products saved to {1}').format(cnt, fileName))
        return

    def isValueProtected(self, entityId, protectedAttributeCode, entityTypeCode='catalog_product', storeId=0):
        if protectedAttributeCode in self.protectedAttributes:
            checkAttributeCode = self.protectedAttributes[protectedAttribute]
            checkAttributeValue = self.getAttributeValue(entityTypeCode, checkAttributeCode, entityId, storeId)
            if checkAttributeValue == 1:
                return True
            return False
        else:
            return False

    def getProductOutOfStockQty(self, productId, websiteId=0, multiLocationModule=''):
        self.getDefaultOutOfStockQty()
        outOfStockQty = self._inventoryDefaultConfig['min_qty']
        sql = self.queries['getProductOutOfStockQtySQL']
        if multiLocationModule == 'aitoc':
            sql = sql.replace('cataloginventory_stock_item', 'aitoc_cataloginventory_stock_item')
            sql = sql + (' AND website_id = {0}').format(websiteId)
        self.mageCursor.execute(sql, [productId, 1])
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            outOfStockQty = res[0]
        return outOfStockQty

    def getDefaultOutOfStockQty(self):
        self.mageCursor.execute(self.queries['getDefaultOutOfStockQtySQL'])
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            self._inventoryDefaultConfig['min_qty'] = res[0]
        return

    def importInventory(self, product):
        sku = product['sku']
        syncResult = {'id': product['id'], 
           'action': '', 
           'sku': sku, 
           'product_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        if productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Does not existed in Magento').format(sku)
        else:
            try:
                isProtected = self.isValueProtected(productId, 'stock')
                if isProtected:
                    syncResult['sync_status'] = 'I'
                    syncResult['sync_notes'] = ('Stock is protected in Magento').format(sku)
                else:
                    websiteId = self._inventoryDefaultConfig['default_website_id']
                    qty = product['qty']
                    if 'is_in_stock' in product and product['is_in_stock'] is not None:
                        is_in_stock = product['is_in_stock']
                    if 'stock_status' in product and product['stock_status'] is not None:
                        stock_status = product['stock_status']
                    outOfStockQty = self.getProductOutOfStockQty(productId)
                    if qty > int(outOfStockQty):
                        is_in_stock = 1
                        stock_status = 1
                    else:
                        is_in_stock = 0
                        stock_status = 0
                    if self._alwaysInStock == True:
                        is_in_stock = 1
                        stock_status = 1
                    self.mageCursor.execute(self.queries['setStockStatuSQL'], [
                     productId, websiteId, 1, qty, stock_status, qty, stock_status])
                    self.mageCursor.execute(self.queries['setStockItemSQL'], [
                     productId, 1, qty, is_in_stock, websiteId, qty, is_in_stock])
                    extSyncResult = self.importInvenoryExt(productId, product, syncResult)
                    syncResult['sync_status'] = extSyncResult['sync_status']
                    syncResult['sync_notes'] = 'Sync inventory to Magento \n' + extSyncResult['sync_notes']
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Inventory Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, status: {1} notes: {2}').format(sku, syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def importInvenoryExt(self, productId, product, syncResult):
        syncResult = {'sync_status': 'O', 
           'sync_notes': ''}
        return syncResult

    def importAitocMultiLocationInventory(self, product):
        sku = product['sku']
        syncResult = {'id': product['id'], 
           'action': '', 
           'sku': sku, 
           'product_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        if productId == 0:
            syncResult['sync_status'] = 'N'
            syncResult['sync_notes'] = ('{0} Does not existed in Magento').format(sku)
        else:
            try:
                isProtected = self.isValueProtected(productId, 'stock')
                if isProtected:
                    syncResult['sync_status'] = 'I'
                    syncResult['sync_notes'] = ('Stock is protected in Magento').format(sku)
                else:
                    if 'website_code' in product:
                        websiteCodes = product['website_code']
                    else:
                        websiteCodes = ''
                    if websiteCodes is None or websiteCodes == '':
                        websiteIds = [
                         0]
                    else:
                        websiteIds = []
                        websiteCodesList = [ code.strip() for code in websiteCodes.split(',') ]
                        for websiteCode in websiteCodesList:
                            if websiteCode in self.websites:
                                websiteId = self.websites[websiteCode]['id']
                                if websiteId not in websiteIds:
                                    websiteIds.append(websiteId)
                            else:
                                self.logger.info(('website code : {0} is not found in Magento').format(websiteCode))

                    qty = product['qty']
                    if 'is_in_stock' in product and product['is_in_stock'] is not None:
                        is_in_stock = product['is_in_stock']
                    if 'stock_status' in product and product['stock_status'] is not None:
                        stock_status = product['stock_status']
                    for websiteId in websiteIds:
                        outOfStockQty = self.getProductOutOfStockQty(productId, websiteId, 'aitoc')
                        if qty > int(outOfStockQty):
                            is_in_stock = 1
                            stock_status = 1
                        else:
                            is_in_stock = 0
                            stock_status = 0
                        self.mageCursor.execute(self.queries['insertAitocStockStatusSQL'], [
                         productId, websiteId, 1, qty, stock_status, qty, stock_status])
                        self.mageCursor.execute(self.queries['insertAitocStockItemSQL'], [
                         websiteId, productId, 1, qty, is_in_stock, qty, is_in_stock])

                    if self.aitocWebsiteCode in self.websites:
                        aitocWebsiteId = self.websites[self.aitocWebsiteCode]['id']
                        self.mageCursor.execute(self.queries['insertAitocStockItemSQL'], [
                         aitocWebsiteId, productId, 1, qty, is_in_stock, qty, is_in_stock])
                    syncResult['sync_status'] = 'O'
                    syncResult['sync_notes'] = 'Sync inventory to Magento'
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Inventory Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, status: {1} notes: {2}').format(sku, syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def processEavData(self, eavData, product, updateAdmin=False):
        if 'store_code' in product:
            storeCodes = product['store_code']
            if type(storeCodes) != list:
                storeCodes = [ code.strip() for code in storeCodes.split(',') ]
        else:
            storeCodes = [
             self.productDefaults['store_code']]
        if updateAdmin and 'admin' not in storeCodes:
            storeCodes.insert(0, 'admin')
        for storeCode in storeCodes:
            if storeCode in self.stores:
                storeId = self.stores[storeCode]['id']
                for k, v in eavData.items():
                    if len(v) > 0:
                        entity = MagentoEntity(self.mageCursor, k, 'catalog_product', storeId, self._entityLogConf)
                        entity._mageConf = self.mageConf
                        entity._multiSelectValueDelimiter = self._multiSelectValueDelimiter
                        entity.setProperties()
                        entity.readData(v)
                        entity.loadData()
                        del entity

    def importProductPrice(self, product):
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        sku = product['sku']
        syncResult = {'id': product['id'], 
           'sku': sku, 
           'product_id': None, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        productId = self.getProductIdBySku(sku)
        eavData = {}
        if productId == 0:
            syncResult['sync_status'] = 'N'
            syncResult['sync_notes'] = ('{0} Does not existed in Magento').format(sku)
            return syncResult
        else:
            try:
                for k, v in product.items():
                    if k in self.priceAttributes:
                        if k in self.protectedAttributes:
                            isProtected = self.isValueProtected(productId, k)
                            if isProtected:
                                syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n {0} is protected in Magento').format(k)
                        else:
                            eavData[k] = [
                             [
                              productId, v]]
                            if k == 'price' and self._disableZeroPriceProduct == True and v <= 0:
                                eavData['status'] = [
                                 [
                                  productId, '2']]
                            if k == 'price' and self._deleteZeroPriceProduct == True and v <= 0:
                                self.deleteProductById(productId)

                self.processEavData(eavData, product)
                syncResult['product_id'] = productId
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = syncResult['sync_notes'] + ('\n price updated for {0}').format(sku)
            except Exception as e:
                log = ('Price {0} update failed with error {1}').format(sku, traceback.format_exc())
                syncResult['product_id'] = productId
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = log

            self.logger.info(('sku: {0}, status: {1} notes: {2}').format(sku, syncResult['sync_status'], syncResult['sync_notes']))
            return syncResult

    def getMInventory(self, multiLocationModule=''):
        if multiLocationModule == 'aitoc':
            exportStockSQL = self.queries['exportAitocStockSQL']
        else:
            exportStockSQL = self.queries['exportStockSQL']
        self.mageCursor.execute(exportStockSQL)
        print self.mageCursor._last_executed
        mInventories = self.fetchCursorResultAsDict(self.mageCursor)
        return mInventories

    def syncMagentoInventoryToDST(self, multiLocationModule=''):
        syncResult = {'sync_status': 'F', 
           'sync_notes': ''}
        try:
            print multiLocationModule
            start = self.getNowStr()
            task = 'inventory_mage_to_dst'
            lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
            mInventories = self.getMInventory(multiLocationModule)
            lastCutoffEntityId = None
            for mInventory in mInventories:
                syncStatus = 'N'
                syncNotes = 'Magento to DST'
                itemId = mInventory['item_id']
                if itemId > lastCutoffEntityId:
                    lastCutoffEntityId = itemId
                self.dstCursor.execute(self.queries['insertMInventorySQL'], [
                 mInventory['item_id'],
                 mInventory['sku'],
                 mInventory['website_code'],
                 mInventory['qty'],
                 mInventory['is_in_stock'],
                 mInventory['is_in_stock'],
                 syncStatus,
                 syncNotes])
                self.logger.info(('{0} {1} Magento to DST').format(mInventory['sku'], mInventory['website_code']))

            if lastCutoffEntityId:
                syncStatus = 'O'
                lastCutoffDt = start
                lastStartDt = start
                lastEndDt = self.getNowStr()
                syncNotes = 'Sync from Magento to DST'
                self.dstControl.insertSyncControl(task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes)
            else:
                syncStatus = 'I'
                syncNotes = 'No product inventory needs to sync'
            syncResult['sync_status'] = syncStatus
            syncResult['sync_notes'] = syncNotes
        except Exception as e:
            error = traceback.format_exc()
            print error
            syncResult['sync_status'] = 'F'
            syncResult['sync_notes'] = error

        return syncResult

    def importGroupPrice(self, product):
        sku = product['sku']
        websiteCode = product['website_code']
        syncResult = {'id': product['id'], 
           'action': '', 
           'sku': sku, 
           'website_code': websiteCode, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        customerGroupId = self.getCustomerGroupIdByCode(product['customer_group'])
        if productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Product {0} does not existed in Magento').format(sku)
        elif customerGroupId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Customer group {0} does not existed in Magento').format(product['customer_group'])
        else:
            try:
                isProtected = self.isValueProtected(productId, 'price')
                if isProtected:
                    syncResult['sync_status'] = 'I'
                    syncResult['sync_notes'] = ('Stock is protected in Magento').format(sku)
                else:
                    if websiteCode not in self.websites:
                        websiteId = 0
                    else:
                        websiteId = self.websites[product['website_code']]['id']
                    if product['all_groups'] is None:
                        allGroups = 1
                    else:
                        allGroups = product['all_groups']
                    param = [productId,
                     allGroups,
                     customerGroupId,
                     websiteId,
                     product['price'],
                     product['price']]
                    self.mageCursor.execute(self.queries['insOrUpdGroupPriceSQL'], param)
                    syncResult['sync_status'] = 'O'
                    syncResult['sync_notes'] = 'Sync group price to Magento'
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Group price Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, group: {1} status: {2} notes: {3}').format(sku, product['customer_group'], syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def importGroupTierPrice(self, product):
        sku = product['sku']
        websiteCode = product['website_code']
        syncResult = {'id': product['id'], 
           'action': '', 
           'sku': sku, 
           'website_code': websiteCode, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        customerGroupId = self.getCustomerGroupIdByCode(product['customer_group'])
        if productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Product {0} does not existed in Magento').format(sku)
        elif customerGroupId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Customer group {0} does not existed in Magento').format(product['customer_group'])
        else:
            try:
                isProtected = self.isValueProtected(productId, 'price')
                if isProtected:
                    syncResult['sync_status'] = 'I'
                    syncResult['sync_notes'] = ('Stock is protected in Magento').format(sku)
                else:
                    if websiteCode not in self.websites:
                        websiteId = 0
                    else:
                        websiteId = self.websites[product['website_code']]['id']
                    if product['all_groups'] is None:
                        allGroups = 1
                    else:
                        allGroups = product['all_groups']
                    param = [productId,
                     allGroups,
                     customerGroupId,
                     websiteId,
                     product['qty'],
                     product['price'],
                     product['price']]
                    self.mageCursor.execute(self.queries['insOrUpdGroupTierPriceSQL'], param)
                    syncResult['sync_status'] = 'O'
                    syncResult['sync_notes'] = 'Sync group tier price to Magento'
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Group tier price Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, group: {1}, qty: {2} status: {3} notes: {4}').format(sku, product['customer_group'], product['qty'], syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def getCompanyIdByCode(self, companyCode):
        self.mageCursor.execute(self.queries['getCompanyIdByCodeSQL'], [companyCode])
        companyId = 0
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            companyId = res[0]
        return companyId

    def importCompanyTierPrice(self, product):
        sku = product['sku']
        websiteCode = product['website_code']
        syncResult = {'id': product['id'], 
           'action': '', 
           'sku': sku, 
           'website_code': websiteCode, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        companyId = self.getCompanyIdByCode(product['company_code'])
        if productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Product {0} does not existed in Magento').format(sku)
        elif companyId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Company {0} does not existed in Magento').format(product['company_code'])
        else:
            try:
                isProtected = self.isValueProtected(productId, 'price')
                if isProtected:
                    syncResult['sync_status'] = 'I'
                    syncResult['sync_notes'] = ('Price is protected in Magento').format(sku)
                else:
                    if websiteCode not in self.websites:
                        websiteId = 0
                    else:
                        websiteId = self.websites[product['website_code']]['id']
                    param = [productId,
                     product['company_code'],
                     websiteId,
                     product['qty'],
                     product['price'],
                     product['price']]
                    self.mageCursor.execute(self.queries['insOrUpdCompanyPriceSQL'], param)
                    syncResult['sync_status'] = 'O'
                    syncResult['sync_notes'] = 'Sync company price to Magento'
            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Company price Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, company: {1}, qty: {2} status: {3} notes: {4}').format(sku, product['company_code'], product['qty'], syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def getRootCategoryByStore(self, storeCode):
        self.mageCursor.execute(self.queries['getRootCategoryByStoreSQL'], [storeCode])
        res = self.mageCursor.fetchone()
        if res is not None:
            rootCategoryId = int(res[0])
        else:
            rootCategoryId = 2
        rootCategoryValue = self.getAttributeValue('catalog_category', self._categoryValueAttributeCode, rootCategoryId, 0)
        rootCategory = {'id': rootCategoryId, 
           'value': rootCategoryValue}
        return rootCategory

    def getMaxCategoryId(self):
        self.mageCursor.execute(self.queries['getMaxCategoryIdSQL'])
        res = self.mageCursor.fetchone()
        maxCategoryId = int(res[0])
        return maxCategoryId

    def insertCatalogCategoryEntity(self, currentPathIds, attributeSetName='Default'):
        ids = self.getAttributeSetIdEntityTypeId('catalog_category', attributeSetName)
        if ids == None:
            return 0
        else:
            entityId = self.getMaxCategoryId() + 1
            parentId = currentPathIds[(-1)]
            level = len(currentPathIds)
            pathIds = currentPathIds[:]
            pathIds.append(entityId)
            path = ('/').join([ str(pathId) for pathId in pathIds ])
            childrenCount = 0
            position = 0
            self.mageCursor.execute(self.queries['insertCatalogCategoryEntitySQL'], [
             entityId, ids['attribute_set_id'], parentId, path, level, childrenCount, position])
            categoryId = self.mageCursor.lastrowid
            return categoryId

    def createCategory(self, currentPathIds, category):
        categoryId = self.insertCatalogCategoryEntity(currentPathIds)
        urlKey = re.sub('[^0-9a-zA-Z ]+', '', category).replace(' ', '-').lower()
        categoryEavData = {self._categoryValueAttributeCode: [
                                            [
                                             categoryId, category]], 
           'url_key': [
                     [
                      categoryId, urlKey]], 
           'url_path': [
                      [
                       categoryId, urlKey]]}
        for code, value in self._categoryEavDataDefaults.items():
            if code not in categoryEavData:
                categoryEavData[code] = [
                 [
                  categoryId, value]]

        if self._categoryValueAttributeCode != 'name':
            categoryEavData['name'] = [
             [
              categoryId, category]]
        for k, v in categoryEavData.items():
            if len(v) > 0:
                entity = MagentoEntity(self.mageCursor, k, 'catalog_category', 0, self._entityLogConf)
                entity._mageConf = self.mageConf
                entity._multiSelectValueDelimiter = self._multiSelectValueDelimiter
                entity._intValueAttributes.append('is_active')
                entity._intValueAttributes.append('is_anchor')
                entity._intValueAttributes.append('include_in_menu')
                entity._intValueAttributes.append('custom_use_parent_settings')
                entity._intValueAttributes.append('custom_apply_to_products')
                entity.setProperties()
                entity.readData(v)
                entity.loadData()
                del entity

        return categoryId

    def assignProductCategoryByLowestLevel(self, sku, productId, currentPathIds, category, dataType='varchar', througApi=False):
        getMatchedCategoriesSQL = self.queries['getMatchedCategoriesSQL'].format(dataType=dataType)
        path = self._categoryPathDelimeter.join(currentPathIds) + '/%'
        self.mageCursor.execute(getMatchedCategoriesSQL, [currentPathIds, category])
        res = self.mageCursor.fetchall()
        notes = ''
        if res is not None and len(res) > 0:
            for r in res:
                categoryId = r[0]
                if througApi == True:
                    self.linkCatalogCategory(sku, categoryId)
                else:
                    self.setProductCategory(productId, categoryId)
                notes = notes + ('\n assign product id:{0} to category id: {1} API? : {2}').format(productId, categoryId, througApi)

        else:
            notes = ('No matched category: productId:{0}, currentPathIds: {1}, category: {2}').format(productId, currentPathIds, category)
        return notes

    def createCategoryThrougAPI(self, currentPathIds, category):
        parentId = currentPathIds[(-1)]
        level = len(currentPathIds)
        childrenCount = 0
        position = 0
        categoryData = {'category': {'parentId': parentId, 
                        'name': category, 
                        'isActive': self._categoryEavDataDefaults['is_active'], 
                        'position': position, 
                        'level': level, 
                        'children': childrenCount, 
                        'availableSortBy': [], 'includeInMenu': self._categoryEavDataDefaults['include_in_menu'], 
                        'extensionAttributes': {}, 'customAttributes': []}}
        mCategory = self.mageApi.createCategory(categoryData)
        return mCategory['id']

    def linkCatalogCategory(self, sku, categoryId):
        productCategoryData = {'productLink': {'sku': sku, 
                           'categoryId': categoryId}}
        linkResult = self.mageApi.linkCatalogCategory(productCategoryData, categoryId)

    def getCategoryId(self, level, parentId, category):
        categoryId = None
        attributeMetadata = self.getAttributeMetadata(self._categoryValueAttributeCode, 'catalog_category')
        dataType = attributeMetadata['backend_type']
        getCategoryIdByAttributeValueAndPathSQL = self.queries['getCategoryIdByAttributeValueAndPathSQL'].format(dataType=dataType)
        self.mageCursor.execute(getCategoryIdByAttributeValueAndPathSQL, [
         level, parentId, category])
        print self.mageCursor._last_executed
        res = self.mageCursor.fetchone()
        print res
        if res is not None and len(res) > 0:
            categoryId = res[0]
        return categoryId

    def getCategoryIdThroughApi(self, level, parentId, category):
        categoryId = None
        categoryData = self.mageApi.getCategoryData(level, parentId)
        if categoryData and 'children_data' in categoryData:
            for subCategory in categoryData['children_data']:
                if subCategory['name'] == category:
                    categoryId = subCategory['id']

        return categoryId

    def importProductCategory(self, eProductCategory, througApi=False):
        sku = eProductCategory['sku']
        action = eProductCategory['action']
        path = eProductCategory['path']
        storeCode = eProductCategory['store_code']
        syncResult = {'id': eProductCategory['id'], 
           'action': action, 
           'sku': sku, 
           'path': path, 
           'sync_status': 'F', 
           'sync_notes': 'DST to Magento'}
        self.websites = self.getWebsites()
        self.stores = self.getStores()
        productId = self.getProductIdBySku(sku)
        attributeMetadata = self.getAttributeMetadata(self._categoryValueAttributeCode, 'catalog_category')
        if path is None or path.strip() == '':
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Path is empty for {0}').format(sku)
        elif productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Product {0} does not existed in Magento').format(sku)
        elif attributeMetadata is None:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Attribute {0} does not existed for category in Magento').format(self._categoryValueAttributeCode)
        else:
            path = self._rootCategories + path
            if storeCode is None or storeCode.strip() == '':
                storeCode = 'defalut'
            categories = path.split(self._categoryPathDelimeter)
            if self._includeRootCategory == False:
                rootCategory = self.getRootCategoryByStore(storeCode)
                categories.insert(0, rootCategory['value'])
            try:
                parentId = 1
                currentPathIds = [1]
                for idx in range(0, len(categories)):
                    currentPath = self._categoryPathDelimeter.join(categories[0:idx + 1])
                    categoryId = None
                    category = categories[idx]
                    if category == '%':
                        notes = self.assignProductCategoryByLowestLevel(sku, productId, currentPathIds, categories[(-1)], dataType)
                        notes = notes + ('\nSet product: {0} category: {1} by the lowest level function.').format(sku, path)
                        syncResult['sync_notes'] = syncResult['sync_notes'] + notes
                        break
                    level = idx + 1
                    categoryId = None
                    categoryId = self.getCategoryId(level, parentId, category)
                    if categoryId is None and self._createCategoryDynamic == True:
                        if througApi == True:
                            categoryId = self.createCategoryThrougAPI(currentPathIds, category)
                        else:
                            print currentPathIds
                            categoryId = self.createCategory(currentPathIds, category)
                    if categoryId is None:
                        syncResult['sync_status'] = 'F'
                        syncResult['sync_notes'] = ('Category {0} does not existed and is not created').format(currentPath)
                    else:
                        if self._assignProductToAllLevels == True:
                            if level == 1:
                                parentId = categoryId
                                currentPathIds.append(categoryId)
                                continue
                            elif througApi == True:
                                self.linkCatalogCategory(sku, categoryId)
                            else:
                                self.setProductCategory(productId, categoryId)
                            notes = ('Assgin product {0} to category: {1} API?: {2}').format(sku, currentPath, througApi)
                            syncResult['sync_notes'] = syncResult['sync_notes'] + notes
                        elif level == len(categories):
                            if througApi == True:
                                self.linkCatalogCategory(sku, categoryId)
                            else:
                                self.setProductCategory(productId, categoryId)
                            notes = ('Assgin product {0} to category: {1} API?: {2}').format(sku, currentPath, througApi)
                            syncResult['sync_notes'] = syncResult['sync_notes'] + notes
                        currentPathIds.append(categoryId)
                        parentId = categoryId
                    syncResult['sync_status'] = 'O'

            except Exception as e:
                syncResult['sync_status'] = 'F'
                syncResult['sync_notes'] = ('Product Category Sync Failed: {0}').format(traceback.format_exc())

        self.logger.info(('sku: {0}, category: {1} status: {2} notes: {3}').format(sku, path, syncResult['sync_status'], syncResult['sync_notes']))
        return syncResult

    def refreshUrlRewriteThroughAPI(self, productId, mProduct):
        sku = mProduct['sku']
        syncResult = {'action': '', 
           'sku': sku, 
           'product_id': productId, 
           'sync_status': 'F', 
           'sync_notes': 'Refresh URL Rewrite'}
        productData = self.mageApi.getProductData(sku)
        if productData is None:
            log = ('Failed to get product data for {0}').format(sku)
            self.logger.error(log)
            syncResult['sync_result'] = log
            return syncResult
        else:
            urlKey = mProduct['url_key']
            urlKeyAttributeData = {'attribute_code': 'url_key', 
               'value': urlKey}
            for customAttribute in productData['custom_attributes']:
                if customAttribute['attribute_code'] == 'url_key':
                    productData['custom_attributes'].remove(customAttribute)
                    break

            productData['custom_attributes'].append(urlKeyAttributeData)
            postData = {'product': productData}
            postResult = self.mageApi.updateProductData(sku, postData)
            log = ('Successfully update url_key to {0} for product {1}').format(urlKey, sku)
            self.logger.info(log)
            syncResult['sync_status'] = 'O'
            syncResult['sync_result'] = log
            return

    def importCustomOptions(self, productId, formattedProductJsonObj, syncResult):
        log = ''
        if 'custom_options' in formattedProductJsonObj:
            for customOption in formattedProductJsonObj['custom_options']:
                optionId = self.getCustomOptionIdByTitle(productId, customOption['title'])
                if optionId is None:
                    optionId = self.insertCustomOption(productId, customOption)
                    log = ('Custom Option {0} is inserted for {1}').format(customOption['title'], formattedProductJsonObj['sku'])
                else:
                    log = ('Custom Option {0} is existed for: {1}').format(customOption['title'], formattedProductJsonObj['sku'])
                    self.logger.info(log)

            if 'require_custom_option' in formattedProductJsonObj:
                requireOption = formattedProductJsonObj['require_custom_option']
            else:
                requireOption = 0
            self.mageCursor.execute(self.queries['updateProductCustomOptionSQL'], [1, requireOption, productId])
        elif self._removeCustomOptions == True:
            self.mageCursor.execute(self.queries['updateProductCustomOptionSQL'], [0, 0, productId])
            self.mageCursor.execute(self.queries['deleteProductCustomOptionSQL'], [productId])
            log = ('Remove custom option for {0}').format(formattedProductJsonObj['sku'])
            self.logger.info(log)
        syncResult['sync_notes'] = log
        return syncResult

    def getCustomOptionIdByTitle(self, productId, title):
        self.mageCursor.execute(self.queries['getCustomOptionIdByTitleSQL'], [productId, title])
        optionId = None
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            optionId = res[0]
        return optionId

    def insertCustomOption(self, productId, customOption):
        self.mageCursor.execute(self.queries['insertCatalogProductOptionSQL'], [
         productId, customOption['type'], customOption['is_require'],
         customOption['sku'], customOption['max_characters'], customOption['file_extension'],
         customOption['image_size_x'], customOption['image_size_y'], customOption['sort_order']])
        optionId = self.mageCursor.lastrowid
        self.mageCursor.execute(self.queries['insertCustomOptionTitleSQL'], [
         optionId, 0, customOption['title']])
        optionTitleId = self.mageCursor.lastrowid
        self.mageCursor.execute(self.queries['insertCustomOptionPriceSQL'], [
         optionId, 0, customOption['price'], customOption['price_type']])
        optionPriceId = self.mageCursor.lastrowid
        log = ('product_id/option_id/option_title_id/option_price_id:{0}/{1}/{2}/{3}').format(productId, optionId, optionTitleId, optionPriceId)
        self.logger.info(log)
# okay decompiling MagentoProduct.pyc
