# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleReport(models.Model):
    _inherit = "sale.report"

    single_analytic_tag_id = fields.Many2one('account.analytic.tag', string="Analytic Tag", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['single_analytic_tag_id'] = ", l.single_analytic_tag_id as single_analytic_tag_id"
        groupby += ', l.single_analytic_tag_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
