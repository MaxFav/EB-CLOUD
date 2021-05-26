# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    linked_payment_ids = fields.One2many('account.payment', 'linked_purchase_order_id')
    outstanding_balance = fields.Float(string="Outstanding Balance", compute='_compute_outstanding_balance', store=True,
                                       help="The total amount of money due for this purchase order, before considering "
                                            "unreconciled prepayments.")
    advance_payment_total = fields.Float(string="Advance Payment Total", compute='_compute_advance_payment_total')
    reconciled_advance_payment_total = fields.Float("Reconciled Prepayment", compute='_compute_advance_payment_total',
                                                    help="Total amount of pre-payment that has already been assigned to"
                                                         " invoices linked to this purchase order. It has already been "
                                                         "subtracted from the Total to create the Outstanding figure.")
    unreconciled_advance_payment_total = fields.Float("Unreconciled Prepayment", compute='_compute_advance_payment_total',
                                                      help="Total amount of pre-payment ready to assign to an invoice "
                                                           "for this purchase order. If assigned, this figure and the "
                                                           "Outstanding will both reduce and Reconciled Prepayment will"
                                                           " increase.")

    def action_open_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Wizard',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('invoice_ids', 'invoice_ids.residual')
    def _compute_outstanding_balance(self):
        for order in self:
            amount_to_invoice = order.amount_total
            for invoice in order.invoice_ids:
                amount_to_invoice -= (invoice.amount_total - invoice.residual)
            order.outstanding_balance = amount_to_invoice

    @api.depends('linked_payment_ids', 'linked_payment_ids.amount', 'invoice_ids', 'invoice_ids.payment_move_line_ids',
                 'invoice_ids.outstanding_debit_ids')
    def _compute_advance_payment_total(self):
        for order in self:
            amount_advance = order.advance_payment_total
            amount_unreconciled = 0
            amount_reconciled = 0
            for payment in order.linked_payment_ids:
                amount_advance += payment.amount
            order.advance_payment_total = amount_advance

            for invoice in order.invoice_ids:
                if order.currency_id != order.company_id.currency_id:
                    amount_unreconciled += sum(invoice.outstanding_debit_ids.mapped('amount_currency'))
                    amount_reconciled += sum(invoice.payment_move_line_ids.mapped('amount_currency'))
                else:
                    amount_unreconciled += sum(invoice.outstanding_debit_ids.mapped('debit'))
                    amount_reconciled += sum(invoice.payment_move_line_ids.mapped('debit'))

            order.unreconciled_advance_payment_total = amount_unreconciled
            order.reconciled_advance_payment_total = amount_reconciled
