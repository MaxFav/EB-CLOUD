from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(string="Unit Price",compute='_compute_price_unit',digits=(12,2),store=True, readonly=False, required=True, precompute=True)