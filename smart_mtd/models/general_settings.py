# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.l10n_uk_reports_hmrc.models import hmrc_service as HmrcSvc

class GeneralSettings(models.Model):
    _name = 'smart_mtd.general_settings'
    
    default_end_date = fields.Date(string="Default End Date (Account Move Line)",
                                    help="Setting this date and pressing the button, will find all invoice lines before this and set it as HMRC submitted")
    test_mode = fields.Boolean(string="HMRC Test Mode", compute='compute_test_mode')
        
    def set_hmrc_submitted(self):
        if not self.default_end_date:
            raise UserError("Set a default default end date")
        
        sql = """select distinct aml.id from account_move_line_account_tax_rel aml_rel
                    inner join account_move_line aml
                    on aml.id = aml_rel.account_move_line_id
                    inner join account_tax_smart_mtd_mtd_tag_rel taxtag
                    on taxtag.account_tax_id = aml_rel.account_tax_id
                    inner join smart_mtd_mtd_tag tag
                    on taxtag.smart_mtd_mtd_tag_id = tag.id
                    where aml.date <= '%s'
                    and tag.name ilike '%%Box%%'""" % (str(self.default_end_date))
        self.env.cr.execute(sql)
        aml_ids = [rec[0] for rec in self.env.cr.fetchall()]
        
        
        sql = """select distinct aml.id from account_move_line aml
                    inner join account_tax_smart_mtd_mtd_tag_rel taxtag
                    on aml.tax_line_id = taxtag.account_tax_id
                    inner join smart_mtd_mtd_tag tag
                    on taxtag.smart_mtd_mtd_tag_id = tag.id
                    where tax_line_id is not null and date <= '%s'
                    and tag.name ilike '%%Box%%'""" % str(self.default_end_date)
                    
        self.env.cr.execute(sql)
        tax_line_aml_ids = [rec[0] for rec in self.env.cr.fetchall()]
        
        if aml_ids or tax_line_aml_ids:
            sql = """UPDATE account_move_line SET hmrc_submitted = True, date_on_vat_return = '%s' where id in (%s) """ % (str(self.default_end_date), str(aml_ids + tax_line_aml_ids)[1:-1])
            self.env.cr.execute(sql)
        
    def create_test_obligations(self):
        self.env['l10n_uk.hmrc.send.wizard'].search([]).unlink()
        self.env['l10n_uk.vat.obligation'].search([]).unlink()
        
        #Setting up a list of obligations to be created, similar to what a API call to /organisations/vat/{vrn}/obligations returns
        #But there is no test header that allows a return of all open obligations in 2019.

        obligations = [{'start': '2019-01-01', 'end': '2019-03-31', 'due': '2019-05-07', 'status': 'O', 'periodKey': '19A1'},
                       {'start': '2019-04-01', 'end': '2019-06-30', 'due': '2019-08-07', 'status': 'O', 'periodKey': '19A2'},
                       {'start': '2019-07-01', 'end': '2019-09-30', 'due': '2019-11-07', 'status': 'O', 'periodKey': '19A3'},
                       {'start': '2019-10-01', 'end': '2019-12-31', 'due': '2020-02-07', 'status': 'O', 'periodKey': '19A4'}
                       ]
        for new_obligation in obligations:
            obligation = self.env['l10n_uk.vat.obligation'].search([('period_key', '=', new_obligation.get('periodKey')),
                                                                 ('company_id', '=', self.env.user.company_id.id)])
            status = 'open' if new_obligation['status'] == 'O' else 'fulfilled'
            if not obligation:
                self.env['l10n_uk.vat.obligation'].sudo().create({'date_start': new_obligation['start'],
                                    'date_end': new_obligation['end'],
                                    'date_received': new_obligation.get('received_date'),
                                    'date_due': new_obligation['due'],
                                    'status': status,
                                    'period_key': new_obligation['periodKey'],
                                    'company_id': self.env.user.company_id.id,
                                    })
                
    def change_to_live_mode(self):
        HmrcSvc.DEBUG = False
        HmrcSvc.HMRC_CLIENT_ID = 'GqJgi8Hal1hsEwbG6rY6i9Ag1qUa'
        HmrcSvc.PROXY_SERVER = 'https://onlinesync.odoo.com'
        
    def change_to_test_mode(self):
        HmrcSvc.DEBUG = True
        HmrcSvc.HMRC_CLIENT_ID = 'dTdANDSeX4fiw63DicmUaAVQDSMa'
        HmrcSvc.PROXY_SERVER = 'https://www.test.odoo.com'
    
    def compute_test_mode(self):
        for record in self:
            record.test_mode = HmrcSvc.DEBUG