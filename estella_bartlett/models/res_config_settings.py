from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_pay_by = fields.Selection(default='invoice')
    commission_calc = fields.Selection(default='customer')
    commission_account_id = fields.Many2one(domain=[('is_sales_commission_account', '=', True)])
