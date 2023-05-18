# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: C:\magedst\astro\MageDstSyncAgent.py
# Compiled at: 2017-04-28 03:50:12
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
                    syncResult = {'id': customer['id'], 
                       'email': email, 
                       'm_json_data': customer['m_json_data'], 
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
                param = [syncResult['m_json_data'], syncResult['sync_status'], syncResult['sync_notes'], syncResult['id']]
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
            urlKey = {'entity_id': result[0], 
               'sku': result[1], 
               'name': result[2], 
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
# okay decompiling MageDstSyncAgent.pyc
