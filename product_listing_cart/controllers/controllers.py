# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import fields, http, tools, _


class WebsiteSaleCart(WebsiteSale):
    
    @http.route(['/shop/cart/update_option'], type='http', auth="public", methods=['POST'], website=True, multilang=False)
    def cart_options_update_json(self, product_id, add_qty=1, set_qty=0, goto_shop=None, lang=None, **kw):
        # Needed to modify this because otherwise there were 2 inputs 'add_qty' and it behaved weirdly
        add_qty = (kw.get('from_product_grid') and kw.get('add_qty_grid')) or add_qty
        return super().cart_options_update_json(product_id, add_qty, set_qty, goto_shop, lang, **kw)

