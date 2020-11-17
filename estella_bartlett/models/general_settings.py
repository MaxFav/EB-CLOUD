# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GeneralSettings(models.Model):
    _name = 'estella.general_settings'

    def recalculate_single_analytic_tag_ids(self):
        sale_order_lines = self.env['sale.order.line'].search([])
        sale_order_lines._compute_single_analytic_tag_id()
        account_invoice_lines = self.env['account.invoice.line'].search([])
        account_invoice_lines._compute_single_analytic_tag_id()
