# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import requests
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

_logger = logging.getLogger(__name__)
  
class HmrcVatObligation(models.Model):
    """ VAT obligations retrieved from HMRC """

    _inherit = 'l10n_uk.vat.obligation'
    
    def action_submit_vat_return(self):
        self.ensure_one()
        report = self.env.ref('l10n_uk_reports.financial_report_l10n_uk')[0]
        options = self.env.context.get('options')
        options.update({'date': {'date_from': self.date_start,
                                 'date_to': self.date_end}})
        report_values = report._get_lines(options)
        values = self._fetch_values_from_report(report_values)
        vat = self.env.user.company_id.vat
        res = self.env['hmrc.service']._login()
        if res: # If you can not login, return url for re-login
            return res
        headers = self._get_auth_headers(self.env.user.l10n_uk_hmrc_vat_token)
        url = self.env['hmrc.service']._get_endpoint_url('/organisations/vat/%s/returns' % vat)
        data = values.copy()
        data.update({
         'periodKey': self.period_key,
         'finalised': True
        })
        self.update_move_lines(options)
        # Need to check with which credentials it needs to be done
        r = requests.post(url, headers=headers, data=json.dumps(data))
        # Need to do something with the result?
        if r.status_code == 201: #Successful post
            #Call the function to update the move lines used in the report - to show they have been submitted
            self.update_move_lines(options)
            response = json.loads(r.content)
            msg = _('Tax return successfully posted:') + ' <br/>'
            msg += '<b>' + _('Date Processed') + ': </b>' + response['processingDate'] + '<br/>'

            if response.get('paymentIndicator'):
                msg += '<b>' + _('Payment Indicator') + ': </b>' + response['paymentIndicator'] + '<br/>'
            msg += '<b>' + _('Form Bundle Number') + ': </b>' + response['formBundleNumber'] + '<br/>'
            if response.get('chargeRefNumber'):
                msg += '<b>' + _('Charge Ref Number') + ': </b>' + response['chargeRefNumber'] + '<br/>'
            user_message = msg
            msg += '<br/>' + _('Sent Values:') + '<br/>'
            for sent_key in data:
                if sent_key != 'periodKey':
                    msg += '<b>' + sent_key + '</b>: ' + str(data[sent_key]) + '<br/>'
            self.sudo().message_post(body = msg)
            self.sudo().write({'status': "fulfilled"})    
            return user_message
        elif r.status_code == 401:  # auth issue
            _logger.exception(_("HMRC auth issue : %s"), r.content)
            raise UserError(_(
             "Sorry, your credentials were refused by HMRC or your permission grant has expired. You may try to authenticate again."))
        else:  # other issues
            _logger.exception(_("HMRC other issue : %s") % r.content)
            # even 'normal' hmrc errors have a json body. Otherwise will also raise.
            response = json.loads(r.content)
            # Recuperate error message
            if response.get('errors'):
                msgs = ""
                for err in response['errors']:
                    msgs += err.get('message', '')
            else:
                msgs = response.get('message') or response
                return msgs
            raise UserError(_("Sorry, something went wrong: %s") %  msgs)
        
    def update_move_lines(self, options):
        #Function will find the move line for each financial report line
        #and will write to the 2 fields to show it has been submitted to HMRC
        hmrc_report_domain = ['|', ('tax_line_id.include_in_vat_return', '=', True), ('tax_ids.include_in_vat_return', '=', True)]
        options['date_from'] = options['date']['date_from']
        options['date_to'] = options['date']['date_to']
        options['strict_range'] = True
        tables, where_clause, where_params = self.env['account.move.line'].with_context(options)._query_get(hmrc_report_domain)
        sql = "SELECT id FROM" + tables + " WHERE" + where_clause
        self.env.cr.execute(sql, where_params)
        results = self.env.cr.fetchall()
        if results:
            ids = list(map(lambda x: x[0], results))
            self.env['account.move.line'].browse(ids).write({'hmrc_submitted': True, 'date_on_vat_return': self.date_end})
    
    @api.model
    def retrieve_vat_obligations(self, vat, from_date, to_date, status=''):
        if from_date and to_date:
            from_date = (datetime.strptime(from_date, '%Y-%m-%d') + relativedelta(days=1)).strftime('%Y-%m-%d')
        return super(HmrcVatObligation, self).retrieve_vat_obligations(vat, from_date, to_date, status)
    
    def get_submission_data(self):
        res = self.env['hmrc.service']._login()
        if res: # If you can not login, return url for re-login
            return res
        headers = self._get_auth_headers(self.env.user.l10n_uk_hmrc_vat_token)
        if self.env.user.company_id.vat and self.period_key:
            url = self.env['hmrc.service']._get_endpoint_url('/organisations/vat/%s/returns/%s' % (self.env.user.company_id.vat, self.period_key))
            r = requests.get(url, headers=headers)        
            if r.status_code == 200: #Successful get
                return json.loads(r.content)
            else:
                return {}
        else:
            return {}
