# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountAccount(models.Model):
    _inherit = "account.account"

    mandatory_analytic_account = fields.Boolean('Mandatory Analytic Account')
    is_sales_commission_account = fields.Boolean(string="Commission Account")


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    outstanding_debit_ids = fields.Many2many('account.move.line', compute="_compute_outstanding_debits")

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

    # Adding an extra domain to the beginning so only move lines linked to a payment with the same linked PO as the
    # invoice's origin POs return as results.
    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            domain = [('payment_id.linked_purchase_order_id.name', 'like', self.origin),
                      ('account_id', '=', self.account_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                      ('reconciled', '=', False),
                      ('move_id.state', '=', 'posted'),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None),
                      ('amount_residual', '!=', 0.0)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        amount_to_show = currency._convert(abs(line.amount_residual), self.currency_id, self.company_id,
                                                           line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    if line.ref:
                        title = '%s : %s' % (line.move_id.name, line.ref)
                    else:
                        title = line.move_id.name
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'title': title,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    def action_part_prepayment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Part Prepayment Wizard',
            'res_model': 'part.prepayment.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('outstanding_credits_debits_widget')
    def _compute_outstanding_debits(self):
        for invoice in self:
            domain = [('payment_id.linked_purchase_order_id.name', 'like', invoice.origin),
                      ('account_id', '=', invoice.account_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(invoice.partner_id).id),
                      ('reconciled', '=', False),
                      ('move_id.state', '=', 'posted'),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None),
                      ('amount_residual', '!=', 0.0)]
            lines = self.env['account.move.line'].search(domain)
            invoice.outstanding_debit_ids = lines.ids


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
