from odoo.upgrade import util

def migrate(cr,version):
    util.move_field_to_module(cr,"res.partner","warehouse_id","eb_bulk_returns","eb_transfers")