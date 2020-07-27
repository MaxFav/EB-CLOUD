from odoo import models, fields, api, _

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"
    
    search_domain = fields.Char('Search domain', help="This field is used when journal entries with different domains need to be displayed for one line")