from odoo.upgrade import util

def migrate(cr,version):
    util.remove_module(cr,'eb_sales_quotation_to_invoice')
    util.rename_module(cr,'sale_automate','eb_sales_quotation_to_invoice')
    util.remove_module(cr,'eb_extended_sales_reporting')
    util.rename_module(cr,'sale_module_reporting','eb_extended_sales_reporting')
    util.remove_module(cr,'eb_bulk_returns')
    util.rename_module(cr,'estella_bartlett','eb_bulk_returns')
    util.rename_field(cr,'res.partner','territory_id','analytic_account_id')