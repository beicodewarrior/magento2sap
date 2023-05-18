#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'sandy.tu'
import os
logPath = os.path.abspath(os.path.join(os.path.dirname(__file__),"log/"))

mage_conf = {
    'host':'52.35.22.108',
    'user': 'astrodst',
    'password':'yBuWsClD',
    'db': 'astropaper0511',
    'mage_wsdl':'http://astropaper.silksoftware.net/index.php/api/v2_soap/?wsdl',
    'apiuser':'sapb1_dst',
    'apikey':'dev4silk',
    'logPath' : logPath + "/",
    'logFileName' : 'dev_mage_dst.log',
    'projectName' : 'Astro',
    'storeCode' : 'default',
    'edition' : 'community',
    'restApiAccessToken' : 'tsv9imhg4iuhwhlx2a1bg29c0o0h71mv',
    'restApiEndpoint' : 'http://astropaper.silksoftware.net/rest',
    #'apiHttpUsername' : 'silkdev',
    #'apiHttpPassword' : 'devsitego'
}

dst_conf = {
    'host':'52.35.22.108',
    'user': 'astrodst',
    'password':'yBuWsClD',
    'db':'astropaper_dst',
    'sapb1_card_code':'C20000',
    'dbEngine' : 'mysql'
}

mail_conf = {
    'host' : 'smtp.silksoftware.com',
    'mail_from' : 'DST Notify<opteam@silksoftware.com>',
    'mail_to' : ['sandy.tu@silksoftware.com','bibo.wangxxxx@silksoftware.com'],
    'user' : 'opteam@silksoftware.com',
    'password' : 'silk4dev',
    'processDuration' : {
        'Order Sync' : 5,
        'Shipment Sync' : 5,
        'Invoice Sync' : 5,
        'Product Master Sync' : 5,
        'Product Stock Sync' : 5,
        'Product Price Sync' : 5,
        'Config Product Sync' : 5,
    }
}

sapb1di_conf = {
    "server":"ACI-SAP",
    "language":"ln_English",
    "dbservertype":"dst_MSSQL2012",
    "dbusername":"sa",
    "dbpassword":"acSAPvision33",
    "companydb":"Astro_zUAT",
    "username":"manager",
    "password":"testing",
    "diapi":"SAPB1.SAPbobsCOM90",
    "logfilename":"log/dev_sapb1sync.log",
    'export_price_list':'Astro Price',
    'new_customer_price_list': 'Retail Price'
}

tax_metrics = {
    'Exempt': 'EX',
    'code_rate': {
        'SM-CA': {
            'rate': 8.00,
            'postcode': ['00000','99999'],
            'country': 'US'
        }
    }
}

shipment_methods = {
    'freeshipping_freeshipping': 'WILL CALL',
    'flatrate_flatrate': 'BEST WAY',
    'ups_GND': 'UPS GROUND',
    'ups_3DS': 'UPS 3 DAY SELECT',
    'ups_2DA' : "UPS 2ND DAY AIR",
    'ups_1DA' : "UPS NEXT DAY AIR"
}

payment_methods = {
    'cashondelivery' : 'Incoming Pmnt'
}

HOST = mage_conf['host']
USER = mage_conf["user"]
PWD = mage_conf["password"]
DB = mage_conf["db"]
