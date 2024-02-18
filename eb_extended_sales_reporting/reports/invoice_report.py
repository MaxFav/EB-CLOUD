from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    territory = fields.Selection([('UK', 'UK'), ('EU', 'EU'), ('USA', 'USA'), ('ROW', 'ROW')])
    category = fields.Selection([('Department Store', 'Department Store'), ('Multiple Retailer', 'Multiple Retailer'), ('Online Retailer', 'Online Retailer'), ('Indies', 'Indies'), ('Travel Retail', 'Travel Retail'), ('Websales', 'Websales'), ('Retail', 'Retail'), ('Concession', 'Concession'), ('White Label', 'White Label'), ('Discount Retailer', 'Discount Retailer')])
'''
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.territory as territory, move.category as category"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ai.territory as territory, ai.category as category"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.territory, ai.category"
'''