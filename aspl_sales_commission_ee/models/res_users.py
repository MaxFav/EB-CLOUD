# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ResUsers(models.Model):
    _inherit = "res.users"

    is_sales_agent = fields.Boolean(related="partner_id.is_sales_agent", string="Sales Agent",
                                    help="The Sales Agent field is set on a user's related contact form.")
