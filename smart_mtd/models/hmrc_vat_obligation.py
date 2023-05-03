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

    submission_message = fields.Html('Submission Message')
    report_attachment_name = fields.Char(string="VAT Report Name", default='VAT Report.pdf')
    report_attachment_id = fields.Binary(string="VAT Report", readonly=True)

    # hard overrideen to set submitted on relevant account move lines after success, and pass through
    # filtering from report that normally gets reset to default by report._get_options()
    def action_submit_vat_return(self, data=None):
        self.ensure_one()
        report = self.env['account.generic.tax.report']
        options = report._get_options()   
        options['date'].update({'date_from': fields.Date.to_string(self.date_start),
                        'date_to': fields.Date.to_string(self.date_end),
                        'filter': 'custom',
                        'mode': 'range'})

        existing_report_options = self.env.context.get('options', False)
        if existing_report_options:
            if existing_report_options.get('unsubmitted', False):
                options['unsubmitted'] = True
            if existing_report_options.get('submitted', False):
                options['submitted'] = True

            # this one is change to OTB so its possible to submit all entries if tick 'include unposted entries'
            # not sure if this is necessary / should be done but better mataches what options are set in report
            if existing_report_options.get('all_entries', False):
                options['all_entries'] = True

        ctx = report._set_context(options)
        report_values = report.with_context(ctx)._get_lines(options)
        values = self._fetch_values_from_report(report_values)
        vat = self.env.user.company_id.vat
        res = self.env['hmrc.service']._login()
        if res: # If you can not login, return url for re-login
            return res
        headers = self._get_auth_headers(self.env.user.l10n_uk_hmrc_vat_token, data)
        url = self.env['hmrc.service']._get_endpoint_url('/organisations/vat/%s/returns' % vat)
        data = values.copy()
        data.update({
         'periodKey': self.period_key,
         'finalised': True
        })

        # Need to check with which credentials it needs to be done
        r = requests.post(url, headers=headers, data=json.dumps(data))
        # Need to do something with the result?
        if r.status_code == 201: #Successful post
            #Call the function to update the move lines used in the report - to show they have been submitted
            self.update_move_lines(options, report)

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

            report = self.env.ref('smart_mtd.vat_return_report')
            if report:
                self.sudo().write({'submission_message': user_message})
                pdf = report.with_context(submission_msg=user_message)._render_qweb_pdf(
                    [self.id])[0]
                pdf_file = base64.b64encode(pdf)
                self.sudo().write({'report_attachment_name': 'VAT Return Report - ' + self.display_name + '.pdf'})
                self.sudo().write({'report_attachment_id': pdf_file})

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
            raise UserError(_("Sorry, something went wrong: %s") % msgs)
        
    def update_move_lines(self, options, report):
        #Function will find the move line for each financial report line
        #and will write to the 2 fields to show it has been submitted to HMRC
        aml = self.env['account.move.line'].search([('id','in', report._query_get_aml_ids(options))])
        aml.write({'hmrc_submitted': True, 'date_on_vat_return': self.date_end})

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
