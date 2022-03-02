from odoo import models, fields, api, _

class AccountTag(models.Model):
    _inherit = 'account.account.tag'
    
    def smart_get_tags(self, country_code, tags):
        return self.search([('name', 'in', tags), ('country_id.code', '=', country_code)]).ids
