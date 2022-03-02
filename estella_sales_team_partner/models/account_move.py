# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountMove, self)._onchange_partner_id()
        if self.partner_id.team_id:
            self.team_id = self.partner_id.team_id
        if self.partner_id.user_id:
            self.invoice_user_id = self.partner_id.user_id