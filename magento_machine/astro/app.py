#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'sandy.tu'
import MySQLdb
import logging
import sys
import os
sys.path.insert(0, '..')
path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0,path)
import os
import json
import getopt
from datetime import datetime
from MageDstSyncAgent import MageDSTSyncAstro
from utility.utility import DSTMailer


from config import *

def sendErrorLogMail(processName,dstTableName):
    print "==========Start Sending Mail Process==============="
    dstMailer = DSTMailer(mage_conf,dst_conf,mail_conf)
    dstMailer.sendErrorLogMail(processName,dstTableName)
    del dstMailer
    print "===========End Send Mail Process===================="

argv = sys.argv[1:]
if len(argv) ==0:
    print "Not enough parameters. Please specify the attribute_set_name and file name."
    print "-t: attribute_set_name"
    print "-f: force the action"
    print "-a: action"
    print "Example Usage:"
    print 'python application.py -a "import_product" -t "Default" -f 1'
    sys.exit(2)
else :
    try:
        opts, args = getopt.getopt(argv,"t:f:a:")
    except getopt.GetoptError:
        print "Error while parsing the input."
        print "Example Usage:"
        print 'python application.py -a import_product -t "Default" -f 1'
        sys.exit(2)

    attribute_set_name = ''
    force = 0
    action = ''
    for opt, arg in opts:
        if opt == '-a':
            action = arg.strip()
        if opt == '-t':
            attribute_set_name = arg.strip()
        if opt == '-f':
            force = arg
    if action == '':
        print "action needs to be specified"
        sys.exit(2)

    elif action == 'order2dst':
        print "==============Start MAGENTO ORDER TO DST================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncMagentoOrderToDst()
        del sync_tool
        print "===============End MAGENTO ORDER TO DST==============="

    elif action == 'ship2mage':
        print "==============Start SHIPMENT TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncShipmentToMagento('N')
        del sync_tool
        print "===============End SHIPMENT TO MAGENTO==============="

    elif action == 'productm2mage':
        print "==============Start PRODUCT MASTER TO Magento================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductMaster(productAttributesMap={},syncCategoryThroughAPI=False)
        del sync_tool
        sendErrorLogMail('Product Master Sync','e_product_master')
        print "==============End PRODUCT MASTER TO Magento================"

    elif action == 'image2mage':
        print "==============Start PRODUCT IMAGE TO Magento================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductImage(syncThroughAPI=False)
        del sync_tool
        print "==============End PRODUCT IMAGE TO Magento================"

    elif action == 'stock2mage':
        print "==============Start PRODUCT INVENTORY TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductInventory('N')
        del sync_tool
        sendErrorLogMail('Product Stock Sync','e_product_inventory')
        print "==============End PRODUCT INVENTORY TO MAGENTO================"

    elif action == 'custmage2dst':
        print "==============Start SYNC CUSTOMER FROM MAGENTO TO DST================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncMagentoCustomersToDst(limits=100)
        del sync_tool
        print "==============END SYNC CUSTOMER FROM MAGENTO TO DST================"

    elif action == 'price2mage':
        print "==============Start PRODUCT Price TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductPrice()
        del sync_tool
        print "==============End PRODUCT Price TO MAGENTO================"

    elif action == 'configproduct2mage':
        print "==============Start Config PRODUCT TO Magento================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncConfigProduct('N')
        del sync_tool
        sendErrorLogMail('Config Product Sync','e_config_product')
        print "==============End Config PRODUCT TO Magento================"

    elif action == 'productcategory2mage':
        print "==============Start Product Category DST TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductCategory(througApi=False)
        del sync_tool
        print "==============End Product Category DST TO MAGENTO================"

    elif action == 'tierprice2mage':
        print "==============Start PRODUCT Tier Price TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductGroupTierPrice()
        del sync_tool
        print "==============End PRODUCT Tier Price TO MAGENTO================"

    elif action == 'custdst2mage':
        print "==============Start Customer DST TO MAGENTO================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncCustomerToMage()
        del sync_tool
        print "==============End Customer DST TO MAGENTO================"

    elif action == 'custgroup2mage':
        print "============ Start Customer Group DST TO MAGENTO ============"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncCustomerGroupToMage()
        del sync_tool
        print "============  End  Customer Group DST TO MAGENTO ============"

    elif action == 'updatePrintApplication':
        print "============ START Update Print Application ============"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.updatePrintApplication()
        del sync_tool
        print "============  END  Update Print Application ============"

    elif action == 'image2mage':
        print "============== Start Image From DST to Magento ================"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.syncProductImage()
        del sync_tool
        print "==============  End  Image From DST to Magento ================"

    elif action == 'updateUrlKey':
        print "============ START Update URL Key and URL Rewrite ============"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.updateUrlKey()
        del sync_tool
        print "============  END  Update URL Key and URL Rewrite ============"

    elif action == 'updateTierPriceLevel':
        print "============ START Update Customer Tier Price Level ============"
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.updateTierPriceLevel()
        del sync_tool
        print "============  END  Update Customer Tier Price Level ============"

    elif action == 'totalsheets':
        print "========== START Set Up Total Sheets =========="
        sync_tool = MageDSTSyncAstro(mage_conf, dst_conf)
        sync_tool.setTotalSheets()
        del sync_tool
        print "==========  END  Set Up Total Sheets =========="

    else :
        print "Action: {0} is not recognized".format(action)

