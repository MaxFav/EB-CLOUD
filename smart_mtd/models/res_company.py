from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    def get_uk_company(self):
        company_param = self.env['ir.config_parameter'].sudo().get_param('smart_mtd.company')
        if company_param:
            return self.browse(int(company_param))
        uk_accounting_template = self.env.ref('l10n_uk.l10n_uk')
        uk_company = self.sudo().search([('chart_template_id', '=', uk_accounting_template.id)], limit=1)
        if not uk_company:
            raise ValidationError('UK Accounting is not set against any company')
        return uk_company


    def get_sales_control_tax(self):
        company_id = self.get_uk_company()
        id_ref = 'l10n_uk.%s_2200' % company_id.id
        return self.env.ref(id_ref).id

    def get_purchase_control_tax(self):
        company_id = self.get_uk_company()
        id_ref = 'l10n_uk.%s_2201' % company_id.id
        return self.env.ref(id_ref).id