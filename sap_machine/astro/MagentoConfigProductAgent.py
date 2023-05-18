# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: C:\magedst\astro\MagentoConfigProductAgent.py
# Compiled at: 2017-01-17 19:55:00
import sys
sys.path.insert(0, '..')
from MAGE2.MagentoConfigProduct import MagentoConfigProduct
from MAGE2.MagentoCommon import MagentoApi
import json

class MagentoConfigProductAstro(MagentoConfigProduct):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoConfigProduct.__init__(self, mageConf, mageConn, mageApi)
        self._configProductAttributesMapping = {'action': 'action', 
           'parent_sku': 'Configurable', 
           'child_sku': 'Simple', 
           'configurable_attributes': 'Attributes', 
           'configurable_attributes_delimiter': ',', 
           'attribute_set_name': 'Attr_Set', 
           'attribute_sets': {'Paper': {'Pack_Size': 'paper_sheet_per_box', 
                                        'Color': 'specific_color', 
                                        'Size': 'paper_size'}, 
                              'Envelope': {'Envelope_Format': 'envelop_format', 
                                           'Pack_Size': 'paper_sheet_per_box', 
                                           'Color': 'specific_color', 
                                           'Env_Type': 'envelop_type'}}}
# okay decompiling MagentoConfigProductAgent.pyc
