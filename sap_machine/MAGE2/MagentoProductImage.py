# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\MAGE2\MagentoProductImage.py
# Compiled at: 2016-06-18 20:45:10
__author__ = 'sandy.tu'
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
import traceback
from datetime import datetime, timedelta
import json, requests, base64, os, shutil
from MagentoProduct import MagentoProduct

class MagentoProductImage(MagentoProduct):

    def __init__(self, mageConf, mageConn=None, mageApi=None, dstCursor=None):
        MagentoProduct.__init__(self, mageConf, mageConn, mageApi, dstCursor)
        self.imageDownloadFolder = 'product_images'
        self.queries['getProductImageGallerySQL'] = "\n            SELECT mg.value\n            FROM catalog_product_entity AS ce\n            INNER JOIN catalog_product_entity_media_gallery_value AS mgv ON ce.entity_id = mgv.entity_id\n            INNER JOIN catalog_product_entity_media_gallery AS mg ON mg.value_id = mgv.value_id\n            INNER JOIN eav_attribute as ea ON mg.attribute_id = ea.attribute_id\n            WHERE ce.sku = %s AND\n            ea.attribute_code = %s AND\n            mg.media_type = 'image' AND\n            mgv.store_id = %s\n        "
        self.queries['getProductImageByTypeSQL'] = '\n            SELECT ce_varchar.value\n            FROM catalog_product_entity AS ce\n            INNER JOIN catalog_product_entity_varchar AS ce_varchar ON ce.entity_id = ce_varchar.entity_id\n            INNER JOIN eav_attribute AS ea ON ce_varchar.attribute_id = ea.attribute_id\n            WHERE ce.sku = %s and attribute_code = %s and ce_varchar.store_id = %s\n        '
        self.queries['insertProductImageSQL'] = '\n            INSERT INTO catalog_product_entity_varchar\n            (attribute_id,store_id,entity_id,value)\n            VALUES (%s,%s,%s,%s)\n            ON DUPLICATE KEY UPDATE\n            value = %s\n        '
        self.queries['insertProductImageGallerySQL'] = '\n            INSERT INTO catalog_product_entity_media_gallery\n            (attribute_id,value,media_type)\n            VALUES (%s,%s,%s)\n        '
        self.queries['insertProductImageGalleryValueSQL'] = '\n            INSERT INTO catalog_product_entity_media_gallery_value\n            (value_id,store_id,entity_id,label,position)\n            VALUES (%s,%s,%s,%s,%s)\n        '
        self.queries['insertMediaValueToEntitySQL'] = '\n            INSERT IGNORE INTO catalog_product_entity_media_gallery_value_to_entity\n            (value_id,entity_id)\n            VALUES (%s,%s)\n        '
        self.imageDownloadFolder = 'image_import/'
        self._mediaFileFolder = '/var/www/'
        self._needAssignPosition = False
        self._needAssignLabel = False
        self._singleImageTypes = ['image', 'small_image', 'thumbnail', 'swatch_image']
        self._webuserUID = 48
        self._webuserGID = 48
        self._needDownload = True

    def downloadImage(self, imageUrl, forceDownload=False):
        downloadResult = {'image_url': imageUrl, 
           'http_response_code': None, 
           'file_name': None, 
           'success': False, 
           'log': ''}
        try:
            filename = self.getFilenameFromURL(imageUrl)
            if self.isFileExist(self.imageDownloadFolder + filename) and forceDownload == False:
                downloadResult['file_name'] = filename
                downloadResult['success'] = True
                downloadResult['http_response_code'] = 200
                downloadResult['log'] = ('File {0} exists in {1}').format(filename, self.imageDownloadFolder)
                self.logger.info(downloadResult['log'])
                return downloadResult
            if self._needDownload == False:
                downloadResult['log'] = ('File {0} not exists in {1} but config not to download').format(filename, self.imageDownloadFolder)
                self.logger.info(downloadResult['log'])
                return downloadResult
            request = requests.get(imageUrl)
            rawData = request.content
            httpResponseCode = request.status_code
            request.close()
            downloadResult['http_response_code'] = httpResponseCode
            if httpResponseCode == 200:
                fullpath = self.imageDownloadFolder + '/' + filename
                file = open(fullpath, 'wb')
                file.write(rawData)
                file.close()
                log = ('Successfully download image {0} to {1}').format(imageUrl, fullpath)
                downloadResult['file_name'] = filename
                downloadResult['success'] = True
            else:
                log = ('Error while download image {0} with http response status {1}').format(imageUrl, httpResponseCode)
            downloadResult['log'] = log
            return downloadResult
        except Exception as e:
            log = ('Error while download image {0} with error {1}').format(imageUrl, traceback.format_exc())
            self.logger.exception(log)
            downloadResult['log'] = log
            return downloadResult

        return

    def base64EncodeImage(self, filename):
        with open(filename, 'rb') as (imageFile):
            encodedString = base64.b64encode(imageFile.read())
            return encodedString

    def createProductImageThroughAPI(self, eProductImage):
        sku = eProductImage['sku']
        syncResult = {'sku': sku, 
           'http_response_code': None, 
           'media_url': None, 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            imageUrl = eProductImage['image_url']
            downloadResult = self.downloadImage(imageUrl)
            syncResult['http_response_code'] = downloadResult['http_response_code']
            if downloadResult['success']:
                filename = self.imageDownloadFolder + '/' + downloadResult['file_name']
                imageData = self.base64EncodeImage(filename)
                imageFileEntity = {'content': imageData, 
                   'mime': 'image/jpeg'}
                productImageEntity = {'file': imageFileEntity, 
                   'label': eProductImage['image_label'], 
                   'position': eProductImage['position'], 
                   'types': eProductImage['image_type'].split(','), 
                   'exclude': 0, 
                   'remove': 0}
                mediaUrl = self.mageApi.catalogProductAttributeMediaCreate(sku, productImageEntity)
                if mediaUrl is not None:
                    syncResult['sync_status'] = 'O'
                    syncResult['media_url'] = mediaUrl
                    log = ('id/sku/image_type/media_url : {0}/{1}/{2}/{3}').format(eProductImage['id'], sku, eProductImage['image_type'], mediaUrl)
                else:
                    log = ('Failed id/sku/image_type : {0}/{1}/{2}').format(eProductImage['id'], sku, eProductImage['image_type'])
                syncResult['sync_notes'] = log
            else:
                syncResult['sync_notes'] = downloadResult['log']
            return syncResult
        except Exception as e:
            log = traceback.format_exc()
            syncResult['sync_notes'] = log
            return syncResult

        return

    def isFileExist(self, filename):
        return os.path.isfile(filename)

    def getFilenameFromURL(self, url):
        filename = os.path.basename(url)
        filename = filename.replace('%20', '_20')
        filename = filename.replace(' ', '_')
        filename, fileExtension = os.path.splitext(filename)
        if fileExtension == '':
            fileExtension = '.jpg'
        filename = filename + fileExtension
        return filename

    def importImage(self, eProductImage):
        sku = eProductImage['sku']
        syncResult = {'sku': sku, 
           'http_response_code': None, 
           'media_url': None, 
           'sync_status': 'F', 
           'sync_notes': ''}
        try:
            imageUrl = eProductImage['image_url']
            downloadResult = self.downloadImage(imageUrl)
            syncResult['http_response_code'] = downloadResult['http_response_code']
            if downloadResult['success']:
                syncResult['sync_notes'] = downloadResult['log']
                i = 0
                for imageType in eProductImage['image_type'].split(','):
                    imageType = imageType.strip()
                    if i > 0:
                        duplicateImage = True
                    else:
                        duplicateImage = False
                    assignResult = self.assignImageToProduct(eProductImage, downloadResult['file_name'], imageType, duplicateImage)
                    syncResult['sync_notes'] = syncResult['sync_notes'] + '\n' + assignResult['sync_notes']
                    i = i + 1

                syncResult['media_url'] = assignResult['media_url']
                syncResult['sync_status'] = assignResult['sync_status']
            else:
                syncResult['sync_notes'] = downloadResult['log']
            return syncResult
        except Exception as e:
            log = traceback.format_exc()
            syncResult['sync_notes'] = log
            return syncResult

        return

    def getDispretionPath(self, filename):
        dispretionPath = ''
        l = len(filename)
        if l >= 2:
            s = filename[0:2].replace('.', '_')
            dispretionPath = '/' + s[0] + '/' + s[1]
        elif l == 1:
            dispretionPath = '/_/' + filename
        return dispretionPath

    def productHasImageLike(self, sku, filename, imageType):
        predictKey = self.getDispretionPath(filename) + '/' + filename
        basename = os.path.splitext(os.path.basename(filename))[0]
        ext = os.path.splitext(predictKey)[(-1)]
        dirname = os.path.dirname(predictKey)
        cont = True
        index = 1
        if imageType == 'media_gallery':
            productImageSQL = self.queries['getProductImageGallerySQL']
        else:
            productImageSQL = self.queries['getProductImageByTypeSQL']
        self.mageCursor.execute(productImageSQL, [sku, imageType, 0])
        res = self.mageCursor.fetchall()
        productImages = []
        if res is not None and len(res) > 0:
            for r in res:
                productImages.append(r[0])

        if basename and ext:
            while cont:
                fullpath = self._mediaFileFolder + predictKey
                if os.path.isfile(fullpath):
                    if predictKey in productImages:
                        return predictKey
                    basename += '_' + str(index)
                    predictKey = dirname + '/' + basename + ext
                    index += 1
                else:
                    cont = False

        return False

    def moveFile(self, filename, force=0):
        srcFile = self.imageDownloadFolder + '/' + filename
        dispretionPath = self.getDispretionPath(filename)
        fullDispretionPath = self._mediaFileFolder + dispretionPath
        fullPath = fullDispretionPath + '/' + filename
        if not os.path.isfile(fullPath) or force > 0:
            if os.path.isfile(fullPath) and force > 0:
                os.remove(fullPath)
            if not os.path.isdir(fullDispretionPath):
                os.makedirs(fullDispretionPath)
            shutil.copy2(srcFile, fullDispretionPath)
            try:
                shutil.copy2(srcFile, fullDispretionPath)
                try:
                    os.chown(fullDispretionPath, self._webuserUID, self._webuserGID)
                    os.chmod(fullDispretionPath, '0755')
                except:
                    self.logger.warning(('Failed to change ownership and permission for {0} with error {1}').format(fullDispretionPath, traceback.format_exc()))

            except:
                return False

        return dispretionPath + '/' + filename

    def assignImageToProduct(self, eProductImage, filename, imageType, duplicateImage=False):
        syncResult = {'sku': eProductImage['sku'], 
           'media_url': None, 
           'sync_status': 'F', 
           'sync_notes': ''}
        productId = self.getProductIdBySku(eProductImage['sku'])
        if productId == 0:
            syncResult['sync_status'] = 'I'
            syncResult['sync_notes'] = ('Product {0} does not exist.').format(eProductImage['sku'])
            return syncResult
        else:
            attributeMetadata = self.getAttributeMetadata(imageType)
            mediaGalleryAttributeMetadata = self.getAttributeMetadata('media_gallery')
            if attributeMetadata is None:
                syncResult['sync_notes'] = ('Attribute {0} does not exist.').format(imageType)
                return syncResult
            addedFilename = self.productHasImageLike(eProductImage['sku'], filename, imageType)
            if not addedFilename:
                addedFilename = self.moveFile(filename)
            else:
                syncResult['media_url'] = addedFilename
                syncResult['sync_status'] = 'O'
                syncResult['sync_notes'] = ('Product has image like: sku/image_type/media_url: {0}/{1}/{2}').format(eProductImage['sku'], imageType, addedFilename)
                return syncResult
            if not addedFilename:
                syncResult['sync_notes'] = ('Failed to move file {0}.').format(filename)
                return syncResult
            insParam = None
            if imageType in self._singleImageTypes:
                insParam = [
                 attributeMetadata['attribute_id'], 0, productId, addedFilename, addedFilename]
                self.mageCursor.execute(self.queries['insertProductImageSQL'], insParam)
            if duplicateImage == False:
                mediaGalleryParam = [
                 mediaGalleryAttributeMetadata['attribute_id'], addedFilename, 'image']
                self.mageCursor.execute(self.queries['insertProductImageGallerySQL'], mediaGalleryParam)
                valueId = self.mageCursor.lastrowid
                if self._needAssignPosition == True:
                    position = eProductImage['position']
                else:
                    position = 0
                if self._needAssignLabel == True:
                    label = eProductImage['label']
                else:
                    label = None
                mediaGalleryValueParam = [
                 valueId, 0, productId, label, position]
                self.mageCursor.execute(self.queries['insertProductImageGalleryValueSQL'], mediaGalleryValueParam)
                self.mageCursor.execute(self.queries['insertMediaValueToEntitySQL'], [valueId, productId])
            syncResult['media_url'] = addedFilename
            syncResult['sync_status'] = 'O'
            syncResult['sync_notes'] = ('Success: sku/image_type/media_url: {0}/{1}/{2}').format(eProductImage['sku'], imageType, addedFilename)
            return syncResult
            return
# okay decompiling MagentoProductImage.pyc
