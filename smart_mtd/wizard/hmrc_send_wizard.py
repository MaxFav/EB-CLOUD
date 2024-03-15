# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class HmrcSendWizard(models.TransientModel):
    _inherit = 'l10n_uk.hmrc.send.wizard'
