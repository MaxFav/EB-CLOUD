# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class BadDebtWizard(models.TransientModel):
    _name = 'smart_mtd.bad.debt.wizard'
    
    account_id = fields.Many2one('account.account', help="The net amount will be written off to this account")
    
    @api.multi
    def write_off(self):
        #Function to write off the invoice with tax
        #This function basically replicates what the reconciliation widget does, but the values needed are pulled from the invoice
        invoice_id = self.env.context.get('active_id')
        invoice = self.env['account.invoice'].browse(invoice_id)
        account_move_lines = invoice.move_id.line_ids
        misc_journal = self.env['account.journal'].search([('code', '=', 'MISC')])
        ids = []
        #Get the journal entry needed to reconcile against (uses same code from def open_reconcile_view)
        for aml in account_move_lines:
            if aml.account_id.reconcile:
                ids.extend([r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id.id for r in aml.matched_credit_ids])
                ids.append(aml.id)
        if not ids:
            raise UserError('No journal entry to reconcile against')
        new_move_ids = []
        
        #Create dictionary for the goods (net) line
        net_line_dict = {
            'name': 'Bad Debt',
            'debit': 0,
            'credit': invoice.amount_untaxed,
            'account_id': self.account_id.id,
            'journal_id': misc_journal.id,
            'partner_id': invoice.partner_id.id,
            'date': datetime.now().date(),
            'tax_ids':  [[4, tax_line.tax_id.id, None] for tax_line in invoice.tax_line_ids],
            }
        new_move_ids.append(net_line_dict)
        
        #Create dictionary for the tax lines
        for tax_line in invoice.tax_line_ids:
            tax_line_dict = {
                'name': tax_line.tax_id.name,
                'debit': 0,
                'credit': tax_line.amount_total,
                'account_id': tax_line.tax_id.account_id.id,
                'journal_id': misc_journal.id,
                'date': datetime.now().date(),
                'tax_line_id': tax_line.tax_id.id,                
                }
            new_move_ids.append(tax_line_dict)
        
        #Set the data parameter and pass to reconciliation widget function to process.
        data = [{'type': None, 'mv_line_ids': ids, 'new_mv_line_dicts': new_move_ids}]
        self.env['account.reconciliation.widget'].process_move_lines(data)
