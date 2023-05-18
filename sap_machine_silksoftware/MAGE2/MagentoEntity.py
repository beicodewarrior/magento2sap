# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoEntity.py
# Compiled at: 2016-06-18 20:45:10
__author__ = 'sandy.tu'
import sys, os
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import MySQLdb, logging

class MagentoEntity(object):

    def __init__(self, cursor, attributeCode, entityTypeCode, storeId=0, entityLog={}):
        if 'logFileName' not in entityLog or entityLog['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            logFileName = entityTypeCode + '.' + attributeCode + '.' + today + '.' + 'log'
        self.cursor = cursor
        if 'logPath' in entityLog and entityLog['logPath'] != '':
            logFileName = entityLog['logPath'] + logFileName
        self.logger = Logger('Entity', logFileName)
        if 'enableLog' in entityLog and entityLog['enableLog'] == True:
            self.logger.logger.setLevel(logging.DEBUG)
        else:
            self.logger.logger.setLevel(logging.WARNING)
        self.attributeCode = attributeCode
        self.entityTypeCode = entityTypeCode
        self.storeId = storeId
        self.entities = []
        self.status = 'init'
        self.abort_reason = ''
        self._mageConf = {'edition': 'enterprise'}
        self._multiSelectValueDelimiter = ','
        self._intValueAttributes = ['status', 'visibility', 'tax_class_id']
        self.sqls = {'getAttributeMetadataSQL': '\n                SELECT DISTINCT t1.attribute_id, t2.entity_type_id, t1.backend_type, t1.frontend_input\n                FROM eav_attribute t1, eav_entity_type t2\n                WHERE t1.entity_type_id = t2.entity_type_id\n                AND t1.attribute_code = %s\n                AND t2.entity_type_code = %s;\n            ', 
           'isEntityExitSQL': '\n                SELECT count(*) FROM entity_code_entity WHERE entity_id = %s\n            ', 
           'isAttributeValueExitSQL': '\n                SELECT count(*)\n                FROM entity_code_entity_data_type\n                WHERE entity_id = %s\n                AND attribute_id = %s\n            ', 
           'updateEntityUpdatedAtSQL': '\n                UPDATE entity_code_entity SET updated_at = %s WHERE entity_id = %s\n            ', 
           'getOptionIdSQL': '\n                SELECT t2.option_id\n                FROM eav_attribute_option t1, eav_attribute_option_value t2\n                WHERE t1.option_id = t2.option_id\n                AND t1.attribute_id = %s\n                AND t2.value = %s;\n            ', 
           'replaceAttributeValueSQL': '\n                REPLACE INTO\n                entity_code_entity_data_type (entity_id, attribute_id, value)\n                values (%s, %s, %s)\n            '}

    def __del__(self):
        del self.logger

    def setProperties(self):
        sql = self.sqls['getAttributeMetadataSQL']
        self.cursor.execute(sql, [self.attributeCode, self.entityTypeCode])
        item = self.cursor.fetchone()
        if item is None or len(item) < 4:
            log = ('Entity Type/Attribute Code: {0}/{1} does not exist').format(self.entityTypeCode, self.attributeCode)
            self.logger.exception(log)
            raise Exception(log)
        self.attributeId = item[0]
        self.entityTypeId = item[1]
        self.frontendInput = item[3]
        if self.attributeCode == 'url_key' and self._mageConf['edition'] == 'enterprise':
            self.dataType = self.attributeCode
        else:
            self.dataType = item[2]
        self.setSQLs()
        return

    def setSQLs(self):
        self.sqls['isEntityExitSQL'] = self.sqls['isEntityExitSQL'].replace('entity_code', self.entityTypeCode)
        self.sqls['isAttributeValueExitSQL'] = self.sqls['isAttributeValueExitSQL'].replace('data_type', self.dataType).replace('entity_code', self.entityTypeCode)
        self.sqls['replaceAttributeValueSQL'] = self.sqls['replaceAttributeValueSQL'].replace('data_type', self.dataType).replace('entity_code', self.entityTypeCode)
        self.sqls['updateEntityUpdatedAtSQL'] = self.sqls['updateEntityUpdatedAtSQL'].replace('entity_code', self.entityTypeCode)
        if self.entityTypeCode == 'catalog_product' or self.entityTypeCode == 'catalog_category':
            cnd = '\nand store_id = %s' % self.storeId
            cols = '(entity_id, attribute_id, store_id, value)'
            vls = '(%s, %s,' + str(self.storeId) + ', %s)'
            self.sqls['isAttributeValueExitSQL'] = self.sqls['isAttributeValueExitSQL'] + cnd
            self.sqls['replaceAttributeValueSQL'] = self.sqls['replaceAttributeValueSQL'].replace('(entity_id, attribute_id, value)', cols)
            self.sqls['replaceAttributeValueSQL'] = self.sqls['replaceAttributeValueSQL'].replace('(%s, %s, %s)', vls)

    def getOptionId(self, attributeId, value):
        sql = self.sqls['getOptionIdSQL']
        self.cursor.execute(sql, [attributeId, value])
        item = self.cursor.fetchone()
        option_id = None
        if item is not None and len(item) > 0:
            option_id = item[0]
        return option_id

    def getMultiSelectIds(self, attributeId, values):
        if values is None:
            return [None]
        else:
            values = values.strip('"').strip("'").strip('\n').strip()
            listValues = [ v.strip() for v in values.split(self._multiSelectValueDelimiter) ]
            listOptionIds = []
            for v in listValues:
                optionId = self.getOptionId(attributeId, v)
                listOptionIds.append(str(optionId))

            optionIds = (',').join(listOptionIds)
            return optionIds

    def readData(self, data):
        for row in data:
            entity = {}
            entity['entity_id'] = row[0]
            entity['attribute_id'] = self.attributeId
            entity['comment'] = ''
            if self.entityTypeCode in ('catalog_product', 'catalog_category') and self.attributeCode in self._intValueAttributes:
                entity['value'] = row[1]
            elif self.dataType == 'int' and self.frontendInput == 'select':
                entity['value'] = self.getOptionId(self.attributeId, row[1])
            elif self.frontendInput == 'multiselect':
                entity['value'] = self.getMultiSelectIds(self.attributeId, row[1])
            else:
                entity['value'] = row[1]
            self.entities.append(entity)

    def loadData(self):
        for entity in self.entities:
            sql = self.sqls['isEntityExitSQL']
            self.cursor.execute(sql, [entity['entity_id']])
            exist = self.cursor.fetchone()
            if exist[0]:
                sql = self.sqls['replaceAttributeValueSQL']
                entity['comment'] = 'replace'
                try:
                    param = [
                     entity['entity_id'], entity['attribute_id'], entity['value']]
                    self.cursor.execute(sql, param)
                except Exception as e:
                    print str(e)
                    self.logger.info(('SQL:{0}, PARAM: {1}').format(sql, param))
                    entity['comment'] = 'entity_id (%s) fail to %s in %s_entity_%s' % (entity['entity_id'], entity['comment'], self.entityTypeCode, self.dataType)
                else:
                    try:
                        now = datetime.utcnow()
                        updatedAt = '%s-%s-%s %s:%s:%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
                        sql = self.sqls['updateEntityUpdatedAtSQL']
                        self.cursor.execute(sql, [updatedAt, entity['entity_id']])
                    except:
                        entity['comment'] = 'entity_id (%s) fail to update updated_at in catalog_product_entity' % entity['entity_id']

            else:
                entity['comment'] = 'entity_id (%s) not found in %s_entity' % (entity['entity_id'], self.entityTypeCode)
# okay decompiling MagentoEntity.pyc
