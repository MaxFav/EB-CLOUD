from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    eur_rrp = fields.Monetary(string="Euro RRP",compute="_compute_eur_rrp",store=True)

    @api.depends('list_price')
    def _compute_eur_rrp(self):
        for record in self:
            record.eur_rrp = record.list_price * 2

