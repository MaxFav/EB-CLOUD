from odoo import api, fields, models, _

class SaleReport(models.Model):
    _inherit = 'sale.report'

    untaxed_amount_reserved11 = fields.Float(string='Untaxed Amount Reserved', readonly=True)
    untaxed_amount_undelivered13 = fields.Float(string='Untaxed Amount Left to Delivered', readonly=True)
    quantity_reserved11 = fields.Float(string='Quantity Reserved', readonly=True)
    quantity_undelivered13 = fields.Float(string='Qty Left to Delivered', readonly=True)
    effective_date = fields.Date(string='Effective Date', readonly=True)
    commitment_date = fields.Date(string='Commitment Date', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['untaxed_amount_reserved11'] = ', sum(l.untaxed_amount_reserved11) as untaxed_amount_reserved11'
        fields['untaxed_amount_undelivered13'] = ', sum(l.untaxed_amount_undelivered13) as untaxed_amount_undelivered13'
        fields['quantity_reserved11'] = ', sum(l.quantity_reserved11) as quantity_reserved11'
        fields['quantity_undelivered13'] = ', sum(l.quantity_undelivered13) as quantity_undelivered13'
        fields['effective_date'] = ', s.effective_date'
        fields['commitment_date'] = ', s.commitment_date'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)