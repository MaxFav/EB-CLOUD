from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleReport(models.Model):
    _inherit = 'sale.report'

    untaxed_amount_reserved1 = fields.Float(string='Untaxed Amount Reserved', readonly=True)
    untaxed_amount_undelivered1 = fields.Float(string='Untaxed Amount Undelivered', readonly=True)
    quantity_reserved1 = fields.Float(string='Quantity Reserved', readonly=True)
    quantity_undelivered1 = fields.Float(string='Quantity Undelivered', readonly=True)
    effective_date = fields.Date(string='Effective Date', readonly=True)
    commitment_date = fields.Date(string='Commitment Date', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['untaxed_amount_reserved1'] = ', sum(l.untaxed_amount_reserved1) as untaxed_amount_reserved1'
        fields['untaxed_amount_undelivered1'] = ', sum(l.untaxed_amount_undelivered1) as untaxed_amount_undelivered1'
        fields['quantity_reserved1'] = ', sum(l.quantity_reserved1) as quantity_reserved1'
        fields['quantity_undelivered1'] = ', sum(l.quantity_undelivered1) as quantity_undelivered1'
        fields['effective_date'] = ', s.effective_date'
        fields['commitment_date'] = ', s.commitment_date'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)