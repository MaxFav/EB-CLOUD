# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def get_action_context(self):
        if self.move_id:
            return {
                'default_type': self.move_id.move_type,
                'default_journal_id': self.move_id.journal_id.id,
            }
        return {}
