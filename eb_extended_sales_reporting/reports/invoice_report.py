from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    territory = fields.Selection([('UK', 'UK'), ('EU', 'EU'), ('USA', 'USA'), ('ROW', 'ROW')])
    category = fields.Selection([('Department Store', 'Department Store'), ('Multiple Retailer', 'Multiple Retailer'), ('Online Retailer', 'Online Retailer'), ('Indies', 'Indies'), ('Travel Retail', 'Travel Retail'), ('Websales', 'Websales'), ('Retail', 'Retail'), ('Concession', 'Concession'), ('White Label', 'White Label'), ('Discount Retailer', 'Discount Retailer')])

    def _select(self):
        return super()._select() + ", move.territory as territory, move.category as category"