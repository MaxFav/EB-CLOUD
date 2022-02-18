# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    territory = fields.Selection(string='Territory', related='partner_id.x_studio_field_Xo5vK', store=True)
    category = fields.Selection(string='Category', related='partner_id.x_studio_field_KgSOM', store=True)
