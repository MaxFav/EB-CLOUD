from odoo.upgrade import util

def migrate(cr,version):
    util.remove_record(cr,"product_listing_cart.product_quantity")