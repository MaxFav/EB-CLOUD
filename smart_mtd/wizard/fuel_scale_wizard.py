# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class FuelScaleWizard(models.TransientModel):
    _name = 'smart_mtd.fuel.scale.wizard'
    
    date = fields.Date(string = "Date", help="Typically the quarter end date")
    driver_name = fields.Char(string = "Driver Name")
    registration_number = fields.Char(string = "Registration Number")
    total_charge = fields.Float(string = "Total Charge (including VAT)")
    
    
    def create_journal_entry(self):
        misc_operations_journal = self.env['account.journal'].search([('code', '=', 'MISC')])
        fuel_scale_tax = self.env.ref('smart_mtd.fuel_scale_tax')
        
        #Create move with information from wizard
        new_move = {
            'date': self.date,
            'ref': 'Fuel Scale Charge',
            'journal_id': misc_operations_journal.id,
            }
        new_move = self.env['account.move'].create(new_move)
        
        #Create 3 lines for journal entry
        debit_line = {
            'account_id': self.env.ref('smart_mtd.account_fuel_scale_charge').id,
            'debit': self.total_charge,
            'credit': 0,
            'name': self.driver_name + ' ' + self.registration_number,
            'move_id': new_move.id
            }
        
        credit_line = {
            'account_id': self.env.ref('smart_mtd.account_fuel_scale_charge').id,
            'debit': 0,
            'credit': round((self.total_charge / (1 + fuel_scale_tax.amount/100)), 2),
            'name': self.driver_name + ' ' + self.registration_number,
            'move_id': new_move.id,
            'tax_ids': [[6, False, [fuel_scale_tax.id]]],
            }
        
        #Compute tax
        tax_dict = fuel_scale_tax.compute_all(self.total_charge / (1 + fuel_scale_tax.amount/100))['taxes'][0]
        
        tax_line = {
            'account_id': fuel_scale_tax.account_id.id,
            'debit': 0,
            'credit': tax_dict['amount'],
            'name': self.driver_name + ' ' + self.registration_number,
            'move_id': new_move.id,
            'tax_line_id': tax_dict['id'],
            }
        
        #Create move lines and post the journal entry
        self.env['account.move.line'].create([debit_line, credit_line, tax_line])
        new_move.action_post()
        
        #Return the form view of the newly created journal entry
        view_id = self.env.ref('account.view_move_form').id        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'target': 'current',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'res_id': new_move.id
            }