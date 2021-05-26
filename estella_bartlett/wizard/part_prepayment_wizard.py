from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PartPrepaymentWizard(models.TransientModel):
    _name = 'part.prepayment.wizard'

    def _default_invoice_id(self):
        return self.env['account.invoice'].browse(self._context.get('active_id'))

    payment_money = fields.Monetary(compute="_compute_payment_total", string="Payment Total", currency_field="currency_id")
    part_payment = fields.Monetary(string="Part Payment to Make", required=True, currency_field="currency_id")
    invoice_id = fields.Many2one('account.invoice', default=_default_invoice_id, readonly=True)
    invoice_amount_total = fields.Monetary(related="invoice_id.amount_total", string="Invoice Amount Total")
    invoice_amount_due = fields.Monetary(related="invoice_id.residual", string="Invoice Amount Due")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    rel_outstanding_debit_ids = fields.Many2many(related="invoice_id.outstanding_debit_ids")
    outstanding_debit_move_line_ids = fields.Many2one('account.move.line', string="Outstanding Debits", required=True)

    @api.depends('outstanding_debit_move_line_ids')
    def _compute_payment_total(self):
        if self.currency_id != self.invoice_id.company_currency_id:
            self.payment_money = self.outstanding_debit_move_line_ids.amount_currency
        else:
            self.payment_money = self.outstanding_debit_move_line_ids.debit

    @api.constrains('part_payment', 'payment_money')
    def check_part_payment(self):
        if self.part_payment > self.payment_money \
                and 0 < self.part_payment < self.invoice_amount_due:
            raise ValidationError('Cannot part-pay more money from a payment than it contains.')
        if self.part_payment == self.payment_money:
            raise ValidationError('Cannot part-pay as much money from a payment as it contains.')
        if self.part_payment > self.invoice_amount_due:
            raise ValidationError('Cannot part-pay more money than is due for an invoice.')
        if self.part_payment <= 0:
            raise ValidationError('Part payment must contain a positive amount of money.')

    def button_save(self):
        # Cancel the move temporarily so I can change values within it.
        self.outstanding_debit_move_line_ids.move_id.button_cancel()

        # Search for a move line that matches the selected debit move line but in credit, as both need to be changed to
        # keep consistency.
        credit_line = self.env['account.move.line'].search([('move_id', '=', self.outstanding_debit_move_line_ids.move_id.id),
                                                            ('credit', '=', self.outstanding_debit_move_line_ids.debit),
                                                            ('journal_id', '=',
                                                             self.outstanding_debit_move_line_ids.journal_id.id),
                                                            ('reconciled', '=', False)], limit=1)

        # Copying the debit line and altering it so it becomes the new debit move line for the part payment.
        debit_copy = self.outstanding_debit_move_line_ids.copy_data()
        debit_dict = debit_copy[0]
        if self.currency_id != self.invoice_id.company_currency_id:
            debit_dict['amount_currency'] = self.part_payment
            debit_dict['debit'] = self.currency_id.compute(self.part_payment, self.invoice_id.company_currency_id)
        else:
            debit_dict['debit'] = self.part_payment
        debit_dict['payment_id'] = self.outstanding_debit_move_line_ids.payment_id.id

        # Copying the credit line and altering it so it becomes the new credit move line for the part payment.
        credit_copy = credit_line[0].copy_data()
        credit_dict = credit_copy[0]
        if self.currency_id != self.invoice_id.company_currency_id:
            credit_dict['amount_currency'] = -self.part_payment
            credit_dict['credit'] = self.currency_id.compute(self.part_payment, self.invoice_id.company_currency_id)
        else:
            credit_dict['credit'] = self.part_payment
        credit_dict['payment_id'] = self.outstanding_debit_move_line_ids.payment_id.id

        # Creating the new credit and debit part payment move lines, and adding them to the move.
        self.env['account.move.line'].create([debit_dict, credit_dict])

        # Finding the original debit and credit move lines and reducing their value by the amount of the part payment.
        if self.currency_id != self.invoice_id.company_currency_id:
            debit_record = self.env['account.move.line'].search([('amount_currency', '=', self.payment_money),
                                                                ('move_id', '=', self.outstanding_debit_move_line_ids.move_id.id),
                                                                ('reconciled', '=', False)], limit=1)
            if debit_record:
                debit_record.with_context(prepayment_edit=True).write({'amount_currency': debit_record.amount_currency - self.part_payment})
                debit_orig_currency = self.currency_id.compute(debit_record.amount_currency, self.invoice_id.company_currency_id)
                debit_record.with_context(prepayment_edit=True).write({'debit': debit_orig_currency})
        else:
            debit_record = self.env['account.move.line'].search([('debit', '=', self.payment_money),
                                                                 ('move_id', '=',
                                                                  self.outstanding_debit_move_line_ids.move_id.id),
                                                                 ('reconciled', '=', False)], limit=1)
            if debit_record:
                debit_record.with_context(prepayment_edit=True).write({'debit': debit_record.debit - self.part_payment})

        if self.currency_id != self.invoice_id.company_currency_id:
            credit_record = self.env['account.move.line'].search([('amount_currency', '=', -self.payment_money),
                                                    ('move_id', '=',self.outstanding_debit_move_line_ids.move_id.id),
                                                    ('reconciled', '=', False)], limit=1)
            if credit_record:
                credit_record.amount_currency += self.part_payment
                credit_orig_currency = self.currency_id.compute(credit_record.amount_currency,self.invoice_id.company_currency_id)
                credit_record.credit = abs(credit_orig_currency)
        else:
            credit_record = self.env['account.move.line'].search([('credit', '=', self.payment_money),
                                                              ('move_id', '=',
                                                              self.outstanding_debit_move_line_ids.move_id.id),
                                                              ('reconciled', '=', False)], limit=1)
            if credit_record:
                credit_record.credit -= self.part_payment

        # Assigning the part payment to the invoice, finally, thus reducing the amount due of the invoice.
        if self.currency_id != self.invoice_id.company_currency_id:
            debit_company_currency = self.currency_id.compute(self.part_payment, self.invoice_id.company_currency_id)
            part_payment_record = self.env['account.move.line'].search([('debit', '=', debit_company_currency),
                                                                    ('move_id', '=',
                                                                    self.outstanding_debit_move_line_ids.move_id.id),
                                                                    ('reconciled', '=', False)], limit=1)  # Possible dupes?
        else:
            part_payment_record = self.env['account.move.line'].search([('debit', '=', self.part_payment),
                                                                        ('move_id', '=',
                                                                         self.outstanding_debit_move_line_ids.move_id.id),
                                                                        ('reconciled', '=', False)],
                                                                       limit=1)  # Possible dupes?

        self.invoice_id.assign_outstanding_credit(credit_aml_id=part_payment_record.id)

        # Re-posting the move, to counter the first line of code.
        self.outstanding_debit_move_line_ids.move_id.action_post()
        return {'type': 'ir.actions.act_window_close'}
