from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    bad_debt_enabled = fields.Boolean(compute='_compute_bad_debt_enabled')

    def _compute_bad_debt_enabled(self):
        for record in self:
            if record.invoice_date:
                if datetime.today().date() >= record.invoice_date + relativedelta(
                        months=+6) and record.amount_residual > 0:
                    record.bad_debt_enabled = True
                else:
                    record.bad_debt_enabled = False
            else:
                record.bad_debt_enabled = False

    def bad_debt(self):
        view_id = self.env.ref('smart_mtd.bad_debt_wizard_form').id
        return {'type': 'ir.actions.act_window',
                'name': 'Bad Debt Wizard',
                'res_model': 'smart_mtd.bad.debt.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'views': [[view_id, 'form']],
                }