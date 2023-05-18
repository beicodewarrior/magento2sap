# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/MagentoProductImageAgent.py
# Compiled at: 2021-03-22 14:02:59
import sys
sys.path.insert(0, '..')
from MAGE2.MagentoProductImage import MagentoProductImage
import json

class MagentoProductImageAstro(MagentoProductImage):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoProductImage.__init__(self, mageConf, mageConn, mageApi, dstCursor)
        self.imageDownloadFolder = '/opt/magedst/astro/image_cache'
        self._mediaFileFolder = '/var/www/astropaper/www/pub/media/catalog/product/'
        self._needDownload = True