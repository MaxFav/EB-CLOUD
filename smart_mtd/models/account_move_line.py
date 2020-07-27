from odoo import models, fields, api, _

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'
    
    hmrc_submitted = fields.Boolean(string="Submitted to HMRC", help="If the line has been submitted as part of a VAT return to HMRC this is true.")
    date_on_vat_return = fields.Date(string="VAT Return Submission Date", help="This field stores the date the move line was submitted to HMRC succesfully")
    
    
    @api.model
    def _query_get(self, domain=None):
        context = dict(self._context or {})
        domain = domain or []
        if 'hmrc_submitted' in context and context['hmrc_submitted'] == False or context.get('mtd_unsent', False) or ('options' in context and context['options'].get('mtd_unsent', False)):
            #Want to see all unsubmitted lines up to the end date
            #So we are popping the start date and looking at unsubmitted lines
            domain += [('hmrc_submitted', '=', False)]
            if 'date_from' in context:
                context.pop('date_from')
            return super(AccountMoveLine, self.with_context(context))._query_get(domain)
        return super(AccountMoveLine, self)._query_get(domain)