odoo.define('product_listing_cart.add_to_cart', function (require) {
    "use strict"

    var WebsiteSaleOptions = require('website_sale_options.website_sale');
    var weContext = require('web_editor.context');

    WebsiteSaleOptions.include({

        events: _.extend({
            "click a.submit-qty": 'async _AddQtyToCart'
        }, WebsiteSaleOptions.prototype.events),

        _AddQtyToCart: function (ev) {
            this.$form = $(ev.currentTarget).closest('form');
            this.$form.ajaxSubmit({
                url: '/shop/cart/update_option',
                data: {
                    lang: weContext.get().lang,
                    from_product_grid: true,
                },
                success: function (quantity) {
                    var $quantity = $(".my_cart_quantity");
                    var $divcart = $(ev.currentTarget).closest('div.js_add_to_cart')
                    $quantity.parent().parent().removeClass("d-none", !quantity);
                    $quantity.html(quantity).hide().fadeIn(600);
                    $divcart.hide(400);
                }
            });
        },

    });
});
