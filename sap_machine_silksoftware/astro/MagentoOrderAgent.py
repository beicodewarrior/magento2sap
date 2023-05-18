# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: C:\magedst\astro\MagentoOrderAgent.py
# Compiled at: 2017-04-28 03:51:54
import sys
sys.path.insert(0, '..')
from MAGE2.MagentoOrder import MagentoOrder
from MAGE2.MagentoCommon import MagentoApi
import json, phpserialize

class MagentoOrderAstro(MagentoOrder):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoOrder.__init__(self, mageConf, mageConn, mageApi, dstCursor)
        _defaultECustomerId = "'C20000'"
        _cardCodePrefix = '"M"'
        _eCustomerIdSQL = ('\n            CASE\n                WHEN sales_order.customer_id IS NULL THEN {0}\n                ELSE CONCAT("C",{1},sales_order.customer_id)\n            END\n        ').format(_defaultECustomerId, _cardCodePrefix)
        self.mOrderQueryMap['fields']['e_customer_id'] = _eCustomerIdSQL
        self._customOptionMatrix = {'Width Dimension': 'custom_cut_width', 
           'Length Dimension': 'custom_cut_length', 
           'Total Cut': 'custom_cut_total_cut'}
        self.queries['getOrderItemProductOptionsSQL'] = '\n            SELECT product_options\n            FROM sales_order_item\n            WHERE item_id = %s\n        '
        self.queries['getCustomOptionTitleByIdSQL'] = '\n            SELECT title\n            FROM catalog_product_option_title\n            WHERE option_id = %s\n        '
        self.mOrderQueryMap['fields']['cut_fee'] = 'IFNULL(sales_order.cut_fee,0)'
        self.mOrderQueryMap['fields']['additional_fee'] = 'IFNULL(sales_order.additiaonal_fee,0)'
        self.mOrderItemQueryMap['fields']['cut_fee'] = 'IFNULL(sales_order_item.cut_fee_details,0)'

    def getCustomOptionTitleById(self, optionId):
        self.mageCursor.execute(self.queries['getCustomOptionTitleByIdSQL'], [optionId])
        title = ''
        res = self.mageCursor.fetchone()
        if res is not None and len(res) > 0:
            title = res[0]
        return title

    def getOrderItemCustomOptions(self, orderItemId):
        self.mageCursor.execute(self.queries['getOrderItemProductOptionsSQL'], [orderItemId])
        res = self.mageCursor.fetchone()
        customOptions = {}
        if res is not None and len(res) > 0:
            productOptionsStr = res[0]
            productOptions = phpserialize.loads(productOptionsStr)
            if type(productOptions) == str:
                productOptions = phpserialize.loads(productOptions)
            if 'options' in productOptions['info_buyRequest']:
                for optionId, value in productOptions['info_buyRequest']['options'].items():
                    title = self.getCustomOptionTitleById(optionId)
                    if title in self._customOptionMatrix:
                        customOptions[self._customOptionMatrix[title]] = value

        return customOptions

    def insertMOrderItemExt(self, orderItem):
        print orderItem
        customOptions = self.getOrderItemCustomOptions(orderItem['id'])
        sql = 'UPDATE m_order_item SET '
        keys = []
        values = []
        for key, value in customOptions.items():
            keys.append(key + '=%s')
            values.append(value)

        sql = sql + (',').join(keys) + ' WHERE id = %s '
        values.append(orderItem['id'])
        if len(customOptions) > 0:
            self.dstCursor.execute(sql, values)
            self.logger.info(('Update custom option for order item id: {0}').format(orderItem['id']))
        else:
            self.logger.info(('No custom option for order item id: {0}').format(orderItem['id']))
# okay decompiling MagentoOrderAgent.pyc
