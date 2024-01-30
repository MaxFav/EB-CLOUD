from odoo import models, fields, api, _

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    hmrc_submitted = fields.Boolean(string="Submitted to HMRC", help="If the line has been submitted as part of a VAT return to HMRC this is true.", default=False)
    date_on_vat_return = fields.Date(string="VAT Return Submission Date", help="This field stores the date the move line was submitted to HMRC succesfully")