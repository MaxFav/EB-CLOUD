from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    territory = fields.Selection(string="Territory", related="partner_id.territory", store=True)
    category = fields.Selection(string="Category", related="partner_id.category", store=True)
