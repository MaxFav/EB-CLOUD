from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")