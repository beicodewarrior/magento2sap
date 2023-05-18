# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\ERPAbstract\DefaultFunctions.py
# Compiled at: 2016-07-26 09:39:58
DEFAULTFUNCTIONS = {'eOrderFunct': {'parent': 'self', 
                   'name': 'erpOrderFunct', 
                   'vars': [
                          'mOrder'], 
                   'return': [
                            'order']}, 
   'eOrderExtFunct': {'parent': 'self', 
                      'name': 'erpOrderExtFunct', 
                      'vars': [
                             'order', 'mOrder'], 
                      'return': []}, 
   'eOrderLineFunct': {'parent': 'self', 
                       'name': 'erpOrderLineFunct', 
                       'vars': [
                              'i', 'order', 'item', 'mOrder'], 
                       'return': []}, 
   'eOrderLineExtFunct': {'parent': 'self', 
                          'name': 'erpOrderLineExtFunct', 
                          'vars': [
                                 'i', 'order', 'item', 'mOrder'], 
                          'return': []}, 
   'addEOrderFunct': {'parent': 'self', 
                      'name': 'addERPOrderFunct', 
                      'vars': [
                             'order'], 
                      'return': [
                               'eOrderIncId']}, 
   'cancelEOrderFunct': {'parent': 'self', 
                         'name': 'cancelERPOrderFunct', 
                         'vars': [
                                'mOrder'], 
                         'return': []}, 
   'eOrderRFunct': {'parent': 'self', 
                    'name': 'erpOrderRFunct', 
                    'vars': [
                           'mDownPayment'], 
                    'return': [
                             'order', 'orderItemCount']}, 
   'eDownPaymentFunct': {'parent': 'self', 
                         'name': 'erpDownPaymentFunct', 
                         'vars': [
                                'order', 'mDownPayment'], 
                         'return': [
                                  'downPayment']}, 
   'eDownPaymentExtFunct': {'parent': 'self', 
                            'name': 'erpDownPaymentExtFunct', 
                            'vars': [
                                   'downPayment', 'order'], 
                            'return': []}, 
   'eDownPaymentLineFunct': {'parent': 'self', 
                             'name': 'erpDownPaymentLineFunct', 
                             'vars': [
                                    'i', 'downPayment', 'order'], 
                             'return': []}, 
   'eDownPaymentLineExtFunct': {'parent': 'self', 
                                'name': 'erpDownPaymentLineExtFunct', 
                                'vars': [
                                       'i', 'downPayment', 'order'], 
                                'return': []}, 
   'eDownPaymentIncIdFunct': {'parent': 'self', 
                              'name': 'erpDownPaymentIncIdFunct', 
                              'vars': [
                                     'mDownPayment'], 
                              'return': [
                                       'eDownPaymentIncId']}, 
   'addEDownPaymentFunct': {'parent': 'self', 
                            'name': 'addERPDownPaymentFunct', 
                            'vars': [
                                   'downPayment', 'order'], 
                            'return': [
                                     'eDownPaymentIncId']}, 
   'eCustFunct': {'parent': 'self', 
                  'name': 'erpCustFunct', 
                  'vars': [
                         'mCustomer'], 
                  'return': [
                           'customer', 'exist']}, 
   'eCustExtFunct': {'parent': 'self', 
                     'name': 'erpCustExtFunct', 
                     'vars': [
                            'customer', 'mCustomer'], 
                     'return': []}, 
   'eCustAddrFunct': {'parent': 'self', 
                      'name': 'erpCustAddrFunct', 
                      'vars': [
                             'i', 'customer', 'address', 'mCustomer'], 
                      'return': []}, 
   'eCustAddrExtFunct': {'parent': 'self', 
                         'name': 'erpCustAddrExtFunct', 
                         'vars': [
                                'i', 'customer', 'address', 'mCustomer'], 
                         'return': []}, 
   'eCustContFunct': {'parent': 'self', 
                      'name': 'erpCustContFunct', 
                      'vars': [
                             'i', 'customer', 'contact', 'mCustomer'], 
                      'return': []}, 
   'eCustContExtFunct': {'parent': 'self', 
                         'name': 'erpCustContExtFunct', 
                         'vars': [
                                'i', 'customer', 'contact', 'mCustomer'], 
                         'return': []}, 
   'addUpdateECustFunct': {'parent': 'self', 
                           'name': 'addUpdateERPCustFunct', 
                           'vars': [
                                  'customer', 'exist'], 
                           'return': [
                                    'eCustIncId']}, 
   'eShipRFunct': {'parent': 'self', 
                   'name': 'erpShipRFunct', 
                   'vars': [
                          'mInvoice'], 
                   'return': [
                            'shipment', 'shipItemCount']}, 
   'eInvoiceFunct': {'parent': 'self', 
                     'name': 'erpInvoiceFunct', 
                     'vars': [
                            'shipment', 'mInvoice'], 
                     'return': [
                              'invoice']}, 
   'eInvoiceExtFunct': {'parent': 'self', 
                        'name': 'erpInvoiceExtFunct', 
                        'vars': [
                               'invoice', 'shipment'], 
                        'return': []}, 
   'eInvoiceLineFunct': {'parent': 'self', 
                         'name': 'erpInvoiceLineFunct', 
                         'vars': [
                                'i', 'invoice', 'shipment'], 
                         'return': []}, 
   'eInvoiceLineExtFunct': {'parent': 'self', 
                            'name': 'erpInvoiceLineExtFunct', 
                            'vars': [
                                   'i', 'invoice', 'shipment'], 
                            'return': []}, 
   'eInvoiceIncIdFunct': {'parent': 'self', 
                          'name': 'erpInvoiceIncIdFunct', 
                          'vars': [
                                 'mInvoice'], 
                          'return': [
                                   'eInvoiceIncId']}, 
   'addEInvoiceFunct': {'parent': 'self', 
                        'name': 'addERPInvoiceFunct', 
                        'vars': [
                               'invoice', 'shipment'], 
                        'return': [
                                 'eInvoiceIncId']}, 
   'eShipsFunct': {'parent': 'self', 
                   'name': 'erpShipsFunct', 
                   'vars': [], 'return': [
                            'eShips']}, 
   'mShipFunct': {'parent': 'self', 
                  'name': 'mageShipFunct', 
                  'vars': [
                         'eShip'], 
                  'return': [
                           'shipment', 'shipItemCount']}, 
   'mShipExtFunct': {'parent': 'self', 
                     'name': 'mageShipExtFunct', 
                     'vars': [
                            'shipment', 'eShip'], 
                     'return': []}, 
   'mShipItemFunct': {'parent': 'self', 
                      'name': 'mageShipItemFunct', 
                      'vars': [
                             'i', 'shipment', 'eShip'], 
                      'return': []}, 
   'mShipItemExtFunct': {'parent': 'self', 
                         'name': 'mageShipItemExtFunct', 
                         'vars': [
                                'i', 'shipment', 'eShip'], 
                         'return': []}, 
   'eProductsFunct': {'parent': 'self', 
                      'name': 'erpProductsFunct', 
                      'vars': [
                             'task'], 
                      'return': [
                               'eProducts']}, 
   'mProductFunct': {'parent': 'self', 
                     'name': 'mageProductFunct', 
                     'vars': [
                            'eProduct'], 
                     'return': [
                              'product']}, 
   'mProductExtFunct': {'parent': 'self', 
                        'name': 'mageProductExtFunct', 
                        'vars': [
                               'product', 'eProduct'], 
                        'return': []}, 
   'addUpdateMProductFunct': {'parent': 'self', 
                              'name': 'addUpdateEMProductFunct', 
                              'vars': [
                                     'product'], 
                              'return': [
                                       'mProductId']}, 
   'eOrderIncIdFunct': {'parent': 'self', 
                        'name': 'erpOrderIncIdFunct', 
                        'vars': [
                               'mOrder'], 
                        'return': [
                                 'eOrderIncId']}, 
   'eProductsInventoryFunct': {'parent': 'self', 
                               'name': 'erpProductsInventoryFunct', 
                               'vars': [
                                      'task'], 
                               'return': [
                                        'eProductsInventory']}, 
   'mProductInventoryFunct': {'parent': 'self', 
                              'name': 'mageProductInventoryFunct', 
                              'vars': [
                                     'eProductInventory'], 
                              'return': [
                                       'productInventory']}, 
   'mProductInventoryExtFunct': {'parent': 'self', 
                                 'name': 'mageProductInventoryExtFunct', 
                                 'vars': [
                                        'productInventory', 'eProductInventory'], 
                                 'return': []}, 
   'addUpdateMProductInventoryFunct': {'parent': 'self', 
                                       'name': 'addUpdateEMProductInventoryFunct', 
                                       'vars': [
                                              'productInventory'], 
                                       'return': [
                                                'mProductInventoryId']}, 
   'eProductsPriceFunct': {'parent': 'self', 
                           'name': 'erpProductsPriceFunct', 
                           'vars': [
                                  'task'], 
                           'return': [
                                    'eProductsPrice']}, 
   'mProductPriceFunct': {'parent': 'self', 
                          'name': 'mageProductPriceFunct', 
                          'vars': [
                                 'eProductPrice'], 
                          'return': [
                                   'productPrice']}, 
   'mProductPriceExtFunct': {'parent': 'self', 
                             'name': 'mageProductPriceExtFunct', 
                             'vars': [
                                    'productPrice', 'eProductPrice'], 
                             'return': []}, 
   'addUpdateMProductPriceFunct': {'parent': 'self', 
                                   'name': 'addUpdateEMProductPriceFunct', 
                                   'vars': [
                                          'productPrice'], 
                                   'return': [
                                            'mProductPriceId']}, 
   'eProductsTierPriceFunct': {'parent': 'self', 
                               'name': 'erpProductsTierPriceFunct', 
                               'vars': [
                                      'task'], 
                               'return': [
                                        'eProductsTierPrice']}, 
   'mProductTierPriceFunct': {'parent': 'self', 
                              'name': 'mageProductTierPriceFunct', 
                              'vars': [
                                     'eProductTierPrice'], 
                              'return': [
                                       'productTierPrice']}, 
   'mProductTierPriceExtFunct': {'parent': 'self', 
                                 'name': 'mageProductTierPriceExtFunct', 
                                 'vars': [
                                        'productTierPrice', 'eProductTierPrice'], 
                                 'return': []}, 
   'addUpdateMProductTierPriceFunct': {'parent': 'self', 
                                       'name': 'addUpdateEMProductTierPriceFunct', 
                                       'vars': [
                                              'productTierPrice'], 
                                       'return': [
                                                'mProductTierPriceId']}, 
   'eProductsGroupPriceFunct': {'parent': 'self', 
                                'name': 'erpProductsGroupPriceFunct', 
                                'vars': [
                                       'task'], 
                                'return': [
                                         'eProductsGroupPrice']}, 
   'mProductGroupPriceFunct': {'parent': 'self', 
                               'name': 'mageProductGroupPriceFunct', 
                               'vars': [
                                      'eProductGroupPrice'], 
                               'return': [
                                        'productGroupPrice']}, 
   'mProductGroupPriceExtFunct': {'parent': 'self', 
                                  'name': 'mageProductGroupPriceExtFunct', 
                                  'vars': [
                                         'productGroupPrice', 'eProductGroupPrice'], 
                                  'return': []}, 
   'addUpdateMProductGroupPriceFunct': {'parent': 'self', 
                                        'name': 'addUpdateEMProductGroupPriceFunct', 
                                        'vars': [
                                               'productGroupPrice'], 
                                        'return': [
                                                 'mProductGroupPriceId']}, 
   'eCustomersFunct': {'parent': 'self', 
                       'name': 'erpCustomersFunct', 
                       'vars': [], 'return': [
                                'eCustomers']}, 
   'mCustomerFunct': {'parent': 'self', 
                      'name': 'mageCustomerFunct', 
                      'vars': [
                             'eCustomer'], 
                      'return': [
                               'customer', 'customerAddressCount']}, 
   'mCustomerExtFunct': {'parent': 'self', 
                         'name': 'mageCustomerExtFunct', 
                         'vars': [
                                'customer', 'eCustomer'], 
                         'return': []}, 
   'mCustomerAddressFunct': {'parent': 'self', 
                             'name': 'mageCustomerAddressFunct', 
                             'vars': [
                                    'i', 'customer', 'eCustomer'], 
                             'return': []}, 
   'mCustomerAddressExtFunct': {'parent': 'self', 
                                'name': 'mageCustomerAddressExtFunct', 
                                'vars': [
                                       'i', 'customer', 'eCustomer'], 
                                'return': []}, 
   'eConfigProductsFunct': {'parent': 'self', 
                            'name': 'erpConfigProductsFunct', 
                            'vars': [
                                   'task'], 
                            'return': [
                                     'eConfigProducts']}, 
   'mConfigProductFunct': {'parent': 'self', 
                           'name': 'mageConfigProductFunct', 
                           'vars': [
                                  'eConfigProduct'], 
                           'return': [
                                    'configProduct']}, 
   'mConfigProductExtFunct': {'parent': 'self', 
                              'name': 'mageConfigProductExtFunct', 
                              'vars': [
                                     'configProduct', 'eConfigProduct'], 
                              'return': []}, 
   'addUpdateMConfigProductFunct': {'parent': 'self', 
                                    'name': 'addUpdateEMConfigProductFunct', 
                                    'vars': [
                                           'configProduct'], 
                                    'return': [
                                             'mConfigProductId']}, 
   'eProductsCompanyPriceFunct': {'parent': 'self', 
                                  'name': 'erpProductsCompanyPriceFunct', 
                                  'vars': [
                                         'task'], 
                                  'return': [
                                           'eProductsCompanyPrice']}, 
   'mProductCompanyPriceFunct': {'parent': 'self', 
                                 'name': 'mageProductCompanyPriceFunct', 
                                 'vars': [
                                        'eProductCompanyPrice'], 
                                 'return': [
                                          'productCompanyPrice']}, 
   'mProductCompanyPriceExtFunct': {'parent': 'self', 
                                    'name': 'mageProductCompanyPriceExtFunct', 
                                    'vars': [
                                           'productCompanyPrice', 'eProductCompanyPrice'], 
                                    'return': []}, 
   'addUpdateMProductCompanyPriceFunct': {'parent': 'self', 
                                          'name': 'addUpdateEMProductCompanyPriceFunct', 
                                          'vars': [
                                                 'productCompanyPrice'], 
                                          'return': [
                                                   'mProductCompanyPriceId']}, 
   'eProductsCategoryFunct': {'parent': 'self', 
                              'name': 'erpProductsCategoryFunct', 
                              'vars': [
                                     'task'], 
                              'return': [
                                       'eProductsCategory']}, 
   'mProductCategoryFunct': {'parent': 'self', 
                             'name': 'mageProductCategoryFunct', 
                             'vars': [
                                    'eProductCategory'], 
                             'return': [
                                      'productCategory']}, 
   'mProductCategoryExtFunct': {'parent': 'self', 
                                'name': 'mageProductCategoryExtFunct', 
                                'vars': [
                                       'productCategory', 'eProductCategory'], 
                                'return': []}, 
   'addUpdateMProductCategoryFunct': {'parent': 'self', 
                                      'name': 'addUpdateEMProductCategoryFunct', 
                                      'vars': [
                                             'productCategory'], 
                                      'return': [
                                               'mProductCategoryId']}, 
   'eCompanysFunct': {'parent': 'self', 
                      'name': 'erpCompanysFunct', 
                      'vars': [
                             'task'], 
                      'return': [
                               'eCompanys']}, 
   'mCompanyFunct': {'parent': 'self', 
                     'name': 'mageCompanyFunct', 
                     'vars': [
                            'eCompany'], 
                     'return': [
                              'company', 'companyAddressCount', 'companyContactCount']}, 
   'mCompanyExtFunct': {'parent': 'self', 
                        'name': 'mageCompanyExtFunct', 
                        'vars': [
                               'company', 'eCompany'], 
                        'return': []}, 
   'mCompanyAddressFunct': {'parent': 'self', 
                            'name': 'mageCompanyAddressFunct', 
                            'vars': [
                                   'i', 'company', 'eCompany'], 
                            'return': []}, 
   'mCompanyAddressExtFunct': {'parent': 'self', 
                               'name': 'mageCompanyAddressExtFunct', 
                               'vars': [
                                      'i', 'company', 'eCompany'], 
                               'return': []}, 
   'mCompanyContactFunct': {'parent': 'self', 
                            'name': 'mageCompanyContactFunct', 
                            'vars': [
                                   'i', 'company', 'eCompany'], 
                            'return': []}, 
   'mCompanyContactExtFunct': {'parent': 'self', 
                               'name': 'mageCompanyContactExtFunct', 
                               'vars': [
                                      'i', 'company', 'eCompany'], 
                               'return': []}}
# okay decompiling DefaultFunctions.pyc
