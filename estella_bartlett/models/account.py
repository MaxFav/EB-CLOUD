# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class AccountAccount(models.Model):
    _inherit = "account.account"

    mandatory_analytic_account = fields.Boolean('Mandatory Analytic Account')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        for record in self:
            if record.type == 'in_invoice':
                for line in record.invoice_line_ids:
                    if line.account_id and line.account_id.mandatory_analytic_account:
                        if not line.account_analytic_id or not line.analytic_tag_ids:
                            raise UserError(_("Analytic Account or Analytic Tag not set for one or more invoice lines"))
        res = super(AccountInvoice, self).action_invoice_open()

        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    mandatory_analytic_account = fields.Boolean('Analytic Mandatory', related='account_id.mandatory_analytic_account', readonly=True)
    single_analytic_tag_id = fields.Many2one('account.analytic.tag', string="Analytic Tag",
                                             compute="_compute_single_analytic_tag_id", store=True)

    @api.depends('analytic_tag_ids', 'analytic_tag_ids.active')
    def _compute_single_analytic_tag_id(self):
        for line in self:
            if line.analytic_tag_ids.filtered(lambda r: r.active):
                line.single_analytic_tag_id = line.analytic_tag_ids.filtered(lambda r: r.active)[0]
            else:
                line.single_analytic_tag_id = False
