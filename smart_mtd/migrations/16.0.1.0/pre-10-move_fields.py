from odoo.upgrade import util

def migrate(cr,version):
    util.remove_field(cr,'account.move','territory')
    util.remove_field(cr,'account.move','category')
    util.move_field_to_module(cr,'account.invoice.report','territory','new_field_invoicing_report','eb_extended_sales_reporting')
    util.move_field_to_module(cr,'account.invoice.report','category','new_field_invoicing_report','eb_extended_sales_reporting')
    util.remove_field(cr,'sale.order','territory')
    util.remove_field(cr,'sale.order','category')
    util.move_field_to_module(cr,'sale.report','territory','new_field_invoicing_report','eb_extended_sales_reporting')
    util.move_field_to_module(cr,'sale.report','category','new_field_invoicing_report','eb_extended_sales_reporting')