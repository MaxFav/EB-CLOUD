from odoo.upgrade import util

def migrate(cr,version):
    util.remove_model(cr,"x_store") 
    util.remove_model(cr,"smart_mtd.general_settings")
    util.move_field_to_module(cr,"res.partner","warehouse_id","eb_bulk_returns","eb_transfers")   
    util.remove_field(cr,"account.move","bad_debt_enabled")
    util.remove_field(cr,"account.move.line","hmrc_submitted")
    util.remove_field(cr,"account.move.line","date_on_vat_return")
    util.remove_field(cr,"l10n_uk.vat.obligation","submission_message")
    util.remove_field(cr,"l10n_uk.vat.obligation","report_attachment_name")
    util.remove_field(cr,"l10n_uk.vat.obligation","report_attachment_id")