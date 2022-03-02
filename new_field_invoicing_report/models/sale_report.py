# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    territory = fields.Selection([('UK', 'UK'), ('EU', 'EU'), ('USA', 'USA'), ('ROW', 'ROW')])
    category = fields.Selection([('Department Store', 'Department Store'), ('Multiple Retailer', 'Multiple Retailer'), ('Online Retailer', 'Online Retailer'), ('Indies', 'Indies'), ('Travel Retail', 'Travel Retail'), ('Websales', 'Websales'), ('Retail', 'Retail'), ('Concession', 'Concession'), ('White Label', 'White Label'), ('Discount Retailer', 'Discount Retailer')])

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['territory'] = ', s.territory as territory'
        fields['category'] = ', s.category as category'

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
