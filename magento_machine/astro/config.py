# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/astro/config.py
# Compiled at: 2019-10-24 19:57:48
__author__ = 'sandy.tu'
import os
logPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'log/'))
mage_conf = {'host': '127.0.0.1', 
   'user': 'silkdba', 
   'password': 'fj8Tu6Nh5M', 
   'db': 'astropaper_prod', 
   'mage_wsdl': 'http://beta.astropaper.com/index.php/api/v2_soap/?wsdl', 
   'apiuser': 'sapb1_dst', 
   'apikey': 'dev4silk', 
   'logPath': logPath + '/', 
   'logFileName': 'mage_dst.log', 
   'projectName': 'Astro', 
   'storeCode': 'default', 
   'edition': 'community', 
   'restApiAccessToken': 't7vi7dly62eqblhymhhl3m6dce7haulf', 
   'restApiEndpoint': 'http://beta.astropaper.com/rest'}
dst_conf = {'host': '127.0.0.1', 
   'user': 'silkdba', 
   'password': 'fj8Tu6Nh5M', 
   'db': 'astropaper_dst_new', 
   'sapb1_card_code': 'C20000', 
   'dbEngine': 'mysql'}
mail_conf = {'host': 'smtp.silksoftware.com', 
   'mail_from': 'DST Notify<opteam@silksoftware.com>', 
   'mail_to': [
             'ken@newbirddesign.com'], 
   'user': 'opteam@silksoftware.com', 
   'password': 'silk4dev', 
   'processDuration': {'Order Sync': 5, 
                       'Shipment Sync': 5, 
                       'Invoice Sync': 5, 
                       'Product Master Sync': 5, 
                       'Product Stock Sync': 5, 
                       'Product Price Sync': 5, 
                       'Config Product Sync': 5}}
sapb1di_conf = {'server': 'ACI-SAP', 
   'language': 'ln_English', 
   'dbservertype': 'dst_MSSQL2012', 
   'dbusername': 'sa', 
   'dbpassword': 'acSAPvision33', 
   'companydb': 'Astro', 
   'username': 'manager', 
   'password': 'golive', 
   'diapi': 'SAPB1.SAPbobsCOM90', 
   'logfilename': 'log/sapb1sync.log', 
   'export_price_list': 'Astro Price', 
   'new_customer_price_list': 'Retail Price'}
tax_metrics = {'Exempt': 'EX', 
   'code_rate': {'SM-CA': {'rate': 8.0, 
                           'postcode': [
                                      '00000', '99999'], 
                           'country': 'US'}}}
shipment_methods = {'freeshipping_freeshipping': 'WILL CALL', 
   'flatrate_flatrate': 'BEST WAY', 
   'ups_GND': 'UPS GROUND', 
   'ups_3DS': 'UPS 3 DAY SELECT', 
   'ups_2DA': 'UPS 2ND DAY AIR', 
   'ups_1DA': 'UPS NEXT DAY AIR'}
payment_methods = {'cashondelivery': 'Incoming Pmnt'}
HOST = mage_conf['host']
USER = mage_conf['user']
PWD = mage_conf['password']
DB = mage_conf['db']
