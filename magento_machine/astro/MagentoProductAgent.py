# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/MagentoProductAgent.py
# Compiled at: 2017-05-03 04:50:55
import sys
sys.path.insert(0, '..')
from MAGE2.MagentoProduct import MagentoProduct
from MAGE2.MagentoCommon import MagentoApi
import json

class MagentoProductAstro(MagentoProduct):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoProduct.__init__(self, mageConf, mageConn, mageApi, dstCursor)
        self._attributeSetNameMatrix = {'Box': 'Box', 
           'Envelope': 'Envelope', 
           'Paper': 'Paper'}
        self._productTypeMatrix = {'Configurable': 'configurable', 
           'Simple': 'simple'}
        self.productAttributesMap = {'action': 'Sync', 
           'sku': 'sku', 
           'attribute_set_name': 'Attr_Set', 
           'website_code': '', 
           'type_id': 'ProductType', 
           'status': 'validFor', 
           'visibility': '', 
           'tax_class_id': '', 
           'brand': 'Brand', 
           'color': 'Color', 
           'description': 'long_desc', 
           'envelop_color': 'Color', 
           'envelop_format': 'Env_Format', 
           'envelop_size': 'Env_Type', 
           'manufacturer': 'Manufacturer', 
           'name': 'name', 
           'paper_category': 'Category', 
           'paper_color': 'Color', 
           'paper_finish': 'Finish', 
           'paper_grain_direction': 'Grain_Direction', 
           'paper_sheet_per_box': 'Pack_Size', 
           'paper_size': 'Size', 
           'paper_thickness': 'Thickness', 
           'paper_weight': 'Paper_Weight', 
           'short_description': 'short_desc', 
           'weight': 'Weight', 
           'acid_free': 'Acid_Free', 
           'recycled': 'Recycled', 
           'laser_compatible': 'Laser_Compatible', 
           'fsc_certified': 'FSC_Certified', 
           'cotton_100_percent': 'Cotton', 
           'tree_free': 'Tree_Free', 
           'width': 'Width', 
           'length': 'Length', 
           'specific_color': 'Spec_Color', 
           'envelop_type': 'Env_Type', 
           'print_application': 'print_application'}
        self._yesNoAttributes = [
         'laser_compatible', 'recycled', 'fsc_certified',
         'cotton_100_percent', 'acid_free', 'tree_free']
        self._updateOptionValueAttributes = [
         'brand', 'color', 'envelop_color', 'envelop_format',
         'manufacturer', 'paper_category', 'paper_color', 'paper_finish',
         'paper_grain_direction', 'paper_sheet_per_box', 'paper_size', 'envelop_size',
         'paper_thickness', 'paper_weight', 'specific_color', 'envelop_type']
        self.productDefaults = {'attribute_set_name': 'Default', 
           'website_code': 'base', 
           'store_code': 'admin', 
           'status': '1', 
           'type_id': 'simple', 
           'visibility': '4', 
           'tax_class_id': '2', 
           'qty': 0, 
           'is_in_stock': 1, 
           'stock_status': 1}
        self._inventoryDefaultConfig['default_website_id'] = 0
        self._includeRootCategory = True
        self._categoryPathDelimeter = '->'
        self._createCategoryDynamic = True
        self._assignProductToAllLevels = True
        self._categoryValueAttributeCode = 'name'
        self._rootCategories = 'Default Category->'
        self._importCustomOption = True
        self._removeCustomOptions = False
        self.queries['setStockItemSQL'] = '\n            INSERT INTO  cataloginventory_stock_item\n            (product_id,stock_id,qty,is_in_stock,website_id,backorders,use_config_backorders,use_config_enable_qty_inc,enable_qty_increments)\n            VALUES (%s,%s,%s,%s,%s,1,0,0,0)\n            ON DUPLICATE KEY UPDATE\n            qty = %s,\n            is_in_stock = %s,\n            backorders = 1,\n            use_config_backorders = 0,\n            use_config_enable_qty_inc = 0,\n            enable_qty_increments = 0\n        '
        self.queries['updateQtyUsesDecimalsSQL'] = '\n            UPDATE  cataloginventory_stock_item\n            SET\n            is_qty_decimal = 1\n            WHERE product_id = %s\n        '
        self._alwaysInStock = True
        self._categoryEavDataDefaults['include_in_menu'] = '1'

    def convertYesNoValue(self, value):
        if value == 'Y':
            return '1'
        if value == 'N':
            return '0'
        return value

    def generateCustomOptionsJson(self, formattedProductJsonObj):
        formattedProductJsonObj['custom_options'] = [
         {'type': 'field', 
            'is_require': 0, 
            'sku': None, 
            'max_characters': 0, 
            'file_extension': None, 
            'image_size_x': None, 
            'image_size_y': None, 
            'sort_order': 0, 
            'price': 0, 
            'price_type': 'fixed', 
            'title': 'Length Dimension'},
         {'type': 'field', 
            'is_require': 0, 
            'sku': None, 
            'max_characters': 0, 
            'file_extension': None, 
            'image_size_x': None, 
            'image_size_y': None, 
            'sort_order': 1, 
            'price': 0, 
            'price_type': 'fixed', 
            'title': 'Width Dimension'},
         {'type': 'field', 
            'is_require': 0, 
            'sku': None, 
            'max_characters': 0, 
            'file_extension': None, 
            'image_size_x': None, 
            'image_size_y': None, 
            'sort_order': 2, 
            'price': 0, 
            'price_type': 'fixed', 
            'title': 'Total Cut'}]
        return formattedProductJsonObj

    def generateTotalSheetsCustomOptions(self, formattedProductJsonObj):
        totalSheetsFlag = False
        totalSheetsCustomOption = {'type': 'field', 
           'is_require': 0, 
           'sku': None, 
           'max_characters': 0, 
           'file_extension': None, 
           'image_size_x': None, 
           'image_size_y': None, 
           'sort_order': 3, 
           'price': 0, 
           'price_type': 'fixed', 
           'title': 'Total Sheets'}
        if 'custom_options' in formattedProductJsonObj:
            for customOption in formattedProductJsonObj['custom_options']:
                if customOption['title'] == 'Total Sheets':
                    totalSheetsFlag = True
                    break

            if totalSheetsFlag == False:
                formattedProductJsonObj['custom_options'].append(totalSheetsCustomOption)
        else:
            totalSheetsCustomOption['sort_order'] = 0
            formattedProductJsonObj['custom_options'] = [totalSheetsCustomOption]
        return formattedProductJsonObj

    def formatProductJsonExt(self, formattedProductJsonObj, sourceProduct, productAttributesMap):
        if formattedProductJsonObj['action'] == 'N':
            formattedProductJsonObj['action'] = 'disable'
        else:
            if formattedProductJsonObj['action'] is None:
                formattedProductJsonObj['action'] = 'ignore'
            if formattedProductJsonObj['status'] == 'Y':
                formattedProductJsonObj['status'] = '1'
            else:
                formattedProductJsonObj['status'] = '2'
            for attributeCode in self._yesNoAttributes:
                formattedProductJsonObj[attributeCode] = self.convertYesNoValue(formattedProductJsonObj[attributeCode])

        attributeSetName = formattedProductJsonObj['attribute_set_name']
        if attributeSetName in self._attributeSetNameMatrix:
            formattedProductJsonObj['attribute_set_name'] = self._attributeSetNameMatrix[attributeSetName]
        else:
            formattedProductJsonObj['attribute_set_name'] = self.productDefaults['attribute_set_name']
        typeId = formattedProductJsonObj['type_id']
        if typeId in self._productTypeMatrix:
            formattedProductJsonObj['type_id'] = self._productTypeMatrix[typeId]
        else:
            formattedProductJsonObj['type_id'] = self.productDefaults['type_id']
        formattedProductJsonObj['price'] = '9999'
        if formattedProductJsonObj['type_id'] == 'configurable':
            formattedProductJsonObj['qty'] = 100
            formattedProductJsonObj['price'] = '0.01'
            if formattedProductJsonObj['attribute_set_name'] == 'Paper':
                formattedProductJsonObj = self.generateCustomOptionsJson(formattedProductJsonObj)
            formattedProductJsonObj = self.generateTotalSheetsCustomOptions(formattedProductJsonObj)
        if formattedProductJsonObj['attribute_set_name'] == 'Envelope':
            del formattedProductJsonObj['paper_size']
            del formattedProductJsonObj['color']
            del formattedProductJsonObj['paper_color']
        else:
            del formattedProductJsonObj['envelop_size']
            del formattedProductJsonObj['color']
            del formattedProductJsonObj['envelop_color']
            del formattedProductJsonObj['envelop_type']
            del formattedProductJsonObj['envelop_format']
        return formattedProductJsonObj

    def importInvenoryExt(self, productId, product, syncResult):
        syncResult = {'sync_status': 'O', 
           'sync_notes': ''}
        sheetPerBox = self.getAttributeValue('catalog_product', 'paper_sheet_per_box', productId)
        if sheetPerBox == 'M':
            self.mageCursor.execute(self.queries['updateQtyUsesDecimalsSQL'], [productId])
            syncResult['sync_notes'] = ('Update Qty Uses Decimals to Yes for {0}').format(product['sku'])
        return syncResult