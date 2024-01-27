from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    territory = fields.Selection(string="Territory", related="partner_id.territory", store=True)
    category = fields.Selection(string="Category", related="partner_id.category", store=True)
