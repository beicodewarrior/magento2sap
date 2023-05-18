# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/MageDstSyncAgent.py
# Compiled at: 2021-04-20 08:24:51
import sys
sys.path.insert(0, '..')
import json, traceback
from MAGE2.MageDSTSync import MagentoDSTSync

class MageDSTSyncAstro(MagentoDSTSync):

    def __init__(self, mage_conf, dst_conf):
        MagentoDSTSync.__init__(self, mage_conf, dst_conf)

    def updatePrintApplication(self):
        self.mageApi = None
        sql = '\n            SELECT R.parent_id, C.value parent_print_application, R.child_id, S.value child_print_application\n            FROM catalog_product_relation R\n            LEFT JOIN catalog_product_entity_text C ON R.parent_id = C.entity_id AND C.attribute_id = 179\n            LEFT JOIN catalog_product_entity_text S ON R.child_id = S.entity_id AND S.attribute_id = 179\n            ORDER BY R.parent_id, R.child_id;\n        '
        self.mageCursor.execute(sql)
        results = self.mageCursor.fetchall()
        for result in results:
            if result[1] is not None and result[3] is None:
                sql = '\n                    INSERT INTO catalog_product_entity_text (store_id, attribute_id, entity_id, value)\n                    VALUE (0, 179, %s, %s)\n                    ON DUPLICATE KEY UPDATE value = %s;\n                '
                self.mageCursor.execute(sql, (result[2], result[1], result[1]))

        self.mageConn.commit()
        return

    def syncCustomerGroupToMage(self):
        self.mageApi = None
        try:
            params = self.generateDstQueryParams(['N'])
            self.dstCursor.execute(self.dstQueries['listECustomersSQL'], params)
            customers = self.fetchCursorResultAsDict(self.dstCursor)
            customerGroup = {}
            if len(customers) > 0:
                self.mageCursor.execute('SELECT * FROM customer_group')
                results = self.fetchCursorResultAsDict(self.mageCursor)
                for result in results:
                    customerGroup[result['customer_group_code']] = result['customer_group_id']

            syncResults = []
            for customer in customers:
                try:
                    email = customer['email']
                    customerData = json.loads(customer['e_json_data'])
                    groupCode = None
                    if 'ListName' in customerData:
                        groupCode = customerData['ListName']
                    syncResult = {'id': customer['id'], 'email': email, 'm_json_data': customer['m_json_data'], 
                       'sync_status': 'F', 
                       'sync_notes': 'Customer Group DST to Magento'}
                    if groupCode is None or len(groupCode.strip()) <= 0 or groupCode not in customerGroup:
                        syncResult['sync_status'] = 'I'
                        syncResult['sync_notes'] = ('Can not find customer group: {}').format(groupCode)
                    else:
                        self.mageCursor.execute('SELECT entity_id FROM customer_entity WHERE email = %s', [email])
                        result = self.mageCursor.fetchone()
                        if result is None:
                            syncResult['sync_status'] = 'I'
                            syncResult['sync_notes'] = ('Can not find customer: {}').format(email)
                        else:
                            customerId = result[0]
                            groupId = customerGroup[groupCode]
                            self.mageCursor.execute('UPDATE customer_entity SET group_id = %s WHERE email = %s', [groupId, email])
                            self.mageCursor.execute('UPDATE customer_grid_flat SET group_id = %s WHERE email = %s', [groupId, email])
                            syncResult['sync_status'] = 'O'
                            syncResult['sync_notes'] = ('Set Customer Group to {}: {}').format(groupId, groupCode)
                    syncResults.append(syncResult)
                except Exception as e:
                    log = traceback.format_exc()
                    self.logger.exception(log)

            self.mageConn.commit()
            for syncResult in syncResults:
                param = [
                 syncResult['m_json_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']]
                self.dstCursor.execute(self.dstQueries['updateECustomerSQL'], param)

            self.dstConn.commit()
        except Exception as e:
            self.dstConn.rollback()
            log = traceback.format_exc()
            self.logger.exception(log)

        return

    def updateUrlKey(self):
        self.mageApi = None
        sql = '\n            SELECT\n                P.entity_id, P.sku, V1.value name, V2.value url_key\n            FROM catalog_product_entity P\n            INNER JOIN catalog_product_entity_varchar V1 ON V1.attribute_id = 70 AND V1.entity_id = P.entity_id\n            LEFT JOIN catalog_product_entity_varchar V2 ON V2.attribute_id = 115 AND V2.entity_id = P.entity_id;\n        '
        self.mageCursor.execute(sql)
        results = self.mageCursor.fetchall()
        urlKeys = []
        for result in results:
            urlKey = {'entity_id': result[0], 'sku': result[1], 'name': result[2], 
               'url_key': result[3]}
            if urlKey['url_key'] is None:
                urlKey['url_key'] = urlKey['name'] + '-' + urlKey['sku']
                urlKey['url_key'] = urlKey['url_key'].lower().replace(' - ', '-').replace(' ', '-').replace('.', '-').replace('/', '-').replace("'", '-').replace('"', '').replace('#', '').replace('(', '').replace(')', '')
            urlKeys.append(urlKey)

        insertUrlKeySQL = '\n            INSERT INTO catalog_product_entity_varchar(attribute_id, store_id, entity_id, value)\n            VALUES (115, 0, %s, %s)\n            ON DUPLICATE KEY UPDATE value = %s;\n        '
        insertUrlRewriteURL = "\n            INSERT IGNORE url_rewrite(entity_type, entity_id, request_path, target_path, redirect_type, store_id, is_autogenerated)\n            VALUES ('product', %s, %s, %s, 0, 1, 1);\n        "
        for urlKey in urlKeys:
            self.mageCursor.execute(insertUrlKeySQL, [urlKey['entity_id'], urlKey['url_key'], urlKey['url_key']])
            self.mageCursor.execute(insertUrlRewriteURL, [urlKey['entity_id'], urlKey['url_key'] + '.html', 'catalog/product/view/id/' + str(urlKey['entity_id'])])

        self.mageConn.commit()
        return

    def updateTierPriceLevel(self):
        self.mageApi = None
        getGroupTierSQL = '\n            SELECT\n                customer_group_id, qty\n            FROM catalog_product_entity_tier_price\n            GROUP BY customer_group_id, qty\n            ORDER BY customer_group_id, qty;\n        '
        self.mageCursor.execute(getGroupTierSQL)
        results = self.mageCursor.fetchall()
        counter = {}
        tierPriceLevels = {}
        for groupId, qty in results:
            groupId = str(groupId)
            qty = str(float(qty))
            if groupId not in counter:
                counter[groupId] = 1
            if groupId not in tierPriceLevels:
                tierPriceLevels[groupId] = {}
            if qty not in tierPriceLevels[groupId]:
                tierPriceLevels[groupId][qty] = counter[groupId]
            counter[groupId] = counter[groupId] + 1

        getTierPriceLevelSQL = "\n            SELECT\n                email, group_id, value AS tier_price_level\n            FROM customer_entity\n            INNER JOIN customer_group ON customer_group.customer_group_id = customer_entity.group_id\n            INNER JOIN customer_entity_varchar ON customer_entity_varchar.entity_id = customer_entity.entity_id\n            WHERE customer_entity_varchar.attribute_id =\n                (SELECT attribute_id FROM eav_attribute WHERE attribute_code = 'tier_price_level' and entity_type_id =\n                    (SELECT entity_type_id FROM eav_entity_type WHERE entity_type_code = 'customer')\n                );\n        "
        updateTierPriceLevelSQL = "\n            UPDATE customer_entity_varchar SET value = %s\n            WHERE entity_id = (SELECT entity_id FROM customer_entity WHERE email = %s)\n            AND attribute_id =\n                (SELECT attribute_id FROM eav_attribute WHERE attribute_code = 'tier_price_level' and entity_type_id =\n                    (SELECT entity_type_id FROM eav_entity_type WHERE entity_type_code = 'customer')\n                );\n        "
        self.mageCursor.execute(getTierPriceLevelSQL)
        results = self.mageCursor.fetchall()
        for email, groupId, tierPriceLevel in results:
            groupId = str(groupId)
            tierPriceLevel = str(float(tierPriceLevel))
            if groupId in tierPriceLevels:
                if tierPriceLevel in tierPriceLevels[groupId]:
                    newTierPriceLevel = tierPriceLevels[groupId][tierPriceLevel]
                    self.mageCursor.execute(updateTierPriceLevelSQL, [newTierPriceLevel, email])

        self.mageConn.commit()
        return

    def setTotalSheets(self):
        self.mageApi = None
        getNoTotalSheetsSQL = '\n            SELECT entity_id\n            FROM (  SELECT t0.entity_id, t0.sku\n                    FROM catalog_product_entity t0, catalog_product_entity_int t1\n                    WHERE   t0.entity_id = t1.entity_id\n                        AND t1.attribute_id = 140\n                        AND t1.value = 2710) S1\n            WHERE S1.entity_id NOT IN\n                (   SELECT DISTINCT product_id\n                    FROM catalog_product_option t0, catalog_product_option_title t1\n                    WHERE   t0.option_id = t1.option_id\n                        AND t1.title like "Total Sheets")\n            ORDER BY entity_id;\n        '
        insertOptionSQL = "\n            INSERT INTO catalog_product_option (product_id, type, is_require, max_characters)\n            VALUES (%s, 'field', 0, 0);\n        "
        insertOptionTitleSQL = "\n            INSERT INTO catalog_product_option_title (option_id, store_id, title)\n            VALUES (%s, 0, 'Total Sheets'), (%s, 1, 'Total Sheets');\n        "
        insertOptionPriceSQL = "\n            INSERT INTO catalog_product_option_price (option_id, store_id, price, price_type)\n            VALUES (%s, 0, 0, 'fixed');\n        "
        self.mageCursor.execute(getNoTotalSheetsSQL)
        results = self.mageCursor.fetchall()
        for result in results:
            entityId = result[0]
            self.mageCursor.execute(insertOptionSQL, (entityId,))
            optionId = self.mageCursor.lastrowid
            self.mageCursor.execute(insertOptionTitleSQL, (optionId, optionId))
            self.mageCursor.execute(insertOptionPriceSQL, (optionId,))

        self.mageConn.commit()
        return