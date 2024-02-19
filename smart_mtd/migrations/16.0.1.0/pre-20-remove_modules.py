from odoo.upgrade import util

def migrate(cr,version):
    util.remove_module(cr,'estella_sale_stock')
    util.remove_module(cr,'sh_message')
    util.remove_module(cr,'sh_import_int_transfer')
    util.remove_module(cr,'batch_validation')
    util.remove_module(cr,'delivery_orders')
    util.remove_module(cr,'new_field_invoicing_report')
    util.remove_module(cr,'delevery_orders_list_extended')
    util.remove_module(cr,'estella_sales_team_partner')
    
    