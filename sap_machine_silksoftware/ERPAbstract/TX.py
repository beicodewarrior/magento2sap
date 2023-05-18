# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr 17 2020, 18:29:03) 
# [GCC 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.29.20) (-macos10.15-objc-
# Embedded file name: ..\ERPAbstract\TX.py
# Compiled at: 2016-07-26 09:39:58
__author__ = 'bibow'
from DefaultFunctions import DEFAULTFUNCTIONS
from DefaultQueries import DEFAULTQUERIES

class Functs(object):

    def __init__(self, functs):
        functs = dict(DEFAULTFUNCTIONS, **functs)
        self._eOrderFunct = self.buildFunct(functs['eOrderFunct'])
        self._eOrderExtFunct = self.buildFunct(functs['eOrderExtFunct'])
        self._eOrderLineFunct = self.buildFunct(functs['eOrderLineFunct'])
        self._eOrderLineExtFunct = self.buildFunct(functs['eOrderLineExtFunct'])
        self._addEOrderFunct = self.buildFunct(functs['addEOrderFunct'])
        self._cancelEOrderFunct = self.buildFunct(functs['cancelEOrderFunct'])
        self._eOrderRFunct = self.buildFunct(functs['eOrderRFunct'])
        self._eDownPaymentFunct = self.buildFunct(functs['eDownPaymentFunct'])
        self._eDownPaymentLineFunct = self.buildFunct(functs['eDownPaymentLineFunct'])
        self._eDownPaymentExtFunct = self.buildFunct(functs['eDownPaymentExtFunct'])
        self._eDownPaymentLineExtFunct = self.buildFunct(functs['eDownPaymentLineExtFunct'])
        self._eDownPaymentIncIdFunct = self.buildFunct(functs['eDownPaymentIncIdFunct'])
        self._addEDownPaymentFunct = self.buildFunct(functs['addEDownPaymentFunct'])
        self._eCustFunct = self.buildFunct(functs['eCustFunct'])
        self._eCustExtFunct = self.buildFunct(functs['eCustExtFunct'])
        self._eCustAddrFunct = self.buildFunct(functs['eCustAddrFunct'])
        self._eCustAddrExtFunct = self.buildFunct(functs['eCustAddrExtFunct'])
        self._eCustContFunct = self.buildFunct(functs['eCustContFunct'])
        self._eCustContExtFunct = self.buildFunct(functs['eCustContExtFunct'])
        self._addUpdateECustFunct = self.buildFunct(functs['addUpdateECustFunct'])
        self._eShipRFunct = self.buildFunct(functs['eShipRFunct'])
        self._eInvoiceFunct = self.buildFunct(functs['eInvoiceFunct'])
        self._eInvoiceLineFunct = self.buildFunct(functs['eInvoiceLineFunct'])
        self._eInvoiceExtFunct = self.buildFunct(functs['eInvoiceExtFunct'])
        self._eInvoiceLineExtFunct = self.buildFunct(functs['eInvoiceLineExtFunct'])
        self._eInvoiceIncIdFunct = self.buildFunct(functs['eInvoiceIncIdFunct'])
        self._addEInvoiceFunct = self.buildFunct(functs['addEInvoiceFunct'])
        self._eShipsFunct = self.buildFunct(functs['eShipsFunct'])
        self._mShipFunct = self.buildFunct(functs['mShipFunct'])
        self._mShipExtFunct = self.buildFunct(functs['mShipExtFunct'])
        self._mShipItemFunct = self.buildFunct(functs['mShipItemFunct'])
        self._mShipItemExtFunct = self.buildFunct(functs['mShipItemExtFunct'])
        self._eProductsFunct = self.buildFunct(functs['eProductsFunct'])
        self._mProductFunct = self.buildFunct(functs['mProductFunct'])
        self._mProductExtFunct = self.buildFunct(functs['mProductExtFunct'])
        self._addUpdateMProductFunct = self.buildFunct(functs['addUpdateMProductFunct'])
        self._eOrderIncIdFunct = self.buildFunct(functs['eOrderIncIdFunct'])
        self._eProductsInventoryFunct = self.buildFunct(functs['eProductsInventoryFunct'])
        self._mProductInventoryFunct = self.buildFunct(functs['mProductInventoryFunct'])
        self._mProductInventoryExtFunct = self.buildFunct(functs['mProductInventoryExtFunct'])
        self._addUpdateMProductInventoryFunct = self.buildFunct(functs['addUpdateMProductInventoryFunct'])
        self._eProductsPriceFunct = self.buildFunct(functs['eProductsPriceFunct'])
        self._mProductPriceFunct = self.buildFunct(functs['mProductPriceFunct'])
        self._mProductPriceExtFunct = self.buildFunct(functs['mProductPriceExtFunct'])
        self._addUpdateMProductPriceFunct = self.buildFunct(functs['addUpdateMProductPriceFunct'])
        self._eProductsTierPriceFunct = self.buildFunct(functs['eProductsTierPriceFunct'])
        self._mProductTierPriceFunct = self.buildFunct(functs['mProductTierPriceFunct'])
        self._mProductTierPriceExtFunct = self.buildFunct(functs['mProductTierPriceExtFunct'])
        self._addUpdateMProductTierPriceFunct = self.buildFunct(functs['addUpdateMProductTierPriceFunct'])
        self._eProductsGroupPriceFunct = self.buildFunct(functs['eProductsGroupPriceFunct'])
        self._mProductGroupPriceFunct = self.buildFunct(functs['mProductGroupPriceFunct'])
        self._mProductGroupPriceExtFunct = self.buildFunct(functs['mProductGroupPriceExtFunct'])
        self._addUpdateMProductGroupPriceFunct = self.buildFunct(functs['addUpdateMProductGroupPriceFunct'])
        self._eCustomersFunct = self.buildFunct(functs['eCustomersFunct'])
        self._mCustomerFunct = self.buildFunct(functs['mCustomerFunct'])
        self._mCustomerExtFunct = self.buildFunct(functs['mCustomerExtFunct'])
        self._mCustomerAddressFunct = self.buildFunct(functs['mCustomerAddressFunct'])
        self._mCustomerAddressExtFunct = self.buildFunct(functs['mCustomerAddressExtFunct'])
        self._eConfigProductsFunct = self.buildFunct(functs['eConfigProductsFunct'])
        self._mConfigProductFunct = self.buildFunct(functs['mConfigProductFunct'])
        self._mConfigProductExtFunct = self.buildFunct(functs['mConfigProductExtFunct'])
        self._addUpdateMConfigProductFunct = self.buildFunct(functs['addUpdateMConfigProductFunct'])
        self._eProductsCompanyPriceFunct = self.buildFunct(functs['eProductsCompanyPriceFunct'])
        self._mProductCompanyPriceFunct = self.buildFunct(functs['mProductCompanyPriceFunct'])
        self._mProductCompanyPriceExtFunct = self.buildFunct(functs['mProductCompanyPriceExtFunct'])
        self._addUpdateMProductCompanyPriceFunct = self.buildFunct(functs['addUpdateMProductCompanyPriceFunct'])
        self._eProductsCategoryFunct = self.buildFunct(functs['eProductsCategoryFunct'])
        self._mProductCategoryFunct = self.buildFunct(functs['mProductCategoryFunct'])
        self._mProductCategoryExtFunct = self.buildFunct(functs['mProductCategoryExtFunct'])
        self._addUpdateMProductCategoryFunct = self.buildFunct(functs['addUpdateMProductCategoryFunct'])
        self._eCompanysFunct = self.buildFunct(functs['eCompanysFunct'])
        self._mCompanyFunct = self.buildFunct(functs['mCompanyFunct'])
        self._mCompanyExtFunct = self.buildFunct(functs['mCompanyExtFunct'])
        self._mCompanyAddressFunct = self.buildFunct(functs['mCompanyAddressFunct'])
        self._mCompanyAddressExtFunct = self.buildFunct(functs['mCompanyAddressExtFunct'])
        self._mCompanyContactFunct = self.buildFunct(functs['mCompanyContactFunct'])
        self._mCompanyContactExtFunct = self.buildFunct(functs['mCompanyContactExtFunct'])

    def buildFunct(self, funct):
        return funct['parent'] + '.' + funct['name'] + '(' + (',').join(funct['vars']) + ')'

    @property
    def eOrderFunct(self):
        return self._eOrderFunct

    @eOrderFunct.setter
    def eOrderFunct(self, value):
        self._eOrderFunct = self.buildFunct(value)

    @property
    def eOrderExtFunct(self):
        return self._eOrderExtFunct

    @eOrderExtFunct.setter
    def eOrderExtFunct(self, value):
        self._eOrderExtFunct = self.buildFunct(value)

    @property
    def eOrderLineFunct(self):
        return self._eOrderLineFunct

    @eOrderLineFunct.setter
    def eOrderLineFunct(self, value):
        self._eOrderLineFunct = self.buildFunct(value)

    @property
    def eOrderLineExtFunct(self):
        return self._eOrderLineExtFunct

    @eOrderLineExtFunct.setter
    def eOrderLineExtFunct(self, value):
        self._eOrderLineExtFunct = self.buildFunct(value)

    @property
    def addEOrderFunct(self):
        return self._addEOrderFunct

    @addEOrderFunct.setter
    def addEOrderFunct(self, value):
        self._addEOrderFunct = self.buildFunct(value)

    @property
    def cancelEOrderFunct(self):
        return self._cancelEOrderFunct

    @cancelEOrderFunct.setter
    def cancelEOrderFunct(self, value):
        self._cancelEOrderFunct = self.buildFunct(value)

    @property
    def eOrderRFunct(self):
        return self._eOrderRFunct

    @eOrderRFunct.setter
    def eOrderRFunct(self, value):
        self._eOrderRFunct = self.buildFunct(value)

    @property
    def eDownPaymentFunct(self):
        return self._eDownPaymentFunct

    @eDownPaymentFunct.setter
    def eDownPaymentFunct(self, value):
        self._eDownPaymentFunct = self.buildFunct(value)

    @property
    def eDownPaymentExtFunct(self):
        return self._eDownPaymentExtFunct

    @eDownPaymentExtFunct.setter
    def eDownPaymentExtFunct(self, value):
        self._eDownPaymentExtFunct = self.buildFunct(value)

    @property
    def eDownPaymentLineFunct(self):
        return self._eDownPaymentLineFunct

    @eDownPaymentLineFunct.setter
    def eDownPaymentLineFunct(self, value):
        self._eDownPaymentLineFunct = self.buildFunct(value)

    @property
    def eDownPaymentLineExtFunct(self):
        return self._eDownPaymentLineExtFunct

    @eDownPaymentLineExtFunct.setter
    def eDownPaymentLineExtFunct(self, value):
        self._eDownPaymentLineExtFunct = self.buildFunct(value)

    @property
    def eDownPaymentIncIdFunct(self):
        return self._eDownPaymentIncIdFunct

    @eDownPaymentIncIdFunct.setter
    def eDownPaymentIncIdFunct(self, value):
        self._eDownPaymentIncIdFunct = self.buildFunct(value)

    @property
    def addEDownPaymentFunct(self):
        return self._addEDownPaymentFunct

    @addEDownPaymentFunct.setter
    def addEDownPaymentFunct(self, value):
        self._addEDownPaymentFunct = self.buildFunct(value)

    @property
    def eCustFunct(self):
        return self._eCustFunct

    @eCustFunct.setter
    def eCustFunct(self, value):
        self._eCustFunct = self.buildFunct(value)

    @property
    def eCustExtFunct(self):
        return self._eCustExtFunct

    @eCustExtFunct.setter
    def eCustExtFunct(self, value):
        self._eCustExtFunct = self.buildFunct(value)

    @property
    def eCustAddrFunct(self):
        return self._eCustAddrFunct

    @eCustAddrFunct.setter
    def eCustAddrFunct(self, value):
        self._eCustAddrFunct = self.buildFunct(value)

    @property
    def eCustAddrExtFunct(self):
        return self._eCustAddrExtFunct

    @eCustAddrExtFunct.setter
    def eCustAddrExtFunct(self, value):
        self._eCustAddrExtFunct = self.buildFunct(value)

    @property
    def eCustContFunct(self):
        return self._eCustContFunct

    @eCustContFunct.setter
    def eCustContFunct(self, value):
        self._eCustContFunct = self.buildFunct(value)

    @property
    def eCustContExtFunct(self):
        return self._eCustContExtFunct

    @eCustContExtFunct.setter
    def eCustContExtFunct(self, value):
        self._eCustContExtFunct = self.buildFunct(value)

    @property
    def addUpdateECustFunct(self):
        return self._addUpdateECustFunct

    @addUpdateECustFunct.setter
    def addUpdateECustFunct(self, value):
        self._addUpdateECustFunct = self.buildFunct(value)

    @property
    def eShipRFunct(self):
        return self._eShipRFunct

    @eShipRFunct.setter
    def eShipRFunct(self, value):
        self._eShipRFunct = self.buildFunct(value)

    @property
    def eInvoiceFunct(self):
        return self._eInvoiceFunct

    @eInvoiceFunct.setter
    def eInvoiceFunct(self, value):
        self._eInvoiceFunct = self.buildFunct(value)

    @property
    def eInvoiceExtFunct(self):
        return self._eInvoiceExtFunct

    @eInvoiceExtFunct.setter
    def eInvoiceExtFunct(self, value):
        self._eInvoiceExtFunct = self.buildFunct(value)

    @property
    def eInvoiceLineFunct(self):
        return self._eInvoiceLineFunct

    @eInvoiceLineFunct.setter
    def eInvoiceLineFunct(self, value):
        self._eInvoiceLineFunct = self.buildFunct(value)

    @property
    def eInvoiceLineExtFunct(self):
        return self._eInvoiceLineExtFunct

    @eInvoiceLineExtFunct.setter
    def eInvoiceLineExtFunct(self, value):
        self._eInvoiceLineExtFunct = self.buildFunct(value)

    @property
    def eInvoiceIncIdFunct(self):
        return self._eInvoiceIncIdFunct

    @eInvoiceIncIdFunct.setter
    def eInvoiceIncIdFunct(self, value):
        self._eInvoiceIncIdFunct = self.buildFunct(value)

    @property
    def addEInvoiceFunct(self):
        return self._addEInvoiceFunct

    @addEInvoiceFunct.setter
    def addEInvoiceFunct(self, value):
        self._addEInvoiceFunct = self.buildFunct(value)

    @property
    def eShipsFunct(self):
        return self._eShipsFunct

    @eShipsFunct.setter
    def eShipsFunct(self, value):
        self._eShipsFunct = self.buildFunct(value)

    @property
    def mShipFunct(self):
        return self._mShipFunct

    @mShipFunct.setter
    def mShipFunct(self, value):
        self._mShipFunct = self.buildFunct(value)

    @property
    def mShipExtFunct(self):
        return self._mShipExtFunct

    @mShipExtFunct.setter
    def mShipExtFunct(self, value):
        self._mShipExtFunct = self.buildFunct(value)

    @property
    def mShipItemFunct(self):
        return self._mShipItemFunct

    @mShipItemFunct.setter
    def mShipItemFunct(self, value):
        self._mShipItemFunct = self.buildFunct(value)

    @property
    def mShipItemExtFunct(self):
        return self._mShipItemExtFunct

    @mShipItemExtFunct.setter
    def mShipItemExtFunct(self, value):
        self._mShipItemExtFunct = self.buildFunct(value)

    @property
    def eProductsFunct(self):
        return self._eProductsFunct

    @eProductsFunct.setter
    def eProductsFunct(self, value):
        self._eProductsFunct = self.buildFunct(value)

    @property
    def mProductFunct(self):
        return self._mProductFunct

    @mProductFunct.setter
    def mProductFunct(self, value):
        self._mProductFunct = self.buildFunct(value)

    @property
    def mProductExtFunct(self):
        return self._mProductExtFunct

    @mProductExtFunct.setter
    def mProductExtFunct(self, value):
        self._mProductExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductFunct(self):
        return self._addUpdateMProductFunct

    @addUpdateMProductFunct.setter
    def addUpdateMProductFunct(self, value):
        self._addUpdateMProductFunct = self.buildFunct(value)

    @property
    def eOrderIncIdFunct(self):
        return self._eOrderIncIdFunct

    @eOrderIncIdFunct.setter
    def eOrderIncIdFunct(self, value):
        self._eOrderIncIdFunct = self.buildFunct(value)

    @property
    def eProductsInventoryFunct(self):
        return self._eProductsInventoryFunct

    @eProductsInventoryFunct.setter
    def eProductsInventoryFunct(self, value):
        self._eProductsInventoryFunct = self.buildFunct(value)

    @property
    def mProductInventoryFunct(self):
        return self._mProductInventoryFunct

    @mProductInventoryFunct.setter
    def mProductInventoryFunct(self, value):
        self._mProductInventoryFunct = self.buildFunct(value)

    @property
    def mProductInventoryExtFunct(self):
        return self._mProductInventoryExtFunct

    @mProductInventoryExtFunct.setter
    def mProductInventoryExtFunct(self, value):
        self._mProductInventoryExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductInventoryFunct(self):
        return self._addUpdateMProductInventoryFunct

    @addUpdateMProductInventoryFunct.setter
    def addUpdateMProductInventoryFunct(self, value):
        self._addUpdateMProductInventoryFunct = self.buildFunct(value)

    @property
    def eProductsPriceFunct(self):
        return self._eProductsPriceFunct

    @eProductsPriceFunct.setter
    def eProductsPriceFunct(self, value):
        self._eProductsPriceFunct = self.buildFunct(value)

    @property
    def mProductPriceFunct(self):
        return self._mProductPriceFunct

    @mProductPriceFunct.setter
    def mProductPriceFunct(self, value):
        self._mProductPriceFunct = self.buildFunct(value)

    @property
    def mProductPriceExtFunct(self):
        return self._mProductPriceExtFunct

    @mProductPriceExtFunct.setter
    def mProductPriceExtFunct(self, value):
        self._mProductPriceExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductPriceFunct(self):
        return self._addUpdateMProductPriceFunct

    @addUpdateMProductPriceFunct.setter
    def addUpdateMProductPriceFunct(self, value):
        self._addUpdateMProductPriceFunct = self.buildFunct(value)

    @property
    def eProductsTierPriceFunct(self):
        return self._eProductsTierPriceFunct

    @eProductsTierPriceFunct.setter
    def eProductsTierPriceFunct(self, value):
        self._eProductsTierPriceFunct = self.buildFunct(value)

    @property
    def mProductTierPriceFunct(self):
        return self._mProductTierPriceFunct

    @mProductTierPriceFunct.setter
    def mProductTierPriceFunct(self, value):
        self._mProductTierPriceFunct = self.buildFunct(value)

    @property
    def mProductTierPriceExtFunct(self):
        return self._mProductTierPriceExtFunct

    @mProductTierPriceExtFunct.setter
    def mProductTierPriceExtFunct(self, value):
        self._mProductTierPriceExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductTierPriceFunct(self):
        return self._addUpdateMProductTierPriceFunct

    @addUpdateMProductTierPriceFunct.setter
    def addUpdateMProductTierPriceFunct(self, value):
        self._addUpdateMProductTierPriceFunct = self.buildFunct(value)

    @property
    def eProductsGroupPriceFunct(self):
        return self._eProductsGroupPriceFunct

    @eProductsGroupPriceFunct.setter
    def eProductsGroupPriceFunct(self, value):
        self._eProductsGroupPriceFunct = self.buildFunct(value)

    @property
    def mProductGroupPriceFunct(self):
        return self._mProductGroupPriceFunct

    @mProductGroupPriceFunct.setter
    def mProductGroupPriceFunct(self, value):
        self._mProductGroupPriceFunct = self.buildFunct(value)

    @property
    def mProductGroupPriceExtFunct(self):
        return self._mProductGroupPriceExtFunct

    @mProductGroupPriceExtFunct.setter
    def mProductGroupPriceExtFunct(self, value):
        self._mProductGroupPriceExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductGroupPriceFunct(self):
        return self._addUpdateMProductGroupPriceFunct

    @addUpdateMProductGroupPriceFunct.setter
    def addUpdateMProductGroupPriceFunct(self, value):
        self._addUpdateMProductGroupPriceFunct = self.buildFunct(value)

    @property
    def eCustomersFunct(self):
        return self._eCustomersFunct

    @eCustomersFunct.setter
    def eCustomersFunct(self, value):
        self._eCustomersFunct = self.buildFunct(value)

    @property
    def mCustomerFunct(self):
        return self._mCustomerFunct

    @mCustomerFunct.setter
    def mCustomerFunct(self, value):
        self._mCustomerFunct = self.buildFunct(value)

    @property
    def mCustomerExtFunct(self):
        return self._mCustomerExtFunct

    @mCustomerExtFunct.setter
    def mCustomerExtFunct(self, value):
        self._mCustomerExtFunct = self.buildFunct(value)

    @property
    def mCustomerAddressFunct(self):
        return self._mCustomerAddressFunct

    @mCustomerAddressFunct.setter
    def mCustomerAddressFunct(self, value):
        self._mCustomerAddressFunct = self.buildFunct(value)

    @property
    def mCustomerAddressExtFunct(self):
        return self._mCustomerAddressExtFunct

    @mCustomerAddressExtFunct.setter
    def mCustomerAddressExtFunct(self, value):
        self._mCustomerAddressExtFunct = self.buildFunct(value)

    @property
    def eConfigProductsFunct(self):
        return self._eConfigProductsFunct

    @eConfigProductsFunct.setter
    def eConfigProductsFunct(self, value):
        self._eConfigProductsFunct = self.buildFunct(value)

    @property
    def mConfigProductFunct(self):
        return self._mConfigProductFunct

    @mConfigProductFunct.setter
    def mConfigProductFunct(self, value):
        self._mConfigProductFunct = self.buildFunct(value)

    @property
    def mConfigProductExtFunct(self):
        return self._mConfigProductExtFunct

    @mConfigProductExtFunct.setter
    def mConfigProductExtFunct(self, value):
        self._mConfigProductExtFunct = self.buildFunct(value)

    @property
    def addUpdateMConfigProductFunct(self):
        return self._addUpdateMConfigProductFunct

    @addUpdateMConfigProductFunct.setter
    def addUpdateMConfigProductFunct(self, value):
        self._addUpdateMConfigProductFunct = self.buildFunct(value)

    @property
    def eProductsCompanyPriceFunct(self):
        return self._eProductsCompanyPriceFunct

    @eProductsCompanyPriceFunct.setter
    def eProductsCompanyPriceFunct(self, value):
        self._eProductsCompanyPriceFunct = self.buildFunct(value)

    @property
    def mProductCompanyPriceFunct(self):
        return self._mProductCompanyPriceFunct

    @mProductCompanyPriceFunct.setter
    def mProductCompanyPriceFunct(self, value):
        self._mProductCompanyPriceFunct = self.buildFunct(value)

    @property
    def mProductCompanyPriceExtFunct(self):
        return self._mProductCompanyPriceExtFunct

    @mProductCompanyPriceExtFunct.setter
    def mProductCompanyPriceExtFunct(self, value):
        self._mProductCompanyPriceExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductCompanyPriceFunct(self):
        return self._addUpdateMProductCompanyPriceFunct

    @addUpdateMProductCompanyPriceFunct.setter
    def addUpdateMProductCompanyPriceFunct(self, value):
        self._addUpdateMProductCompanyPriceFunct = self.buildFunct(value)

    @property
    def eProductsCategoryFunct(self):
        return self._eProductsCategoryFunct

    @eProductsCategoryFunct.setter
    def eProductsCategoryFunct(self, value):
        self._eProductsCategoryFunct = self.buildFunct(value)

    @property
    def mProductCategoryFunct(self):
        return self._mProductCategoryFunct

    @mProductCategoryFunct.setter
    def mProductCategoryFunct(self, value):
        self._mProductCategoryFunct = self.buildFunct(value)

    @property
    def mProductCategoryExtFunct(self):
        return self._mProductCategoryExtFunct

    @mProductCategoryExtFunct.setter
    def mProductCategoryExtFunct(self, value):
        self._mProductCategoryExtFunct = self.buildFunct(value)

    @property
    def addUpdateMProductCategoryFunct(self):
        return self._addUpdateMProductCategoryFunct

    @addUpdateMProductCategoryFunct.setter
    def addUpdateMProductCategoryFunct(self, value):
        self._addUpdateMProductCategoryFunct = self.buildFunct(value)

    @property
    def eCompanysFunct(self):
        return self._eCompanysFunct

    @eCompanysFunct.setter
    def eCompanysFunct(self, value):
        self._eCompanysFunct = self.buildFunct(value)

    @property
    def mCompanyFunct(self):
        return self._mCompanyFunct

    @mCompanyFunct.setter
    def mCompanyFunct(self, value):
        self._mCompanyFunct = self.buildFunct(value)

    @property
    def mCompanyExtFunct(self):
        return self._mCompanyExtFunct

    @mCompanyExtFunct.setter
    def mCompanyExtFunct(self, value):
        self._mCompanyExtFunct = self.buildFunct(value)

    @property
    def mCompanyAddressFunct(self):
        return self._mCompanyAddressFunct

    @mCompanyAddressFunct.setter
    def mCompanyAddressFunct(self, value):
        self._mCompanyAddressFunct = self.buildFunct(value)

    @property
    def mCompanyAddressExtFunct(self):
        return self._mCompanyAddressExtFunct

    @mCompanyAddressExtFunct.setter
    def mCompanyAddressExtFunct(self, value):
        self._mCompanyAddressExtFunct = self.buildFunct(value)

    @mCompanyExtFunct.setter
    def mCompanyExtFunct(self, value):
        self._mCompanyExtFunct = self.buildFunct(value)

    @property
    def mCompanyContactFunct(self):
        return self._mCompanyContactFunct

    @mCompanyContactFunct.setter
    def mCompanyContactFunct(self, value):
        self._mCompanyContactFunct = self.buildFunct(value)

    @property
    def mCompanyContactExtFunct(self):
        return self._mCompanyContactExtFunct

    @mCompanyContactExtFunct.setter
    def mCompanyContactExtFunct(self, value):
        self._mCompanyContactExtFunct = self.buildFunct(value)


