# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64

class HmrcSendWizard(models.TransientModel):
    _inherit = 'l10n_uk.hmrc.send.wizard'
    
    submission_message = fields.Html('Submission Message')
    report_attachment_name = fields.Char(string="VAT Report Name", default='VAT Report.pdf')
    report_attachment_id = fields.Binary(string="VAT Report", readonly=True)
    
    def send(self):
        # Check correct obligation and send it to the HMRC
        res = self.obligation_id.action_submit_vat_return()
        if res:
            self.submission_message = res
            report = self.env.ref('smart_mtd.vat_return_report')
            if report:
                pdf = report.with_context(submission_msg = self.submission_message)._render_qweb_pdf([self.obligation_id.id])[0]
                pdf_file = base64.b64encode(pdf)
                self.report_attachment_name = 'VAT Return Report - ' + self.obligation_id.display_name + '.pdf'
                self.report_attachment_id = pdf_file
            #
        return {"type": "ir.actions.client",
                "tag": 'wizard_keep_open'
                }