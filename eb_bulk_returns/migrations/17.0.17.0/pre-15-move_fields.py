from odoo.upgrade import util

def migrate(cr,version):    
    util.move_field_to_module(cr,"res.partner","warehouse_id","eb_bulk_returns","eb_transfers")
    util.move_field_to_module(cr,"stock.picking","sum_initial_demand","eb_sales_quotation_to_invoice","eb_transfers") 
    util.move_field_to_module(cr,"stock.picking","percentage_reserved","eb_sales_quotation_to_invoice","eb_transfers")   
    