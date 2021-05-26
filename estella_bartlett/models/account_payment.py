# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        source_purchase_order = self._context.get('source_purchase_order')
        new_payment_type = self._context.get('new_payment_type')
        wizard_generated = self._context.get('wizard_generated')
        new_partner_type = self._context.get('new_partner_type')
        payment_partner = self._context.get('payment_partner')

        rec = super(AccountPayment, self).default_get(fields)

        rec['linked_purchase_order_id'] = source_purchase_order
        if new_payment_type:
            rec['payment_type'] = new_payment_type
        rec['generated_from_wizard'] = wizard_generated
        if new_partner_type:
            rec['partner_type'] = new_partner_type
        rec['partner_id'] = payment_partner

        return rec

    linked_purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", domain="[('state','=','purchase')]")
    generated_from_wizard = fields.Boolean(default=False, readonly=True)
    reconciled_move_lines_debit_total = fields.Monetary(compute='_compute_move_lines_debit_total', string="Reconciled Amount")
    unreconciled_move_lines_debit_total = fields.Monetary(compute='_compute_move_lines_debit_total', string="Unreconciled Amount")

    @api.onchange('linked_purchase_order_id')
    def onchange_linked_po(self):
        if not self.linked_purchase_order_id:
            return
        self.partner_id = self.linked_purchase_order_id.partner_id

    @api.depends('move_line_ids', 'move_line_ids.debit')
    def _compute_move_lines_debit_total(self):
        for payment in self:
            amount_reconciled = 0
            amount_unreconciled = 0
            for line in payment.move_line_ids:
                if line.reconciled:
                    amount_reconciled += line.debit
                else:
                    amount_unreconciled += line.debit
            payment.reconciled_move_lines_debit_total = amount_reconciled
            payment.unreconciled_move_lines_debit_total = amount_unreconciled
