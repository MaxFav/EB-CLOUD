from odoo import models, fields, api, _

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.multi
    def create_notional_invoices(self):
        """
        This function will create a matching purchase and sales invoice using the information
        from the invoice line and will reconcile them against each other.
        Function is called if the line has a reverse charge tax on
        """
        hmrc_partner = self.env.ref('smart_mtd.hmrc_partner')
        for line in self:
            #Set the products/accounts depending on if it is UK or EU
            if line.invoice_line_tax_ids == self.env.ref('smart_mtd.Reverse_Charge_EU'):
                reverse_charge_sales_product = self.env.ref('smart_mtd.rc_eu_sale_product')
                reverse_charge_purchase_product = self.env.ref('smart_mtd.rc_eu_purchase_product')
                reverse_charge_account = self.env.ref('smart_mtd.hmrc_reverse_charge_sales')
            elif line.invoice_line_tax_ids == self.env.ref('smart_mtd.Reverse_Charge_UK'):
                reverse_charge_sales_product = self.env.ref('smart_mtd.rc_uk_sale_product')
                reverse_charge_purchase_product = self.env.ref('smart_mtd.rc_uk_purchase_product')
                reverse_charge_account = self.env.ref('smart_mtd.hmrc_reverse_charge_sales_uk')      
           
            #Create sale invoice vals
            sale_invoice_line_vals = {
                'product_id': reverse_charge_sales_product.id,
                'quantity': 1,
                'name': 'RC Notional Sale ' + line.invoice_id.number,
                'price_unit': line.price_total,
                'account_id': reverse_charge_account.id,
                'invoice_line_tax_ids': [[6, False, [reverse_charge_sales_product.taxes_id.id]]]
                }
            sale_invoice_vals = {
                'type': 'out_invoice',
                'invoice_line_ids': [[0, False, sale_invoice_line_vals]],
                'partner_id': hmrc_partner.id,
                'date_due': line.invoice_id.date_due,
                'date_invoice': line.invoice_id.date_invoice,
                'currency_id': line.invoice_id.currency_id.id
                }
            
            #Create purchase invoice vals
            purchase_invoice_line_vals = {
                'product_id': reverse_charge_purchase_product.id,
                'quantity': 1,
                'name': 'RC Notional Purchase ' + line.invoice_id.number,
                'price_unit': line.price_total,
                'account_id': reverse_charge_account.id,
                'invoice_line_tax_ids': [[6, False, [reverse_charge_purchase_product.supplier_taxes_id.id]]]
                }
            purchase_invoice_vals = {
                'type': 'in_invoice',
                'invoice_line_ids': [[0, False, purchase_invoice_line_vals]],
                'partner_id': hmrc_partner.id,
                'date_due': line.invoice_id.date_due,
                'date_invoice': line.invoice_id.date_invoice,
                'currency_id': line.invoice_id.currency_id.id,
                'account_id': self.env.ref('l10n_uk.1100').id
                }
            
            #Create and validate invoices
            new_invoices = self.env['account.invoice'].create([sale_invoice_vals, purchase_invoice_vals])
            new_invoices.action_invoice_open()
            
            #Assign the 2 invoices against each other using the debit move line from the sales invoice and assign to the purchase invoice
            debit_move_line = self.env['account.move.line'].search([('invoice_id', '=', new_invoices[0].id), ('debit', '>', 0)])
            new_invoices[1].assign_outstanding_credit(debit_move_line.id)