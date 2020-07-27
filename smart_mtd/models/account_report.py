from odoo import models, fields, api, _
import ast

class AccountReport(models.AbstractModel):
    _inherit = "account.report"
    
    filter_mtd_unsent = False
    
    def _set_context(self, options):
        res = super(AccountReport, self)._set_context(options)
        if options.get('mtd_unsent'):
            res['hmrc_submitted'] =  False
        return res
      
    def open_tax_report_line(self, options, params=None):
        context = self.env.context.copy()
        active_id = int(str(params.get('id')).split('_')[0])
        line = self.env['account.financial.html.report.line'].browse(active_id)
        if line.search_domain and not context.get('search_domain', False):
            domain = ast.literal_eval(line.search_domain)
            context['search_domain'] = domain
        return super(AccountReport, self.with_context(context)).open_tax_report_line(options, params)
    
    def open_action(self, options, domain):
        if self.env.context.get('search_domain'):
            domain = self.env.context.get('search_domain')
        res = super(AccountReport, self).open_action(options, domain)
        if options.get('mtd_unsent', False) and res.get('domain', False):
            #Remove date search from domain
            new_domain = [attr for attr in res['domain'] if attr[0] != 'date']
            #Add in custom search for hmrc_sumbitted field and end data
            new_domain += [('hmrc_submitted', '=', False),
                           ('date', '<=', options.get('date').get('date_to'))]
            res['domain'] = new_domain
        return res