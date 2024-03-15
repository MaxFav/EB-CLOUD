from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    bad_debt_enabled = fields.Boolean(compute='_compute_bad_debt_enabled')
'''
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

    def auto_pay_invoice(self):
        if not self.sudo().env['smart_mtd.general_settings'].search([], limit=1).auto_pay_invoice:
            return
        for record in self:
            payment_wizard_vals = record.action_register_payment()
            payment_wizard = self.env['account.payment.register'].with_context(payment_wizard_vals['context']).create({})
            payment_wizard.action_create_payments()

    def action_post(self):
        res = super(AccountInvoice, self).action_post()
        for record in self:
            if all(line.tax_ids == self.env.ref('smart_mtd.tax_postponed_import_vat') for line in record.invoice_line_ids):
                record.auto_pay_invoice()
        return res
'''