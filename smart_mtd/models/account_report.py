from odoo import models, fields, api, _

class TaxReport(models.AbstractModel):
    _inherit = 'account.generic.tax.report'

    filter_unsubmitted = False
    filter_submitted = False

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _get_options_domain(self, options):

        domain = super(AccountReport, self)._get_options_domain(options)

        if options.get('unsubmitted', False):
            domain += [('hmrc_submitted', '=', False)]
        if options.get('submitted', False):
            domain += [('hmrc_submitted', '=', True)]

        return domain

    # see _query_get
    @api.model
    def _query_get_aml_ids(self, options, domain=None):
        domain = self._get_options_domain(options) + (domain or [])
        self.env['account.move.line'].check_access_rights('read')

        query = self.env['account.move.line']._where_calc(domain)

        # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
        self.env['account.move.line']._apply_ir_rules(query)

        sql, params = query.select()
        self.env.cr.execute(sql, params)
        res = [res[0] for res in self._cr.fetchall()]

        return res



