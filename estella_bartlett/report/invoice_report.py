# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    single_analytic_tag_id = fields.Many2one('account.analytic.tag', string="Analytic Tag", readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.single_analytic_tag_id as single_analytic_tag_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ail.single_analytic_tag_id as single_analytic_tag_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ail.single_analytic_tag_id"
