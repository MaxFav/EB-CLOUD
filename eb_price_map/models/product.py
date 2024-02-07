from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    euro_rrp = fields.Monetary(string="Euro RRP",compute="_compute_euro_rrp",store=True)
    currency_euro = fields.Many2one('res.currency',string="Euro", default=1)
    usd_rrp = fields.Monetary(string="USD RRP",compute="_compute_usd_rrp",store=True,currency_field="currency_euro")

    @api.depends('list_price')
    def _compute_euro_rrp(self):
        for record in self:
            record.euro_rrp = record.list_price * 2

    @api.depends('list_price')
    def _compute_usd_rrp(self):
        for record in self:
            record.usd_rrp = record.list_price / 2