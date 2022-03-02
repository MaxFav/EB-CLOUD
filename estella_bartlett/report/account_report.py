# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_xlsx(self, options, response=None):
        self = self.with_context(self._set_context(options))
        return super(AccountReport, self).get_xlsx(options, response=None)
