from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    warehouse_id = fields.Many2one("stock.warehouse", domain=False)
