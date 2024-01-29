from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    warehouse_id = fields.Many2one("stock.warehouse")