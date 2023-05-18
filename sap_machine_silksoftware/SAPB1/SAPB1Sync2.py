# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\SAPB1\SAPB1Sync2.py
# Compiled at: 2016-07-26 10:05:20
import sys
sys.path.insert(0, '..')
from utility.utility import Logger
from ERPAbstract.ERPSyncAbstract import ERPSyncAbstract
from datetime import datetime, timedelta
from time import time
import traceback, MySQLdb, decimal, pymssql, json
from utility.utility import DecimalEncoder
from utility.DSTControl import DSTControl

class SAPB1Sync2(ERPSyncAbstract):

    def __init__(self, sapb1di_conf, dst_conf, connect_di=True):
        appName = 'SAPB1'
        logFileName = sapb1di_conf['logfilename']
        functs = {'eOrderFunct': {'parent': 'self', 
                           'name': 'b1eOrderFunct', 
                           'vars': [
                                  'mOrder'], 
                           'return': [
                                    'order']}, 
           'eOrderExtFunct': {'parent': 'self', 
                              'name': 'b1eOrderExtFunct', 
                              'vars': [
                                     'order', 'mOrder'], 
                              'return': []}, 
           'eOrderLineFunct': {'parent': 'self', 
                               'name': 'b1eOrderLineFunct', 
                               'vars': [
                                      'i', 'order', 'item', 'mOrder'], 
                               'return': []}, 
           'eOrderLineExtFunct': {'parent': 'self', 
                                  'name': 'b1eOrderLineExtFunct', 
                                  'vars': [
                                         'i', 'order', 'item', 'mOrder'], 
                                  'return': []}, 
           'addEOrderFunct': {'parent': 'self', 
                              'name': 'addB1EOrderFunct', 
                              'vars': [
                                     'order'], 
                              'return': [
                                       'eOrderIncId']}, 
           'cancelEOrderFunct': {'parent': 'self', 
                                 'name': 'cancelB1EOrderFunct', 
                                 'vars': [
                                        'mOrder'], 
                                 'return': []}, 
           'eOrderRFunct': {'parent': 'self', 
                            'name': 'b1eOrderRFunct', 
                            'vars': [
                                   'mDownPayment'], 
                            'return': [
                                     'order', 'orderItemCount']}, 
           'eDownPaymentFunct': {'parent': 'self', 
                                 'name': 'b1eDownPaymentFunct', 
                                 'vars': [
                                        'order', 'mDownPayment'], 
                                 'return': [
                                          'downPayment']}, 
           'eDownPaymentExtFunct': {'parent': 'self', 
                                    'name': 'b1eDownPaymentExtFunct', 
                                    'vars': [
                                           'downPayment', 'order'], 
                                    'return': []}, 
           'eDownPaymentLineFunct': {'parent': 'self', 
                                     'name': 'b1eDownPaymentLineFunct', 
                                     'vars': [
                                            'i', 'downPayment', 'order'], 
                                     'return': []}, 
           'eDownPaymentLineExtFunct': {'parent': 'self', 
                                        'name': 'b1eDownPaymentLineExtFunct', 
                                        'vars': [
                                               'i', 'downPayment', 'order'], 
                                        'return': []}, 
           'eDownPaymentIncIdFunct': {'parent': 'self', 
                                      'name': 'b1eDownPaymentIncIdFunct', 
                                      'vars': [
                                             'mDownPayment'], 
                                      'return': [
                                               'eDownPaymentIncId']}, 
           'addEDownPaymentFunct': {'parent': 'self', 
                                    'name': 'addB1EDownPaymentFunct', 
                                    'vars': [
                                           'downPayment', 'order'], 
                                    'return': [
                                             'eDownPaymentIncId']}, 
           'eCustFunct': {'parent': 'self', 
                          'name': 'b1eCustFunct', 
                          'vars': [
                                 'mCustomer'], 
                          'return': [
                                   'customer', 'exist']}, 
           'eCustExtFunct': {'parent': 'self', 
                             'name': 'b1eCustExtFunct', 
                             'vars': [
                                    'customer', 'mCustomer'], 
                             'return': []}, 
           'eCustAddrFunct': {'parent': 'self', 
                              'name': 'b1eCustAddrFunct', 
                              'vars': [
                                     'i', 'customer', 'address', 'mCustomer'], 
                              'return': []}, 
           'eCustAddrExtFunct': {'parent': 'self', 
                                 'name': 'b1eCustAddrExtFunct', 
                                 'vars': [
                                        'i', 'customer', 'address', 'mCustomer'], 
                                 'return': []}, 
           'eCustContFunct': {'parent': 'self', 
                              'name': 'b1eCustContFunct', 
                              'vars': [
                                     'i', 'customer', 'contact', 'mCustomer'], 
                              'return': []}, 
           'eCustContExtFunct': {'parent': 'self', 
                                 'name': 'b1eCustContExtFunct', 
                                 'vars': [
                                        'i', 'customer', 'contact', 'mCustomer'], 
                                 'return': []}, 
           'addUpdateECustFunct': {'parent': 'self', 
                                   'name': 'addUpdateB1ECustFunct', 
                                   'vars': [
                                          'customer', 'exist'], 
                                   'return': [
                                            'eCustIncId']}, 
           'eShipRFunct': {'parent': 'self', 
                           'name': 'b1eShipRFunct', 
                           'vars': [
                                  'mInvoice'], 
                           'return': [
                                    'shipment', 'shipItemCount']}, 
           'eInvoiceFunct': {'parent': 'self', 
                             'name': 'b1eInvoiceFunct', 
                             'vars': [
                                    'shipment', 'mInvoice'], 
                             'return': [
                                      'invoice']}, 
           'eInvoiceExtFunct': {'parent': 'self', 
                                'name': 'b1eInvoiceExtFunct', 
                                'vars': [
                                       'invoice', 'shipment'], 
                                'return': []}, 
           'eInvoiceLineFunct': {'parent': 'self', 
                                 'name': 'b1eInvoiceLineFunct', 
                                 'vars': [
                                        'i', 'invoice', 'shipment'], 
                                 'return': []}, 
           'eInvoiceLineExtFunct': {'parent': 'self', 
                                    'name': 'b1eInvoiceLineExtFunct', 
                                    'vars': [
                                           'i', 'invoice', 'shipment'], 
                                    'return': []}, 
           'eInvoiceIncIdFunct': {'parent': 'self', 
                                  'name': 'b1eInvoiceIncIdFunct', 
                                  'vars': [
                                         'mInvoice'], 
                                  'return': [
                                           'eInvoiceIncId']}, 
           'addEInvoiceFunct': {'parent': 'self', 
                                'name': 'addB1EInvoiceFunct', 
                                'vars': [
                                       'invoice', 'shipment'], 
                                'return': [
                                         'eInvoiceIncId']}, 
           'eShipsFunct': {'parent': 'self', 
                           'name': 'b1eShipsFunct', 
                           'vars': [], 'return': [
                                    'eShips']}, 
           'mShipFunct': {'parent': 'self', 
                          'name': 'b1mShipFunct', 
                          'vars': [
                                 'eShip'], 
                          'return': [
                                   'shipment', 'shipItemCount']}, 
           'mShipExtFunct': {'parent': 'self', 
                             'name': 'b1mShipExtFunct', 
                             'vars': [
                                    'shipment', 'eShip'], 
                             'return': []}, 
           'mShipItemFunct': {'parent': 'self', 
                              'name': 'b1mShipItemFunct', 
                              'vars': [
                                     'i', 'shipment', 'eShip'], 
                              'return': []}, 
           'mShipItemExtFunct': {'parent': 'self', 
                                 'name': 'b1mShipItemExtFunct', 
                                 'vars': [
                                        'i', 'shipment', 'eShip'], 
                                 'return': []}, 
           'eProductsFunct': {'parent': 'self', 
                              'name': 'b1eProductsFunct', 
                              'vars': [
                                     'task'], 
                              'return': [
                                       'eProducts']}, 
           'mProductFunct': {'parent': 'self', 
                             'name': 'b1mProductFunct', 
                             'vars': [
                                    'eProduct'], 
                             'return': [
                                      'product']}, 
           'mProductExtFunct': {'parent': 'self', 
                                'name': 'b1mProductExtFunct', 
                                'vars': [
                                       'product', 'eProduct'], 
                                'return': []}, 
           'addUpdateMProductFunct': {'parent': 'self', 
                                      'name': 'addUpdateB1MProductFunct', 
                                      'vars': [
                                             'product'], 
                                      'return': [
                                               'mProductId']}, 
           'eOrderIncIdFunct': {'parent': 'self', 
                                'name': 'b1eOrderIncIdFunct', 
                                'vars': [
                                       'mOrder'], 
                                'return': [
                                         'eOrderIncId']}, 
           'eProductsInventoryFunct': {'parent': 'self', 
                                       'name': 'b1eProductsInventoryFunct', 
                                       'vars': [
                                              'task'], 
                                       'return': [
                                                'eProductsInventory']}, 
           'mProductInventoryFunct': {'parent': 'self', 
                                      'name': 'b1mProductInventoryFunct', 
                                      'vars': [
                                             'eProductInventory'], 
                                      'return': [
                                               'productInventory']}, 
           'mProductInventoryExtFunct': {'parent': 'self', 
                                         'name': 'b1mProductInventoryExtFunct', 
                                         'vars': [
                                                'productInventory', 'eProductInventory'], 
                                         'return': []}, 
           'addUpdateMProductInventoryFunct': {'parent': 'self', 
                                               'name': 'addUpdateB1MProductInventoryFunct', 
                                               'vars': [
                                                      'productInventory'], 
                                               'return': [
                                                        'mProductInventoryId']}, 
           'eProductsPriceFunct': {'parent': 'self', 
                                   'name': 'b1eProductsPriceFunct', 
                                   'vars': [
                                          'task'], 
                                   'return': [
                                            'eProductsPrice']}, 
           'mProductPriceFunct': {'parent': 'self', 
                                  'name': 'b1mProductPriceFunct', 
                                  'vars': [
                                         'eProductPrice'], 
                                  'return': [
                                           'productPrice']}, 
           'mProductPriceExtFunct': {'parent': 'self', 
                                     'name': 'b1mProductPriceExtFunct', 
                                     'vars': [
                                            'productPrice', 'eProductPrice'], 
                                     'return': []}, 
           'addUpdateMProductPriceFunct': {'parent': 'self', 
                                           'name': 'addUpdateB1MProductPriceFunct', 
                                           'vars': [
                                                  'productPrice'], 
                                           'return': [
                                                    'mProductPriceId']}, 
           'eProductsTierPriceFunct': {'parent': 'self', 
                                       'name': 'b1eProductsTierPriceFunct', 
                                       'vars': [
                                              'task'], 
                                       'return': [
                                                'eProductsTierPrice']}, 
           'mProductTierPriceFunct': {'parent': 'self', 
                                      'name': 'b1mProductTierPriceFunct', 
                                      'vars': [
                                             'eProductTierPrice'], 
                                      'return': [
                                               'productTierPrice']}, 
           'mProductTierPriceExtFunct': {'parent': 'self', 
                                         'name': 'b1mProductTierPriceExtFunct', 
                                         'vars': [
                                                'productTierPrice', 'eProductTierPrice'], 
                                         'return': []}, 
           'addUpdateMProductTierPriceFunct': {'parent': 'self', 
                                               'name': 'addUpdateB1MProductTierPriceFunct', 
                                               'vars': [
                                                      'productTierPrice'], 
                                               'return': [
                                                        'mProductTierPriceId']}, 
           'eProductsGroupPriceFunct': {'parent': 'self', 
                                        'name': 'b1eProductsGroupPriceFunct', 
                                        'vars': [
                                               'task'], 
                                        'return': [
                                                 'eProductsGroupPrice']}, 
           'mProductGroupPriceFunct': {'parent': 'self', 
                                       'name': 'b1mProductGroupPriceFunct', 
                                       'vars': [
                                              'eProductGroupPrice'], 
                                       'return': [
                                                'productGroupPrice']}, 
           'mProductGroupPriceExtFunct': {'parent': 'self', 
                                          'name': 'b1mProductGroupPriceExtFunct', 
                                          'vars': [
                                                 'productGroupPrice', 'eProductGroupPrice'], 
                                          'return': []}, 
           'addUpdateMProductGroupPriceFunct': {'parent': 'self', 
                                                'name': 'addUpdateB1MProductGroupPriceFunct', 
                                                'vars': [
                                                       'productGroupPrice'], 
                                                'return': [
                                                         'mProductGroupPriceId']}, 
           'eCustomersFunct': {'parent': 'self', 
                               'name': 'b1eCustomersFunct', 
                               'vars': [
                                      'task'], 
                               'return': [
                                        'eCustomers']}, 
           'mCustomerFunct': {'parent': 'self', 
                              'name': 'b1mCustomerFunct', 
                              'vars': [
                                     'eCustomer'], 
                              'return': [
                                       'customer', 'customerAddressCount']}, 
           'mCustomerExtFunct': {'parent': 'self', 
                                 'name': 'b1mCustomerExtFunct', 
                                 'vars': [
                                        'customer', 'eCustomer'], 
                                 'return': []}, 
           'mCustomerAddressFunct': {'parent': 'self', 
                                     'name': 'b1mCustomerAddressFunct', 
                                     'vars': [
                                            'i', 'customer', 'eCustomer'], 
                                     'return': []}, 
           'mCustomerAddressExtFunct': {'parent': 'self', 
                                        'name': 'b1mCustomerAddressExtFunct', 
                                        'vars': [
                                               'i', 'customer', 'eCustomer'], 
                                        'return': []}, 
           'eConfigProductsFunct': {'parent': 'self', 
                                    'name': 'b1eConfigProductsFunct', 
                                    'vars': [
                                           'task'], 
                                    'return': [
                                             'eConfigProducts']}, 
           'mConfigProductFunct': {'parent': 'self', 
                                   'name': 'b1mConfigProductFunct', 
                                   'vars': [
                                          'eConfigProduct'], 
                                   'return': [
                                            'configProduct']}, 
           'mConfigProductExtFunct': {'parent': 'self', 
                                      'name': 'b1mConfigProductExtFunct', 
                                      'vars': [
                                             'configProduct', 'eConfigProduct'], 
                                      'return': []}, 
           'addUpdateMConfigProductFunct': {'parent': 'self', 
                                            'name': 'addUpdateB1MConfigProductFunct', 
                                            'vars': [
                                                   'configProduct'], 
                                            'return': [
                                                     'mConfigProductId']}, 
           'eProductsCompanyPriceFunct': {'parent': 'self', 
                                          'name': 'b1eProductsCompanyPriceFunct', 
                                          'vars': [
                                                 'task'], 
                                          'return': [
                                                   'eProductsCompanyPrice']}, 
           'mProductCompanyPriceFunct': {'parent': 'self', 
                                         'name': 'b1mProductCompanyPriceFunct', 
                                         'vars': [
                                                'eProductCompanyPrice'], 
                                         'return': [
                                                  'productCompanyPrice']}, 
           'mProductCompanyPriceExtFunct': {'parent': 'self', 
                                            'name': 'b1mProductCompanyPriceExtFunct', 
                                            'vars': [
                                                   'productCompanyPrice', 'eProductCompanyPrice'], 
                                            'return': []}, 
           'addUpdateMProductCompanyPriceFunct': {'parent': 'self', 
                                                  'name': 'addUpdateB1MProductCompanyPriceFunct', 
                                                  'vars': [
                                                         'productCompanyPrice'], 
                                                  'return': [
                                                           'mProductCompanyPriceId']}, 
           'eProductsCategoryFunct': {'parent': 'self', 
                                      'name': 'b1eProductsCategoryFunct', 
                                      'vars': [
                                             'task'], 
                                      'return': [
                                               'eProductsCategory']}, 
           'mProductCategoryFunct': {'parent': 'self', 
                                     'name': 'b1mProductCategoryFunct', 
                                     'vars': [
                                            'eProductCategory'], 
                                     'return': [
                                              'productCategory']}, 
           'mProductCategoryExtFunct': {'parent': 'self', 
                                        'name': 'b1mProductCategoryExtFunct', 
                                        'vars': [
                                               'productCategory', 'eProductCategory'], 
                                        'return': []}, 
           'addUpdateMProductCategoryFunct': {'parent': 'self', 
                                              'name': 'addUpdateB1MProductCategoryFunct', 
                                              'vars': [
                                                     'productCategory'], 
                                              'return': [
                                                       'mProductCategoryId']}, 
           'eCompanysFunct': {'parent': 'self', 
                              'name': 'b1eCompanysFunct', 
                              'vars': [
                                     'task'], 
                              'return': [
                                       'eCompanys']}, 
           'mCompanyFunct': {'parent': 'self', 
                             'name': 'b1mCompanyFunct', 
                             'vars': [
                                    'eCompany'], 
                             'return': [
                                      'company', 'companyAddressCount', 'companyContactCount']}, 
           'mCompanyExtFunct': {'parent': 'self', 
                                'name': 'b1mCompanyExtFunct', 
                                'vars': [
                                       'company', 'eCompany'], 
                                'return': []}, 
           'mCompanyAddressFunct': {'parent': 'self', 
                                    'name': 'b1mCompanyAddressFunct', 
                                    'vars': [
                                           'i', 'company', 'eCompany'], 
                                    'return': []}, 
           'mCompanyAddressExtFunct': {'parent': 'self', 
                                       'name': 'b1mCompanyAddressExtFunct', 
                                       'vars': [
                                              'i', 'company', 'eCompany'], 
                                       'return': []}, 
           'mCompanyContactFunct': {'parent': 'self', 
                                    'name': 'b1mCompanyContactFunct', 
                                    'vars': [
                                           'i', 'company', 'eCompany'], 
                                    'return': []}, 
           'mCompanyContactExtFunct': {'parent': 'self', 
                                       'name': 'b1mCompanyContactExtFunct', 
                                       'vars': [
                                              'i', 'company', 'eCompany'], 
                                       'return': []}}
        queries = {'listMOrdersSQL': "SELECT * FROM m_order WHERE sync_status ='N' and m_order_status in (%s);", 
           'listMOrderItemsSQL': "SELECT sku, qty, price, tax_amt FROM m_order_item WHERE m_order_id = '%s';", 
           'listMCancelOrdersSQL': "SELECT * FROM m_order\n                                        WHERE sync_status ='N'\n                                        and m_order_status = 'canceled';", 
           'listMDownPaymentsSQL': "SELECT e_order_inc_id, grand_total\n                                    FROM m_order\n                                    WHERE sync_status = 'O'\n                                    AND payment_method in ({paymentMethods})\n                                    AND m_order_status in ({mOrderStatus})\n                                    AND e_order_inc_id NOT IN (\n                                        SELECT e_order_inc_id\n                                        FROM e_downpayment\n                                        WHERE sync_status = 'O'\n                                    )\n            ", 
           'listMCustsSQL': "SELECT * FROM m_customer WHERE sync_status in ('N','F');", 
           'listMCustAddrsSQL': "SELECT * FROM m_customer_addr WHERE m_cust_id = '%s';", 
           'listMInvoicesSQL': "SELECT m_order_inc_id, m_invoice_inc_id, e_shipment_inc_id\n                                    FROM e_shipment\n                                    WHERE sync_status = 'O'\n                                    AND e_shipment_inc_id not in (\n                                        SELECT e_shipment_inc_id\n                                        FROM e_invoice\n                                        WHERE sync_status = 'O');", 
           'insertOrUpdateEProductSQL': 'INSERT INTO e_product_master\n                                    (sku,e_product_id,raw_data,sync_status,sync_dt,sync_notes)\n                                    VALUES\n                                    (%s,%s,%s,%s,NOW(),%s)\n                                    ON DUPLICATE KEY UPDATE\n                                    e_product_id = %s,\n                                    raw_data = %s,\n                                    sync_status = %s,\n                                    sync_notes = %s,\n                                    sync_dt = NOW()\n                                    ;', 
           'listNeedShipOrdersSQL': "\n                                SELECT id, e_order_inc_id,m_order_inc_id, total_qty\n                                FROM m_order\n                                WHERE m_order_status IN ({mOrderStatus}) AND sync_status IN ('O','N')\n                                ", 
           'listOrderExistingShipmentSQL': '\n                                SELECT id,e_shipment_inc_id, m_order_inc_id, sync_status\n                                FROM e_shipment\n                                WHERE m_order_inc_id = %s\n            ', 
           'addOrUpdateEProductMasterSQL': '\n                                INSERT INTO e_product_master\n                                (sku,e_product_id,raw_data,sync_status,sync_dt,sync_notes)\n                                VALUES\n                                (%s,%s,%s,%s,NOW(),%s)\n                                ON DUPLICATE KEY UPDATE\n                                e_product_id = %s,\n                                raw_data = %s,\n                                sync_status = %s,\n                                sync_notes = %s,\n                                sync_dt = NOW()\n            ', 
           'addOrUpdateEProductInventorySQL': '\n                                INSERT INTO e_product_inventory\n                                (sku,website_code,qty,is_in_stock,stock_status,sync_status,sync_dt,sync_notes)\n                                VALUES\n                                (%s,%s,%s,%s,%s,%s,NOW(),%s)\n                                ON DUPLICATE KEY UPDATE\n                                qty = %s,\n                                is_in_stock = %s,\n                                stock_status = %s,\n                                sync_status = %s,\n                                sync_notes = %s,\n                                sync_dt = NOW()\n            ', 
           'addOrUpdateEProductPriceSQL': '\n                                INSERT INTO e_product_price\n                                (sku,website_code,store_code,price,special_price,special_from_date,special_to_date,sync_status,sync_dt,sync_notes)\n                                VALUES\n                                (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s)\n                                ON DUPLICATE KEY UPDATE\n                                price = %s,\n                                special_price = %s,\n                                special_from_date = %s,\n                                special_to_date = %s,\n                                sync_status = %s,\n                                sync_notes = %s,\n                                sync_dt = NOW()\n            ', 
           'addOrUpdateEProductTierPriceSQL': '\n                INSERT INTO e_product_tier_price\n                (sku,all_groups,customer_group,qty,website_code,price,sync_status,sync_dt,sync_notes)\n                VALUES\n                (%s,%s,%s,%s,%s,%s,%s,NOW(),%s)\n                ON DUPLICATE KEY UPDATE\n                price = %s,\n                sync_status = %s,\n                sync_notes = %s,\n                sync_dt = NOW()\n            ', 
           'addOrUpdateEProductGroupPriceSQL': '\n                INSERT INTO e_product_group_price\n                (sku,all_groups,customer_group,website_code,price,sync_status,sync_dt,sync_notes)\n                VALUES\n                (%s,%s,%s,%s,%s,%s,NOW(),%s)\n                ON DUPLICATE KEY UPDATE\n                price = %s,\n                sync_status = %s,\n                sync_notes = %s,\n                sync_dt = NOW()\n            ', 
           'addOrUpdateECustomerSQL': '\n                INSERT INTO e_customer\n                (email,website_code,e_json_data,sync_status,sync_dt,sync_notes)\n                VALUES\n                (%s,%s,%s,%s,NOW(),%s)\n                ON DUPLICATE KEY UPDATE\n                e_json_data = %s,\n                sync_status = %s,\n                sync_notes = %s,\n                sync_dt = NOW()\n            '}
        ERPSyncAbstract.__init__(self, appName, logFileName, dst_conf, functs, queries)
        self.sapb1Queries = {'listEShipmentsSQL': "\n                                SELECT\n                                t0.DocEntry,\n                                t1.BaseEntry,\n                                t1.ShipDate,\n                                t0.TrackNo,\n                                t1.Quantity,\n                                t3.ItemCode,\n                                ISNULL(t2.TrnspName,'')\n                                FROM\n                                ODLN t0 left join DLN1 t1 on (t0.DocEntry = t1.DocEntry)\n                                LEFT JOIN OSHP t2 on (t0.TrnspCode = t2.TrnspCode)\n                                INNER JOIN OITM t3 on t1.ItemCode = t3.ItemCode\n                                WHERE t0.U_MageOrderIncId =%s\n                                ", 
           'listEProductInventorySQL': "\n                                SELECT OITM.ItemCode, OITM.ItemName, SUM(OITW.OnHand - OITW.IsCommited) as qty\n                                FROM OITM\n                                INNER JOIN OITW ON OITM.ItemCode = OITW.ItemCode\n                                WHERE OITW.ItemCode IN (\n                                SELECT DISTINCT ItemCode FROM OITW\n                                WHERE CASE WHEN updateDate IS NULL THEN createDate ELSE updateDate END\n                                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n                                ) AND OITW.WhsCode IN ({0})\n                                AND OITM.U_SYNC = 'Y'\n                                GROUP BY  OITM.ItemCode, OITM.ItemName\n            ", 
           'listEProductPriceSQL': "\n                                SELECT t1.ItemCode, t1.ItemName,  t2.Price\n                                FROM OITM t1,ITM1 t2,OPLN t3\n                                WHERE t1.ItemCode = t2.ItemCode AND\n                                t2.PriceList = t3.ListNum AND\n                                CASE WHEN t1.updateDate IS NULL THEN t1.createDate ELSE t1.updateDate END\n                                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime) AND\n                                t3.ListName = %s\n                                AND t1.U_SYNC = 'Y'\n            ", 
           'listConfigProductSQL': '\n                SELECT\n                [Configurable],[Simple],B.Attributes,B.Attr_Set\n                FROM [Astro_SB_121815].[dbo].[V33_Config_Parent_Mapping] A\n                JOIN [Astro_SB_121815].[dbo].[V33_Magento_Link] B ON A.Configurable = B.sku\n            ', 
           'listEProductTierPriceSQL': "\n                SELECT\n                T0.ItemCode,\n                T4.CardCode AS 'CustomerGroup',\n                CASE WHEN T3.Price > 0 THEN T3.Price ELSE T1.Price END as 'TierPrice'\n                From OITM T0\n                Inner Join ITM1 T1 ON T0.ItemCode = T1.ItemCode\n                Inner Join OPLN T2 On T1.PriceList = T2.ListNum\n                Left JOIN ITM1 T5 ON T0.ItemCode = T5.ItemCode and T5.PriceList = %s\n                FULL OUTER JOIN OCRD T4 ON T4.ListNum = T2.ListNum\n                FULL OUTER JOIN OSPP T3 ON T3.ItemCode = T0.ItemCode and T4.CardCode = T3.CardCode\n                WHERE T4.CardCode is not null\n                AND CASE WHEN T3.Price > 0 THEN T3.Price ELSE T1.Price END > 0\n                AND CASE WHEN T3.Price > 0 THEN T3.Price ELSE T1.Price END ! = T5.Price\n                AND ( CASE WHEN T3.updateDate IS NULL THEN T3.createDate ELSE T3.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime) OR\n                CASE WHEN T0.updateDate IS NULL THEN T0.createDate ELSE T0.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime))\n                ORDER BY\n                T0.ItemCode,\n                T4.CardCode\n            ", 
           'listEProductCompanyPriceSQL': '\n                SELECT T0.ItemCode,\n                T3.CardCode as CompanyCode,\n                T3.Price as CompanyPrice\n                FROM OITM T0\n                INNER JOIN ITM1 T1 ON T0.ItemCode = T1.ItemCode\n                INNER JOIN OPLN T2 On T1.PriceList = T2.ListNum\n                FULL OUTER JOIN OCRD T4 ON T4.ListNum = T2.ListNum\n                FULL OUTER JOIN OSPP T3 ON T3.ItemCode = T0.ItemCode and T4.CardCode = T3.CardCode\n                WHERE\n                T3.CardCode is not null AND\n                ( CASE WHEN T3.updateDate IS NULL THEN T3.createDate ELSE T3.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime) OR\n                CASE WHEN T0.updateDate IS NULL THEN T0.createDate ELSE T0.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime))\n                GROUP BY T0.ItemCode, T3.Price, T3.CardCode\n                ORDER BY T0.ItemCode, T3.CardCode\n            ', 
           'listEProductCategorySQL': '\n                SELECT\n                catprd.U_itemcode AS sku,\n                catg.U_path AS path\n                FROM\n                "@MAGE_CAT_PRD" catprd\n                INNER JOIN "@MAGE_CATEGORY" catg ON catprd.U_cat_id = catg.Code\n            ', 
           'listECompanySQL': "\n                SELECT\n                OCRD.CardCode,\n                OCRD.CardName,\n                OCRD.ValidFor,\n                OPLN.ListName,\n                OSHP.TrnspName,\n                OCRD.IntrntSite,\n                OCPR.CntctCode,\n                OCTG.PymntGroup,\n                OCRD.U_B2B_SYNC\n                FROM OCRD\n                INNER JOIN OPLN ON OCRD.ListNum = OPLN.ListNum\n                LEFT OUTER JOIN OCTG ON OCRD.GroupNum = OCTG.GroupNum\n                LEFT OUTER JOIN OSHP ON OCRD.ShipType = OSHP.TrnspCode\n                INNER JOIN OCPR ON OCRD.CntctPrsn = OCPR.Name AND OCRD.CardCode = OCPR.CardCode\n                WHERE CardType = 'C'\n                AND OCPR.E_MailL is not null AND OCPR.E_MailL != ''\n                AND ( CASE WHEN OCRD.updateDate IS NULL THEN OCRD.createDate ELSE OCRD.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime) OR\n                OCPR.updateDate\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime))\n            ", 
           'listECompanyContactSQL': '\n                SELECT\n                CntctCode,\n                E_MailL,\n                Name,\n                FirstName,\n                MiddleName,\n                LastName,\n                Gender,\n                U_Role\n                FROM\n                OCPR\n                WHERE\n                CardCode = %s\n            ', 
           'listECompanyAddressSQL': '\n                SELECT\n                Address,\n                Street,\n                Block,\n                Building,\n                ZipCode,\n                City,\n                Country,\n                State,\n                AdresType\n                FROM\n                CRD1\n                WHERE CardCode = %s\n            ', 
           'listECustomerSQL': "\n                SELECT\n                OCRD.CardCode,\n                OCRD.CardName,\n                OCRD.ValidFor,\n                OPLN.ListName,\n                OSHP.TrnspName,\n                OCRD.IntrntSite,\n                OCPR.CntctCode,\n                OCTG.PymntGroup,\n                ISNULL(OCRD.E_Mail, OCPR.E_MailL) AS email,\n                OCPR.Name,\n                OCPR.FirstName,\n                OCPR.MiddleName,\n                OCPR.LastName,\n                OCPR.Gender\n                FROM OCRD\n                INNER JOIN OPLN ON OCRD.ListNum = OPLN.ListNum\n                LEFT OUTER JOIN OCTG ON OCRD.GroupNum = OCTG.GroupNum\n                LEFT OUTER JOIN OSHP ON OCRD.ShipType = OSHP.TrnspCode\n                INNER JOIN OCPR ON OCRD.CntctPrsn = OCPR.Name AND OCRD.CardCode = OCPR.CardCode\n                WHERE CardType = 'C'\n                AND OCPR.E_MailL is not null AND OCPR.E_MailL != ''\n                AND ( CASE WHEN OCRD.updateDate IS NULL THEN OCRD.createDate ELSE OCRD.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime) OR\n                OCPR.updateDate\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime))\n            ", 
           'listECustomerAddressSQL': '\n                SELECT\n                Address,\n                Street,\n                Block,\n                Building,\n                ZipCode,\n                City,\n                Country,\n                State,\n                AdresType\n                FROM\n                CRD1\n                WHERE CardCode = %s\n            '}
        if connect_di:
            SAPbobsCOM = __import__(sapb1di_conf['diapi'])
            self.constants = getattr(SAPbobsCOM, 'constants')
            Company = getattr(SAPbobsCOM, 'Company')
            self.company = Company()
            self.company.Server = sapb1di_conf['server']
            self.company.UseTrusted = False
            self.company.language = eval('self.constants.' + sapb1di_conf['language'])
            self.company.DbServerType = eval('self.constants.' + sapb1di_conf['dbservertype'])
            self.company.DbUserName = sapb1di_conf['dbusername']
            self.company.DbPassword = sapb1di_conf['dbpassword']
            self.company.CompanyDB = sapb1di_conf['companydb']
            self.company.UserName = sapb1di_conf['username']
            self.company.Password = sapb1di_conf['password']
            self.company.Connect()
            self.companyName = self.company.CompanyName
            log = 'Open SAPB1 connection for ' + self.companyName
            self.logger.info(log)
        else:
            self.company = None
        self.sapb1Conn = pymssql.connect(sapb1di_conf['server'], sapb1di_conf['dbusername'], sapb1di_conf['dbpassword'], sapb1di_conf['companydb'])
        self.sapb1Cursor = self.sapb1Conn.cursor()
        log = 'Open SAPB1 DB connection'
        self.logger.info(log)
        self.sapb1di_conf = sapb1di_conf
        self._docDuteDate = 1
        self._mOrderCountries = ['US', 'CA']
        self._cardCodeColumn = 'e_customer_id'
        self._taxPostcodeColumn = 'billto_postcode'
        self._taxCountryColumn = 'billto_country'
        self._expenseFreightName = 'Freight'
        self._warehouseCodes = ['Main']
        self._cardCodePrefix = 'M'
        self._priceList = 'Base Price'
        self._paymentMethodsMatrix = {}
        self._productMasterQueryMap = {'fields': {'sku': 'OITM.ItemCode', 
                      'attribute_set_name': 'U_ATTRIBUTE_SET_NAME', 
                      'website_code': 'U_WEBSITE_CODE', 
                      'ItemName': 'OITM.ItemName', 
                      'qty': 'OITM.OnHand-OITM.IsCommited', 
                      'Price': 'ITM1.Price', 
                      'U_SYNC': 'OITM.U_SYNC', 
                      'U_BASE_IMAGE_URL': 'OITM.U_BASE_IMAGE_URL', 
                      'U_ADD_IMAGE_URLS': 'OITM.U_ADD_IMAGE_URLS', 
                      'U_FULL_DESC': 'OITM.U_FULL_DESC', 
                      'U_SHORT_DESC': 'OITM.U_SHORT_DESC', 
                      'SWeight1': 'OITM.SWeight1', 
                      'U_CATEGORY': 'OITM.U_CATEGORY', 
                      'validFor': 'OITM.validFor'}, 
           'source_tables': '\n                FROM OITM\n                LEFT JOIN ITM1 ON OITM.ItemCode = ITM1.ItemCode\n                LEFT JOIN OPLN ON ITM1.PriceList = OPLN.ListNum\n            ', 
           'wheres': "\n                WHERE OITM.SellItem = 'Y' AND OPLN.ListName = %s AND\n                CASE WHEN OITM.updateDate IS NULL THEN OITM.createDate ELSE OITM.updateDate END\n                >= cast(floor(cast(CAST( %s AS datetime) as float)) as datetime)\n            ", 
           'target_table': 'e_product_master'}
        self._bpPaymentMethods = []
        self.dstControl = DSTControl(self.dstCursor)
        self._defaultWebsiteCode = 'admin'
        self._defaultTierPriceMinQty = 1
        self._defaultCompanyPriceMinQty = 1
        self._defaultStoreCode = 'default'
        return

    @property
    def docDuteDate(self):
        return self._docDuteDate

    @docDuteDate.setter
    def docDuteDate(self, value):
        self._docDuteDate = value

    @property
    def mOrderCountries(self):
        return self._mOrderCountries

    @mOrderCountries.setter
    def mOrderCountries(self, value):
        self._mOrderCountries = value

    @property
    def cardCodeColumn(self):
        return self._cardCodeColumn

    @cardCodeColumn.setter
    def cardCodeColumn(self, value):
        self._cardCodeColumn = value

    @property
    def taxPostcodeColumn(self):
        return self._taxPostcodeColumn

    @taxPostcodeColumn.setter
    def taxPostcodeColumn(self, value):
        self._taxPostcodeColumn = value

    @property
    def taxCountryColumn(self):
        return self._taxCountryColumn

    @taxCountryColumn.setter
    def taxCountryColumn(self, value):
        self._taxCountryColumn = value

    @property
    def expenseFreightName(self):
        return self._expenseFreightName

    @expenseFreightName.setter
    def expenseFreightName(self, value):
        self._expenseFreightName = value

    @property
    def warehouseCodes(self):
        return self._warehouseCodes

    @warehouseCodes.setter
    def warehouseCodes(self, value):
        self._warehouseCodes = value

    @property
    def cardCodePrefix(self):
        return self._cardCodePrefix

    @cardCodePrefix.setter
    def cardCodePrefix(self, value):
        self._cardCodePrefix = value

    @property
    def priceList(self):
        return self._priceList

    @priceList.setter
    def priceList(self, value):
        self._priceList = value

    @property
    def paymentMethodsMatrix(self):
        return self._paymentMethodsMatrix

    @paymentMethodsMatrix.setter
    def paymentMethodsMatrix(self, value):
        self._paymentMethodsMatrix = value

    @property
    def productMasterQueryMap(self):
        return self._productMasterQueryMap

    @productMasterQueryMap.setter
    def productMasterQueryMap(self, value):
        self._productMasterQueryMap = value

    @property
    def bpPaymentMethods(self):
        return self._bpPaymentMethods

    @bpPaymentMethods.setter
    def bpPaymentMethods(self, value):
        self._bpPaymentMethods = value

    def __del__(self):
        super(SAPB1Sync2, self).__del__()
        if self.company:
            self.company.Disconnect()
        self.sapb1Conn.close()

    def getDocEntry(self, id, docType):
        sqls = {}
        sqls['oOrders'] = "SELECT DocEntry FROM dbo.ORDR WHERE U_MageOrderIncId = '%s'" % id
        sqls['oInvoices'] = "SELECT DISTINCT t0.DocEntry\n                                FROM dbo.OINV t0, dbo.INV1 t1\n                                WHERE t0.DocEntry = t1.DocEntry\n                                AND t1.BaseType = '%s'\n                                AND t1.BaseEntry = '%s'" % (self.constants.oDeliveryNotes, id)
        sqls['oBusinessPartners'] = "SELECT distinct CardCode FROM OCRD WHERE CardFName = '%s'" % id
        sqls['oDownPayments'] = "SELECT DISTINCT t0.DocEntry\n                                    FROM dbo.ODPI t0, dbo.DPI1 t1\n                                    WHERE t0.DocEntry = t1.DocEntry\n                                    AND t1.BaseType = '%s'\n                                    AND t1.BaseEntry = '%s'" % (self.constants.oOrders, id)
        sqls['dptInvoice'] = "SELECT DocEntry FROM dbo.ODPI WHERE DpmAmnt != DpmAppl AND U_MageOrderIncId = '%s'" % id
        sqls['oBusinessPartnersByEmail'] = "\n            SELECT DISTINCT OCRD.CardCode\n            FROM  OCRD\n            INNER JOIN OCPR ON OCRD.CntctPrsn = OCPR.Name AND OCRD.CardCode = OCPR.CardCode\n            where CardType = 'C'\n            AND ISNULL(OCRD.E_Mail, OCPR.E_MailL) = '%s'\n        " % id
        sqls['oBusinessPartnersByCode'] = "SELECT distinct CardCode FROM OCRD WHERE CardCode = '%s'" % id
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = sqls[docType]
        rs.DoQuery(sql)
        docNum = rs.Fields.Item(0).Value
        return docNum

    def getCntctCode(self, cardCode, mOrder):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        param = {'E_MailL': mOrder['billto_email']}
        sql = "SELECT cntctcode FROM dbo.OCPR WHERE cardcode = '%s' " % cardCode
        for k, v in param.items():
            if v is not None:
                v = v.replace("'", "''")
                sql = sql + "AND %s = '%s' " % (k, v)
            else:
                sql = sql + 'AND %s is null ' % k

        rs.DoQuery(sql)
        cntctCode = rs.Fields.Item(0).Value
        return cntctCode

    def getExpnsCode(self, expnsName):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = "SELECT ExpnsCode FROM dbo.OEXD WHERE ExpnsName = '%s'" % expnsName
        rs.DoQuery(sql)
        expnsCode = rs.Fields.Item(0).Value
        return expnsCode

    def getTrnspCode(self, trnspName):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = "SELECT TrnspCode FROM dbo.OSHP WHERE TrnspName = '%s'" % trnspName
        rs.DoQuery(sql)
        trnspCode = rs.Fields.Item(0).Value
        return trnspCode

    def getTransportationCode(self, shipmentMethod):
        trnspName = None
        if shipmentMethod in self._shipmentMethods.keys():
            trnspName = self._shipmentMethods[shipmentMethod]
        else:
            for k, v in self._shipmentMethods.items():
                if shipmentMethod.find(k) != -1:
                    trnspName = v
                    break

        if trnspName is not None:
            return self.getTrnspCode(trnspName)
        else:
            return
            return

    def getPaymentMethod(self, paymentMethod):
        paymentMethodCode = None
        if paymentMethod in self.paymentMethodsMatrix:
            paymentMethodCode = self.paymentMethodsMatrix[paymentMethod]
        return paymentMethodCode

    def insertCntctCode(self, mOrder):
        busPartner = self.company.GetBusinessObject(self.constants.oBusinessPartners)
        busPartner.GetByKey(mOrder[self._cardCodeColumn])
        current = busPartner.ContactEmployees.Count
        if busPartner.ContactEmployees.InternalCode == 0:
            nextLine = 0
        else:
            nextLine = current
        busPartner.ContactEmployees.Add()
        busPartner.ContactEmployees.SetCurrentLine(nextLine)
        name = mOrder['billto_firstname'] + ' ' + mOrder['billto_lastname']
        name = name[0:36] + ' ' + str(time())
        busPartner.ContactEmployees.Name = name
        busPartner.ContactEmployees.FirstName = mOrder['billto_firstname']
        busPartner.ContactEmployees.LastName = mOrder['billto_lastname']
        busPartner.ContactEmployees.Phone1 = mOrder['billto_telephone']
        busPartner.ContactEmployees.E_Mail = mOrder['billto_email']
        address = mOrder['billto_address'] + ', ' + mOrder['billto_city'] + ', ' + mOrder['billto_region'] + ' ' + mOrder['billto_postcode'] + ', ' + mOrder['billto_country']
        busPartner.ContactEmployees.Address = self.trimValue(address, 100)
        lRetCode = busPartner.Update()
        if lRetCode != 0:
            log = self.company.GetLastErrorDescription()
            self.logger.error(log)
            raise Exception(log)
        return self.getCntctCode(mOrder[self._cardCodeColumn], mOrder)

    def getContactPersonCode(self, mOrder):
        contactPersonCode = self.getCntctCode(mOrder[self._cardCodeColumn], mOrder)
        if contactPersonCode == 0:
            try:
                contactPersonCode = self.insertCntctCode(mOrder)
            except Exception as e:
                log = str(e)
                self.logger.error(log)
                raise

        return contactPersonCode

    def getDfCurrency(self):
        rs = self.company.GetBusinessObject(self.constants.BoRecordset)
        sql = 'SELECT MainCurncy FROM dbo.OADM'
        rs.DoQuery(sql)
        dfcurrency = rs.Fields.Item(0).Value
        rs.MoveNext()
        return dfcurrency

    def getTaxCode(self, lineTotal, taxAmt, postcode, country):
        taxCode = self._taxMetrics['Exempt']
        for k, v in self._taxMetrics['code_rate'].items():
            if abs(round(lineTotal * v['rate'] / 100 - taxAmt)) == 0 and (int(postcode) in range(int(v['postcode'][0]), int(v['postcode'][(-1)])) or postcode in v['postcode']) and country == v['country']:
                taxCode = k
                break

        return taxCode

    def trimValue(self, value, maxLength):
        if len(value) > maxLength:
            return value[0:maxLength - 1]
        return value

    def getCardCodeByECustomerId(self, eCustomerId, mOrder):
        return eCustomerId

    def b1eOrderFunct(self, mOrder):
        mOrder['billto_telephone'] = self.trimValue(mOrder['billto_telephone'], 20)
        mOrder['billto_address'] = self.trimValue(mOrder['billto_address'], 100)
        mOrder['shipto_address'] = self.trimValue(mOrder['shipto_address'], 100)
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.DocDueDate = datetime.now() + timedelta(days=self._docDuteDate)
        order.CardCode = self.getCardCodeByECustomerId(mOrder[self._cardCodeColumn], mOrder)
        mOrder[self._cardCodeColumn] = order.CardCode
        name = mOrder['billto_firstname'] + ' ' + mOrder['billto_lastname']
        name = name[0:50]
        order.CardName = name
        order.DocCurrency = self.getDfCurrency()
        order.ContactPersonCode = self.getContactPersonCode(mOrder)
        if self._expenseFreightName is not None:
            order.Expenses.ExpenseCode = self.getExpnsCode(self._expenseFreightName)
            order.Expenses.LineTotal = mOrder['shipping_amt']
            taxCode = self.getTaxCode(float(mOrder['shipping_amt']), float(mOrder['shipping_tax_amt']), mOrder[self._taxPostcodeColumn], mOrder[self._taxCountryColumn])
            order.Expenses.TaxCode = taxCode
        if mOrder['discount_amt'] != 0:
            order.DiscountPercent = abs(mOrder['discount_amt']) / mOrder['sub_total'] * 100
        transportationCode = self.getTransportationCode(mOrder['shipment_method'])
        if transportationCode is not None:
            order.TransportationCode = transportationCode
        paymentMethodCode = self.getPaymentMethod(mOrder['payment_method'])
        if paymentMethodCode is not None:
            order.PaymentMethod = paymentMethodCode
        order.UserFields.Fields.Item('U_MageOrderIncId').Value = str(mOrder['m_order_inc_id'])
        order.AddressExtension.BillToCity = mOrder['billto_city']
        order.AddressExtension.BillToCountry = mOrder['billto_country']
        if mOrder['billto_country'] in self._mOrderCountries:
            order.AddressExtension.BillToState = mOrder['billto_region']
        order.AddressExtension.BillToStreet = mOrder['billto_address']
        order.AddressExtension.BillToZipCode = mOrder['billto_postcode']
        order.AddressExtension.ShipToCity = mOrder['shipto_city']
        order.AddressExtension.ShipToCountry = mOrder['shipto_country']
        if mOrder['shipto_country'] in self._mOrderCountries:
            order.AddressExtension.ShipToState = mOrder['shipto_region']
        order.AddressExtension.ShipToStreet = mOrder['shipto_address']
        order.AddressExtension.ShipToZipCode = mOrder['shipto_postcode']
        return order

    def b1eOrderExtFunct(self, order, mOrder):
        pass

    def b1eOrderIncIdFunct(self, mOrder):
        eOrderIncId = self.getDocEntry(str(mOrder['m_order_inc_id']), 'oOrders')
        if str(eOrderIncId) == '0':
            return
        else:
            return eOrderIncId
            return

    def b1eOrderLineFunct(self, i, order, item, mOrder):
        order.Lines.Add()
        order.Lines.SetCurrentLine(i)
        order.Lines.ItemCode = item['sku']
        order.Lines.Quantity = int(item['qty'])
        order.Lines.Price = decimal.Decimal(item['price'])
        lineTotal = order.Lines.Price * order.Lines.Quantity
        taxCode = self.getTaxCode(lineTotal, float(item['tax_amt']), mOrder[self._taxPostcodeColumn], mOrder[self._taxCountryColumn])
        order.Lines.TaxCode = taxCode
        order.Lines.LineTotal = lineTotal

    def b1eOrderLineExtFunct(self, i, order, item, mOrder):
        pass

    def addB1EOrderFunct(self, order):
        mOrderIncId = order.UserFields.Fields.Item('U_MageOrderIncId').Value
        lRetCode = order.Add()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)
        else:
            eOrderIncId = self.getDocEntry(mOrderIncId, 'oOrders')
            return eOrderIncId

    def cancelB1EOrderFunct(self, mOrder):
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.GetByKey(self.b1eOrderIncIdFunct(mOrder))
        lRetCode = order.Cancel()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)

    def b1eOrderRFunct(self, mDownPaymwent):
        order = self.company.GetBusinessObject(self.constants.oOrders)
        order.GetByKey(mDownPaymwent['e_order_inc_id'])
        orderItemCount = order.Lines.Count
        return (
         order, orderItemCount)

    def b1eDownPaymentFunct(self, order, mDownPayment):
        downPayment = self.company.GetBusinessObject(self.constants.oDownPayments)
        downPayment.CardName = order.CardName
        downPayment.DownPaymentType = self.constants.dptInvoice
        downPayment.DocTotal = float(mDownPayment['grand_total'])
        return downPayment

    def b1eDownPaymentExtFunct(self, downPayment, order):
        pass

    def b1eDownPaymentLineFunct(self, i, downPayment, order):
        order.Lines.SetCurrentLine(i)
        downPayment.Lines.Add()
        downPayment.Lines.SetCurrentLine(i)
        downPayment.Lines.ItemCode = order.Lines.ItemCode
        downPayment.Lines.Quantity = order.Lines.Quantity
        downPayment.Lines.BaseEntry = order.DocEntry
        downPayment.Lines.BaseLine = order.Lines.LineNum
        downPayment.Lines.BaseType = self.constants.oOrders

    def b1eDownPaymentLineExtFunct(self, i, downPayment, order):
        pass

    def b1eDownPaymentIncIdFunct(self, mDownPayment):
        eDownPaymentIncId = self.getDocEntry(mDownPayment['e_order_inc_id'], 'oDownPayments')
        if str(eDownPaymentIncId) == '0':
            return
        else:
            return eDownPaymentIncId
            return

    def addB1EDownPaymentFunct(self, downPayment, order):
        lRetCode = downPayment.Add()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)
        else:
            eDownPaymentIncId = self.getDocEntry(order.DocEntry, 'oDownPayments')
            return eDownPaymentIncId

    def b1eShipRFunct(self, mInvoice):
        shipment = self.company.GetBusinessObject(self.constants.oDeliveryNotes)
        shipment.GetByKey(mInvoice['e_shipment_inc_id'])
        shipmentItemCount = shipment.Lines.Count
        return (
         shipment, shipmentItemCount)

    def b1eInvoiceFunct(self, shipment, mInvoice):
        invoice = self.company.GetBusinessObject(self.constants.oInvoices)
        invoice.CardName = shipment.CardName
        invoice.UserFields.Fields.Item('U_MageInvoiceIncId').Value = str(mInvoice['m_invoice_inc_id'])
        eDownPaymentIncId = self.getDocEntry(mInvoice['m_order_inc_id'], 'dptInvoice')
        if eDownPaymentIncId != 0:
            invoice.DownPaymentsToDraw.DocEntry = eDownPaymentIncId
            invoice.DownPaymentsToDraw.GrossAmountToDraw = shipment.DocTotal
        for i in range(0, shipment.Expenses.Count):
            shipment.Expenses.SetCurrentLine(i)
            if shipment.Expenses.LineTotal > 0:
                invoice.Expenses.Add()
                invoice.Expenses.SetCurrentLine(i)
                invoice.Expenses.BaseDocType = self.constants.oDeliveryNotes
                invoice.Expenses.BaseDocLine = shipment.Expenses.LineNum
                invoice.Expenses.BaseDocEntry = shipment.DocEntry

        return invoice

    def b1eInvoiceExtFunct(self, invoice, shipment):
        pass

    def b1eInvoiceLineFunct(self, i, invoice, shipment):
        shipment.Lines.SetCurrentLine(i)
        invoice.Lines.Add()
        invoice.Lines.SetCurrentLine(i)
        invoice.Lines.ItemCode = shipment.Lines.ItemCode
        invoice.Lines.Quantity = shipment.Lines.Quantity
        invoice.Lines.BaseEntry = shipment.DocEntry
        invoice.Lines.BaseLine = shipment.Lines.LineNum
        invoice.Lines.BaseType = self.constants.oDeliveryNotes

    def b1eInvoiceLineExtFunct(self, i, invoice, shipment):
        pass

    def b1eInvoiceIncIdFunct(self, mInvoice):
        eInvoiceIncId = self.getDocEntry(mInvoice['e_shipment_inc_id'], 'oInvoices')
        if str(eInvoiceIncId) == '0':
            return
        else:
            return eInvoiceIncId
            return

    def addB1EInvoiceFunct(self, invoice, shipment):
        lRetCode = invoice.Add()
        if lRetCode != 0:
            error = str(self.company.GetLastError())
            self.logger.error(error)
            raise Exception(error)
        else:
            eInvoiceIncId = self.getDocEntry(shipment.DocEntry, 'oInvoices')
            return eInvoiceIncId

    def setCustPaymentMethods(self, customer):
        existingPaymentMethods = []
        cnt = customer.BPPaymentMethods.Count
        for i in range(0, cnt):
            customer.BPPaymentMethods.SetCurrentLine(i)
            if str(customer.BPPaymentMethods.PaymentMethodCode).strip() != '':
                existingPaymentMethods.append(customer.BPPaymentMethods.PaymentMethodCode)

        needAddPaymentMethods = list(set(self.bpPaymentMethods) - set(existingPaymentMethods))
        cnt = len(existingPaymentMethods)
        for paymentMethodCode in needAddPaymentMethods:
            customer.BPPaymentMethods.Add()
            customer.BPPaymentMethods.SetCurrentLine(cnt)
            customer.BPPaymentMethods.PaymentMethodCode = paymentMethodCode
            cnt = cnt + 1

    def b1eCustFunct(self, mCustomer):
        customer = self.company.GetBusinessObject(self.constants.oBusinessPartners)
        cardCode = self.getDocEntry(mCustomer['m_cust_inc_id'], 'oBusinessPartners')
        exist = 1 if cardCode != 0 and str(cardCode).strip() != '' else 0
        if exist == 1:
            customer.GetByKey(cardCode)
        else:
            customer.CardCode = 'C' + self._cardCodePrefix + str(mCustomer['m_cust_inc_id'])
            customer.CardForeignName = mCustomer['m_cust_inc_id']
            customer.CardName = mCustomer['firstname'] + ' ' + mCustomer['lastname']
            customer.CardType = self.constants.cCustomer
            customer.CompanyPrivate = self.constants.cPrivate
            customer.EmailAddress = mCustomer['email']
        return (customer, exist)

    def b1eCustExtFunct(self, customer, mCustomer):
        pass

    def b1eCustAddrFunct(self, i, customer, address, mCustomer):
        customer.Addresses.Add()
        customer.Addresses.SetCurrentLine(i)
        customer.Addresses.AddressName = 'Address' + str(i + 1)
        customer.Addresses.ZipCode = address['postcode']
        customer.Addresses.Street = address['street']
        customer.Addresses.City = address['city']
        customer.Addresses.Country = address['country_id']
        if 'region_id' in address:
            customer.Addresses.State = address['region_id']
        if mCustomer['default_billing'] == address['entity_id']:
            customer.Addresses.AddressType = self.constants.bo_BillTo
        if mCustomer['default_shipping'] == address['entity_id']:
            customer.Addresses.AddressType = self.constants.bo_ShipTo

    def b1eCustAddrExtFunct(self, i, customer, address, mCustomer):
        pass

    def b1eCustContFunct(self, i, customer, contact, mCustomer):
        customer.ContactEmployees.Add()
        customer.ContactEmployees.SetCurrentLine(i)
        name = contact['firstname'] + ' ' + contact['lastname'] + ' ' + str(time())
        customer.ContactEmployees.Name = name
        customer.ContactEmployees.FirstName = contact['firstname']
        customer.ContactEmployees.LastName = contact['lastname']
        customer.ContactEmployees.E_Mail = contact['email']

    def b1eCustContExtFunct(self, i, customer, contact, mCustomer):
        pass

    def addUpdateB1ECustFunct(self, customer, exist):
        if exist == 0:
            lRetCode = customer.Add()
        else:
            lRetCode = customer.Update()
        if lRetCode != 0:
            log = self.company.GetLastErrorDescription()
            self.logger.error(log)
            raise Exception(log)
        else:
            eCustIncId = self.getDocEntry(customer.CardForeignName, 'oBusinessPartners')
            return eCustIncId

    def getOrderExistingShipment(self, mOrderIncId):
        self.dstCursor.execute(self.queries.listOrderExistingShipmentSQL, [mOrderIncId])
        rows = self.dstCursor.fetchall()
        shippingDocEntries = []
        for row in rows:
            shippingDocEntries.append(str(row['e_shipment_inc_id']))

        return shippingDocEntries

    def b1eShipsFunct(self):
        orderStatusFormatString = (',').join(['%s'] * len(self.needShipOrderStatus))
        self.queries.listNeedShipOrdersSQL = self.queries.listNeedShipOrdersSQL.format(mOrderStatus=orderStatusFormatString)
        self.dstCursor.execute(self.queries.listNeedShipOrdersSQL, self.needShipOrderStatus)
        needShipOrders = self.dstCursor.fetchall()
        eShips = {}
        for needShipOrder in needShipOrders:
            mOrderIncId = needShipOrder['m_order_inc_id']
            existingShipments = self.getOrderExistingShipment(mOrderIncId)
            self.sapb1Cursor.execute(self.sapb1Queries['listEShipmentsSQL'], mOrderIncId)
            b1Shipments = self.sapb1Cursor.fetchall()
            for biShipment in b1Shipments:
                eShipmentIncId, eOrderIncId, shipDt, trackNo, qty, itemCode, carrier = biShipment
                eShipmentIncId = str(eShipmentIncId)
                if qty is None or int(qty) <= 0:
                    continue
                if eShipmentIncId not in eShips and eShipmentIncId not in existingShipments:
                    eShips[eShipmentIncId] = {'m_order_inc_id': mOrderIncId, 'e_shipment_inc_id': eShipmentIncId, 
                       'ship_dt': shipDt, 
                       'tracking': trackNo, 
                       'carrier': carrier, 
                       'items': [
                               {'sku': itemCode, 
                                  'qty': qty}]}
                elif eShipmentIncId in eShips:
                    eShips[eShipmentIncId]['items'].append({'sku': itemCode, 
                       'qty': qty})

        return eShips.values()

    def b1mShipFunct(self, eShip):
        mShip = eShip
        shipmentItemCount = len(eShip['items'])
        return (
         mShip, shipmentItemCount)

    def b1mShipExtFunct(self, mShip, eShip):
        pass

    def b1mShipItemFunct(self, i, mShip, eShip):
        pass

    def b1mShipItemExtFunct(self, i, mShip, eShip):
        pass

    def fetchCursorResultAsDict(self, cursor):
        result = []
        columns = tuple([ d[0].decode('utf8') for d in cursor.description ])
        for row in cursor:
            result.append(dict(zip(columns, row)))

        return result

    def generateB1GetProductSQL(self):
        parts = [
         'SELECT']
        selectParts = []
        for alias, columnName in self.productMasterQueryMap['fields'].items():
            selectParts.append(('{0} as {1}').format(columnName, alias))

        parts.append((',\n').join(selectParts))
        parts.append(self.productMasterQueryMap['source_tables'])
        parts.append(self.productMasterQueryMap['wheres'])
        sql = ('\n').join(parts)
        return sql

    def b1eProductsFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        b1eProductsSQL = self.generateB1GetProductSQL()
        self.sapb1Cursor.execute(b1eProductsSQL, (self.priceList, lastCutoffDt))
        eProducts = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProducts

    def b1mProductFunct(self, eProduct):
        sku = eProduct['sku']
        for k, v in eProduct.items():
            if isinstance(v, datetime):
                eProduct[k] = str(v)

        rawData = json.dumps(eProduct, cls=DecimalEncoder)
        mProduct = {'sku': sku, 
           'e_product_id': None, 
           'raw_data': rawData, 
           'sync_status': 'N', 
           'sync_notes': 'SAPB1 to DST'}
        return mProduct

    def b1mProductExtFunct(self, mProduct, eProduct):
        pass

    def addUpdateB1MProductFunct(self, mProduct):
        param = [
         mProduct['sku'],
         mProduct['e_product_id'],
         mProduct['raw_data'],
         mProduct['sync_status'],
         mProduct['sync_notes'],
         mProduct['e_product_id'],
         mProduct['raw_data'],
         mProduct['sync_status'],
         mProduct['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductMasterSQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsInventoryFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        formatString = (',').join(['%s'] * len(self.warehouseCodes))
        self.sapb1Queries['listEProductInventorySQL'] = self.sapb1Queries['listEProductInventorySQL'].format(formatString)
        params = [
         lastCutoffDt] + self.warehouseCodes
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductInventorySQL'], params)
        eProductsInventory = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsInventory

    def b1mProductInventoryFunct(self, eProductInventory):
        sku = eProductInventory['ItemCode']
        qty = eProductInventory['qty']
        if qty > 0:
            isInStock = 1
            stockStatus = 1
        else:
            isInStock = 0
            stockStatus = 0
        websiteCode = 'admin'
        mProductInventory = {'sku': sku, 
           'website_code': websiteCode, 
           'qty': qty, 
           'is_in_stock': isInStock, 
           'stock_status': stockStatus, 
           'sync_status': 'N', 
           'sync_notes': 'SAPB1 to DST'}
        return mProductInventory

    def b1mProductInventoryExtFunct(self, mProductInventory, eProductInventory):
        pass

    def addUpdateB1MProductInventoryFunct(self, mProductInventory):
        param = [
         mProductInventory['sku'],
         mProductInventory['website_code'],
         mProductInventory['qty'],
         mProductInventory['is_in_stock'],
         mProductInventory['stock_status'],
         mProductInventory['sync_status'],
         mProductInventory['sync_notes'],
         mProductInventory['qty'],
         mProductInventory['is_in_stock'],
         mProductInventory['stock_status'],
         mProductInventory['sync_status'],
         mProductInventory['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductInventorySQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsPriceFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt] + [self.priceList]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductPriceSQL'], params)
        eProductsPrice = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsPrice

    def b1mProductPriceFunct(self, eProductPrice):
        sku = eProductPrice['ItemCode']
        price = eProductPrice['Price']
        websiteCode = 'admin'
        storeCode = 'admin'
        mProductPrice = {'sku': sku, 
           'website_code': websiteCode, 
           'store_code': storeCode, 
           'price': price, 
           'special_price': None, 
           'special_from_date': None, 
           'special_to_date': None, 
           'sync_status': 'N', 
           'sync_notes': 'SAPB1 to DST'}
        return mProductPrice

    def b1mProductPriceExtFunct(self, mProductPrice, eProductPrice):
        pass

    def addUpdateB1MProductPriceFunct(self, mProductPrice):
        param = [
         mProductPrice['sku'],
         mProductPrice['website_code'],
         mProductPrice['store_code'],
         mProductPrice['price'],
         mProductPrice['special_price'],
         mProductPrice['special_from_date'],
         mProductPrice['special_to_date'],
         mProductPrice['sync_status'],
         mProductPrice['sync_notes'],
         mProductPrice['price'],
         mProductPrice['special_price'],
         mProductPrice['special_from_date'],
         mProductPrice['special_to_date'],
         mProductPrice['sync_status'],
         mProductPrice['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductPriceSQL, param)
        return self.dstCursor.lastrowid

    def b1eConfigProductsFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        self.sapb1Cursor.execute(self.sapb1Queries['listConfigProductSQL'], lastCutoffDt)
        eConfigProducts = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eConfigProducts

    def b1mConfigProductFunct(self, eConfigProduct):
        parentSku = eConfigProduct['Configurable']
        childSku = eConfigProduct['Simple']
        for k, v in eConfigProduct.items():
            if isinstance(v, datetime):
                eConfigProduct[k] = str(v)

        eConfigProduct['action'] = 'addOrUpdate'
        rawData = json.dumps(eConfigProduct, cls=DecimalEncoder)
        mConfigProduct = {'parent_sku': parentSku, 
           'child_sku': childSku, 
           'raw_data': rawData, 
           'sync_status': 'N', 
           'sync_notes': 'SAPB1 to DST'}
        return mConfigProduct

    def b1mConfigProductExtFunct(self, mConfigProduct, eConfigProduct):
        pass

    def addUpdateB1MConfigProductFunct(self, mConfigProduct):
        param = [
         mConfigProduct['parent_sku'],
         mConfigProduct['child_sku'],
         mConfigProduct['raw_data'],
         mConfigProduct['sync_status'],
         mConfigProduct['sync_notes'],
         mConfigProduct['raw_data'],
         mConfigProduct['sync_status'],
         mConfigProduct['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEConfigProductSQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsGroupPriceFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt] + [self.priceList]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductGroupPriceSQL'], params)
        eProductsPrice = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsPrice

    def b1mProductGroupPriceFunct(self, eProductGroupPrice):
        websiteCode = self._defaultWebsiteCode
        mProductGroupPrice = {'sku': eProductGroupPrice['sku'], 
           'all_groups': eProductGroupPrice['all_groups'], 
           'customer_group': eProductGroupPrice['customer_group'], 
           'price': eProductGroupPrice['price'], 
           'website_code': websiteCode, 
           'sync_status': 'N', 
           'sync_notes': 'ERP to DST'}
        return mProductGroupPrice

    def b1mProductGroupPriceExtFunct(self, mProductGroupPrice, eProductGroupPrice):
        pass

    def addUpdateB1MProductGroupPriceFunct(self, mProductGroupPrice):
        param = [
         mProductGroupPrice['sku'],
         mProductGroupPrice['all_groups'],
         mProductGroupPrice['customer_group'],
         mProductGroupPrice['website_code'],
         mProductGroupPrice['price'],
         mProductGroupPrice['sync_status'],
         mProductGroupPrice['sync_notes'],
         mProductGroupPrice['price'],
         mProductGroupPrice['sync_status'],
         mProductGroupPrice['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductGroupPriceSQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsTierPriceFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [self.priceList, lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductTierPriceSQL'], params)
        eProductsTierPrice = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsTierPrice

    def b1mProductTierPriceFunct(self, eProductTierPrice):
        websiteCode = self._defaultWebsiteCode
        mProductTierPrice = {'sku': eProductTierPrice['ItemCode'], 
           'all_groups': 0, 
           'customer_group': eProductTierPrice['CustomerGroup'], 
           'qty': self._defaultTierPriceMinQty, 
           'price': eProductTierPrice['TierPrice'], 
           'website_code': websiteCode, 
           'sync_status': 'N', 
           'sync_notes': 'ERP to DST'}
        return mProductTierPrice

    def b1mProductTierPriceExtFunct(self, mProductTierPrice, eProductTierPrice):
        pass

    def addUpdateB1MProductTierPriceFunct(self, mProductTierPrice):
        param = [
         mProductTierPrice['sku'],
         mProductTierPrice['all_groups'],
         mProductTierPrice['customer_group'],
         mProductTierPrice['qty'],
         mProductTierPrice['website_code'],
         mProductTierPrice['price'],
         mProductTierPrice['sync_status'],
         mProductTierPrice['sync_notes'],
         mProductTierPrice['price'],
         mProductTierPrice['sync_status'],
         mProductTierPrice['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductTierPriceSQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsCompanyPriceFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductCompanyPriceSQL'], params)
        eProductsCompanyPrice = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsCompanyPrice

    def b1mProductCompanyPriceFunct(self, eProductCompanyPrice):
        websiteCode = self._defaultWebsiteCode
        mProductCompanyPrice = {'sku': eProductCompanyPrice['ItemCode'], 
           'company_code': eProductCompanyPrice['CompanyCode'], 
           'qty': self._defaultCompanyPriceMinQty, 
           'price': eProductCompanyPrice['CompanyPrice'], 
           'website_code': websiteCode, 
           'sync_status': 'N', 
           'sync_notes': 'ERP to DST'}
        return mProductCompanyPrice

    def b1mProductCompanyPriceExtFunct(self, mProductCompanyPrice, eProductCompanyPrice):
        pass

    def addUpdateB1MProductCompanyPriceFunct(self, mProductCompanyPrice):
        param = [
         mProductCompanyPrice['sku'],
         mProductCompanyPrice['company_code'],
         mProductCompanyPrice['qty'],
         mProductCompanyPrice['website_code'],
         mProductCompanyPrice['price'],
         mProductCompanyPrice['sync_status'],
         mProductCompanyPrice['sync_notes'],
         mProductCompanyPrice['price'],
         mProductCompanyPrice['sync_status'],
         mProductCompanyPrice['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductCompanyPriceSQL, param)
        return self.dstCursor.lastrowid

    def b1eProductsCategoryFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listEProductCategorySQL'], params)
        eProductsCategory = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eProductsCategory

    def b1mProductCategoryFunct(self, eProductCategory):
        websiteCode = self._defaultWebsiteCode
        storeCode = self._defaultStoreCode
        mProductCategory = {'sku': eProductCategory['sku'], 
           'path': eProductCategory['path'], 
           'store_code': storeCode, 
           'action': 'insertOrUpdate', 
           'sync_status': 'N', 
           'sync_notes': 'ERP to DST'}
        return mProductCategory

    def b1mProductCategoryExtFunct(self, mProductCategory, eProductCategory):
        pass

    def addUpdateB1MProductCategoryFunct(self, mProductCategory):
        param = [
         mProductCategory['sku'],
         mProductCategory['path'],
         mProductCategory['store_code'],
         mProductCategory['action'],
         mProductCategory['sync_status'],
         mProductCategory['sync_notes']]
        self.dstCursor.execute(self.queries.addOrUpdateEProductCategorySQL, param)
        return self.dstCursor.lastrowid

    def xstr(self, s):
        if s is None:
            return ''
        else:
            return s

    def b1eComanyAddresses(self, eCompany):
        cardCode = eCompany['CardCode']
        self.sapb1Cursor.execute(self.sapb1Queries['listECompanyAddressSQL'], cardCode)
        eAddresses = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eAddresses

    def b1eCompanyContacts(self, eCompany):
        cardCode = eCompany['CardCode']
        self.sapb1Cursor.execute(self.sapb1Queries['listECompanyContactSQL'], cardCode)
        eContacts = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eContacts

    def b1eCompanysFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listECompanySQL'], params)
        eCompanys = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eCompanys

    def b1mCompanyFunct(self, eCompany):
        eCompany['addresses'] = self.b1eComanyAddresses(eCompany)
        eCompany['contacts'] = self.b1eCompanyContacts(eCompany)
        eCompany['company_code'] = eCompany['CardCode']
        eCompany['website_code'] = self._defaultWebsiteCode
        company = eCompany
        companyAddressCount = len(eCompany['addresses'])
        companyContactCount = len(eCompany['contacts'])
        return (
         company, companyAddressCount, companyContactCount)

    def b1mCompanyExtFunct(self, company, eCompany):
        pass

    def b1mCompanyAddressFunct(self, i, company, eCompany):
        for address in company['addresses']:
            uniqueId = address['AdresType'] + '-' + address['Address']
            address['Street2'] = self.xstr(address['Block']) + ', ' + self.xstr(address['Building'])
            address['unique_id'] = uniqueId

    def b1mCompanyAddressExtFunct(self, i, company, eCompany):
        pass

    def b1mCompanyContactFunct(self, i, company, eCompany):
        for contact in company['contacts']:
            uniqueId = contact['E_MailL']
            if self.xstr(contact['U_Role']) == '':
                if eCompany['CntctCode'] == contact['CntctCode']:
                    contact['U_Role'] = 'Admin'
                else:
                    contact['U_Role'] = 'Manager'
            contact['unique_id'] = uniqueId

    def b1mCompanyContactExtFunct(self, i, company, eCompany):
        pass

    def b1eCustomerAddresses(self, eCustomer):
        cardCode = eCustomer['CardCode']
        self.sapb1Cursor.execute(self.sapb1Queries['listECustomerAddressSQL'], cardCode)
        eAddresses = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eAddresses

    def b1eCustomersFunct(self, task):
        lastCutoffDt = self.dstControl.getTaskLastCutoffDate(task)
        params = [lastCutoffDt, lastCutoffDt]
        params = tuple(params)
        self.sapb1Cursor.execute(self.sapb1Queries['listECustomerSQL'], params)
        eCustomers = self.fetchCursorResultAsDict(self.sapb1Cursor)
        return eCustomers

    def b1mCustomerFunct(self, eCustomer):
        eCustomer['addresses'] = self.b1eCustomerAddresses(eCustomer)
        eCustomer['website_code'] = self._defaultWebsiteCode
        customer = eCustomer
        customerAddressCount = len(eCustomer['addresses'])
        return (
         customer, customerAddressCount)

    def b1mCustomerExtFunct(self, customer, eCustomer):
        pass

    def b1mCustomerAddressFunct(self, i, customer, eCustomer):
        for address in customer['addresses']:
            uniqueId = address['AdresType'] + '-' + address['Address']
            address['unique_id'] = uniqueId

    def b1mCustomerAddressExtFunct(self, i, customer, eCustomer):
        pass
# okay decompiling SAPB1Sync2.pyc
