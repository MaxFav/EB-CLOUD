from odoo.upgrade import util

def migrate(cr,version):
    util.remove_field(cr,"account.move","bad_debt_enabled")
    util.remove_field(cr,"account.move","territory")
    util.remove_field(cr,"account.move","category")
    util.remove_field(cr,"sale.report","territory")
    util.remove_field(cr,"sale.report","category")
    util.remove_field(cr,"account.move.line","hmrc_submitted")
    util.remove_field(cr,"account.move.line","date_on_vat_return")
    util.remove_field(cr,"l10n_uk.vat.obligation","submission_message")
    util.remove_field(cr,"l10n_uk.vat.obligation","report_attachment_name")
    util.remove_field(cr,"l10n_uk.vat.obligation","report_attachment_id")
