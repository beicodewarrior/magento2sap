# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/MagentoOrderAgent.py
# Compiled at: 2021-02-02 15:49:17
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
        self._customOptionMatrix = {'Width Dimension': 'custom_cut_width', 'Length Dimension': 'custom_cut_length', 
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
            productOptions = json.loads(productOptionsStr)
            if type(productOptions) == str:
                enc = productOptions.encode('utf-8')
                productOptions = json.loads(enc)
            try:
                if 'options' in productOptions['info_buyRequest']:
                    if type(productOptions['info_buyRequest']['options']) == dict:
                        for optionId, value in productOptions['info_buyRequest']['options'].items():
                            title = self.getCustomOptionTitleById(optionId)
                            if title in self._customOptionMatrix:
                                customOptions[self._customOptionMatrix[title]] = value

            except Exception as ex:
                print 'Error Order item ID ', orderItemId
                print 'Exception - ', ex

        return customOptions

    def insertMOrderItemExt(self, orderItem):
        print orderItem
        customOptions = self.getOrderItemCustomOptions(orderItem['id'])
        sql = 'UPDATE m_order_item SET '
        keys = []
        values = []
        for key, value in customOptions.items():
            keys.append(key + '=%s')
            if key in ('custom_cut_width', 'custom_cut_length', 'custom_cut_total_cut') and value in ('', ):
                values.append(0)
            else:
                values.append(value)

        sql = sql + (',').join(keys) + ' WHERE id = %s '
        values.append(orderItem['id'])
        if len(customOptions) > 0:
            self.dstCursor.execute(sql, values)
            self.logger.info(('Update custom option for order item id: {0}').format(orderItem['id']))
        else:
            self.logger.info(('No custom option for order item id: {0}').format(orderItem['id']))