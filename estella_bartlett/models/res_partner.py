# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class ResPartner(models.Model):
    _inherit = "res.partner"

    territory_id = fields.Many2one('account.analytic.account', string="Territory")
    sales_channel_ids = fields.Many2many('account.analytic.tag', string="Sales Channel")
    x_studio_field_EpOAQ = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')


