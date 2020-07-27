from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
class AccountInvoice(models.Model):

    _inherit = 'account.invoice'
    
    bad_debt_enabled = fields.Boolean(compute='_compute_bad_debt_enabled')
    
    @api.multi
    def _compute_bad_debt_enabled(self):
        for record in self:
            if record.date_invoice:
                if datetime.today().date() >= record.date_invoice + relativedelta(months = +6) and record.residual == record.amount_total:
                    record.bad_debt_enabled = True
                
    @api.multi
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
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        reverse_charge_taxes = self.env.ref('smart_mtd.Reverse_Charge_UK') + self.env.ref('smart_mtd.Reverse_Charge_EU')
        reverse_charge_lines = self.mapped('invoice_line_ids').filtered(lambda x: x.invoice_line_tax_ids in reverse_charge_taxes)
        if reverse_charge_lines:
            reverse_charge_lines.create_notional_invoices()        
        return res
    