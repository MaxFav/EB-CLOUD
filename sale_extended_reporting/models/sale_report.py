from odoo import api, fields, models, _

class SaleReport(models.Model):
    _inherit = 'sale.report'

    untaxed_amount_reserved11 = fields.Float(string='Untaxed Amount Reserved', readonly=True)
    untaxed_amount_undelivered13 = fields.Float(string='Untaxed Amount Left to Delivered', readonly=True)
    quantity_reserved11 = fields.Float(string='Quantity Reserved', readonly=True)
    quantity_undelivered13 = fields.Float(string='Qty Left to Delivered', readonly=True)
    effective_date = fields.Date(string='Effective Date', readonly=True)
    commitment_date = fields.Date(string='Commitment Date', readonly=True)

    def _select_additional_fields(self):
       fields = {
            'untaxed_amount_reserved11': 'sum(l.untaxed_amount_reserved11)',
            'untaxed_amount_undelivered13': 'sum(l.untaxed_amount_undelivered13)',
            'quantity_reserved11': 'sum(l.quantity_reserved11)',
            'quantity_undelivered13': 'sum(l.quantity_undelivered13)',
            'effective_date': 's.effective_date',
            'commitment_date': 's.commitment_date'
       }
       return fields