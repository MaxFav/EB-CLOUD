from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    territory = fields.Selection(string='Territory', related='partner_id.x_studio_field_Xo5vK', store=True)
    category = fields.Selection(string='Category', related='partner_id.x_studio_field_KgSOM', store=True)