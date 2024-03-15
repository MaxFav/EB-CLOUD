odoo.define('product_listing_cart.add_to_cart', function (require) {
    "use strict"

var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');
var wSaleUtils = require('website_sale.utils');
const wUtils = require('website.utils');
require("web.zoomodoo");


publicWidget.registry.WebsiteSale.include({
    
    _submitForm: function () {
        let params = this.rootProduct;
        params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        params.current_url = window.location.href
        var active_btn =  '#btn_' +params.product_id.toString();
        const $record = $(active_btn);
        $record.hide();
        params.disabeld_btn = true;
        if (this.isBuyNow) {
            params.express = true;
        }

        return wUtils.sendRequest('/shop/cart/update', params);
    },
    
    
    
    });
});
