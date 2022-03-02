# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class BadDebtWizard(models.TransientModel):
    _name = 'smart_mtd.bad.debt.wizard'
    
    account_id = fields.Many2one('account.account', help="The net amount will be written off to this account")
    
    
    def write_off(self):
        #Function to write off the invoice with tax
        #This function basically replicates what the reconciliation widget does, but the values needed are pulled from the invoice
        move_id = self.env.context.get('active_id')
        move = self.env['account.move'].browse(move_id)
        account_move_lines = move.line_ids
        misc_journal = self.env['account.journal'].search([('code', '=', 'MISC')])
        ids = []
        #Get the journal entry needed to reconcile against (uses same code from def open_reconcile_view)
        for aml in account_move_lines:
            if aml.account_id.reconcile:
                ids.extend([r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id.id for r in aml.matched_credit_ids])
                ids.append(aml.id)
        if len(ids) > 1:
            ids = self.env['account.move.line'].browse(ids).filtered(lambda x: x.debit == move.amount_total).ids
        if not ids:
            raise UserError('No journal entry to reconcile against')
        new_move_ids = []

        unpaid_factor = (move.amount_residual) / move.amount_total

        #Create dictionary for the goods (net) line
        net_line_dict = {
            'name': 'Bad Debt',
            'debit': 0,
            'credit': move.amount_untaxed * unpaid_factor,
            'account_id': self.account_id.id,
            'journal_id': misc_journal.id,
            'partner_id': move.partner_id.id,
            'date': datetime.now().date(),
            'tax_ids':  [[4, tax.id, None] for tax in move.invoice_line_ids.mapped('tax_ids')],
            'tax_tag_ids': [[4, tag.id, None] for tag in move.invoice_line_ids.mapped('tax_ids').refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'base').tag_ids]
            }
        new_move_ids.append(net_line_dict)
        
        #Create dictionary for the tax lines
        for line in move.line_ids.filtered(lambda line: line.tax_line_id):
            tax_line_dict = {
                'name': line.tax_line_id.name,
                'debit': 0,
                'credit': line.price_subtotal,
                'account_id': line.account_id.id,
                'journal_id': misc_journal.id,
                'date': datetime.now().date(),
                'tax_line_id': line.tax_line_id.id,
                'tax_tag_ids': [[4, tag.id, None] for tag in line.tax_line_id.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax').tag_ids]
                }
            new_move_ids.append(tax_line_dict)
        
        #Set the data parameter and pass to reconciliation widget function to process.
        data = [{'type': None, 'mv_line_ids': ids, 'new_mv_line_dicts': new_move_ids}]
        self.env['account.reconciliation.widget'].process_move_lines(data)
        test = 1