class Queries(object):

    def __init__(self, queries):
        queries = dict(DEFAULTQUERIES, **queries)
        self._listMOrdersSQL = queries['listMOrdersSQL']
        self._listMOrderItemsSQL = queries['listMOrderItemsSQL']
        self._listMCancelOrdersSQL = queries['listMCancelOrdersSQL']
        self._listMDownPaymentsSQL = queries['listMDownPaymentsSQL']
        self._listMCustsSQL = queries['listMCustsSQL']
        self._listMCustAddrsSQL = queries['listMCustAddrsSQL']
        self._listMInvoicesSQL = queries['listMInvoicesSQL']
        self._insertOrUpdateEProductSQL = queries['insertOrUpdateEProductSQL']
        self._listNeedShipOrdersSQL = queries['listNeedShipOrdersSQL']
        self._listOrderExistingShipmentSQL = queries['listOrderExistingShipmentSQL']
        self._addOrUpdateEProductMasterSQL = queries['addOrUpdateEProductMasterSQL']
        self._addOrUpdateEProductInventorySQL = queries['addOrUpdateEProductInventorySQL']
        self._addOrUpdateEProductPriceSQL = queries['addOrUpdateEProductPriceSQL']
        self._addOrUpdateEProductGroupPriceSQL = queries['addOrUpdateEProductGroupPriceSQL']
        self._addOrUpdateEProductTierPriceSQL = queries['addOrUpdateEProductTierPriceSQL']
        self._addOrUpdateECustomerSQL = queries['addOrUpdateECustomerSQL']
        self._addOrUpdateEConfigProductSQL = queries['addOrUpdateEConfigProductSQL']
        self._addOrUpdateEProductCompanyPriceSQL = queries['addOrUpdateEProductCompanyPriceSQL']
        self._addOrUpdateEProductCategorySQL = queries['addOrUpdateEProductCategorySQL']

    @property
    def listMOrdersSQL(self):
        return self._listMOrdersSQL

    @listMOrdersSQL.setter
    def listMOrdersSQL(self, value):
        self._listMOrdersSQL = value

    @property
    def listMOrderItemsSQL(self):
        return self._listMOrderItemsSQL

    @listMOrderItemsSQL.setter
    def listMOrderItemsSQL(self, value):
        self._listMOrderItemsSQL = value

    @property
    def listMCancelOrdersSQL(self):
        return self._listMCancelOrdersSQL

    @listMCancelOrdersSQL.setter
    def listMCancelOrdersSQL(self, value):
        self._listMCancelOrdersSQL = value

    @property
    def listMDownPaymentsSQL(self):
        return self._listMDownPaymentsSQL

    @listMDownPaymentsSQL.setter
    def listMDownPaymentsSQL(self, value):
        self._listMDownPaymentsSQL = value

    @property
    def listMCustsSQL(self):
        return self._listMCustsSQL

    @listMCustsSQL.setter
    def listMCustsSQL(self, value):
        self._listMCustsSQL = value

    @property
    def listMCustAddrsSQL(self):
        return self._listMCustsSQL

    @listMCustAddrsSQL.setter
    def listMCustAddrsSQL(self, value):
        self._listMCustAddrsSQL = value

    @property
    def listMInvoicesSQL(self):
        return self._listMInvoicesSQL

    @listMInvoicesSQL.setter
    def listMInvoicesSQL(self, value):
        self._listMInvoicesSQL = value

    @property
    def insertOrUpdateEProductSQL(self):
        return self._insertOrUpdateEProductSQL

    @insertOrUpdateEProductSQL.setter
    def insertOrUpdateEProductSQL(self, value):
        self._insertOrUpdateEProductSQL = value

    @property
    def listNeedShipOrdersSQL(self):
        return self._listNeedShipOrdersSQL

    @listNeedShipOrdersSQL.setter
    def listNeedShipOrdersSQL(self, value):
        self._listNeedShipOrdersSQL = value

    @property
    def listOrderExistingShipmentSQL(self):
        return self._listOrderExistingShipmentSQL

    @listOrderExistingShipmentSQL.setter
    def listOrderExistingShipmentSQL(self, value):
        self._listOrderExistingShipmentSQL = value

    @property
    def addOrUpdateEProductMasterSQL(self):
        return self._addOrUpdateEProductMasterSQL

    @addOrUpdateEProductMasterSQL.setter
    def addOrUpdateEProductMasterSQL(self, value):
        self._addOrUpdateEProductMasterSQL = value

    @property
    def addOrUpdateEProductInventorySQL(self):
        return self._addOrUpdateEProductInventorySQL

    @addOrUpdateEProductInventorySQL.setter
    def addOrUpdateEProductInventorySQL(self, value):
        self._addOrUpdateEProductInventorySQL = value

    @property
    def addOrUpdateEProductPriceSQL(self):
        return self._addOrUpdateEProductPriceSQL

    @addOrUpdateEProductPriceSQL.setter
    def addOrUpdateEProductPriceSQL(self, value):
        self._addOrUpdateEProductPriceSQL = value

    @property
    def addOrUpdateEProductTierPriceSQL(self):
        return self._addOrUpdateEProductTierPriceSQL

    @addOrUpdateEProductTierPriceSQL.setter
    def addOrUpdateEProductTierPriceSQL(self, value):
        self._addOrUpdateEProductTierPriceSQL = value

    @property
    def addOrUpdateEProductGroupPriceSQL(self):
        return self._addOrUpdateEProductGroupPriceSQL

    @addOrUpdateEProductGroupPriceSQL.setter
    def addOrUpdateEProductGroupPriceSQL(self, value):
        self._addOrUpdateEProductGroupPriceSQL = value

    @property
    def addOrUpdateECustomerSQL(self):
        return self._addOrUpdateECustomerSQL

    @addOrUpdateECustomerSQL.setter
    def addOrUpdateECustomerSQL(self, value):
        self._addOrUpdateECustomerSQL = value

    @property
    def addOrUpdateEConfigProductSQL(self):
        return self._addOrUpdateEConfigProductSQL

    @addOrUpdateEConfigProductSQL.setter
    def addOrUpdateEConfigProductSQL(self, value):
        self._addOrUpdateEConfigProductSQL = value

    @property
    def addOrUpdateEProductCompanyPriceSQL(self):
        return self._addOrUpdateEProductCompanyPriceSQL

    @addOrUpdateEProductCompanyPriceSQL.setter
    def addOrUpdateEProductCompanyPriceSQL(self, value):
        self._addOrUpdateEProductCompanyPriceSQL = value

    @property
    def addOrUpdateEProductCategorySQL(self):
        return self._addOrUpdateEProductCategorySQL

    @addOrUpdateEProductCategorySQL.setter
    def addOrUpdateEProductCategorySQL(self, value):
        self._addOrUpdateEProductCategorySQL = value
# okay decompiling TX.pyc
