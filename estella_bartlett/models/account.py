# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    mandatory_analytic_account = fields.Boolean("Mandatory Analytic Account")


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for record in self.filtered(lambda l: l.move_type == "in_invoice"):
            for line in record.invoice_line_ids.filtered(
                lambda l: l.account_id and l.account_id.mandatory_analytic_account
            ):
                if not line.analytic_account_id or not line.analytic_tag_ids:
                    raise UserError(
                        _(
                            "Analytic Account or Analytic Tag not set for one or more invoice lines"
                        )
                    )

        return super(AccountMove, self).action_post()


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    mandatory_analytic_account = fields.Boolean(
        "Analytic Mandatory",
        related="account_id.mandatory_analytic_account",
        readonly=True,
    )
    single_analytic_tag_id = fields.Many2one(
        "account.analytic.tag",
        string="Analytic Tag",
        compute="_compute_single_analytic_tag_id",
        store=True,
    )

    @api.depends("analytic_tag_ids", "analytic_tag_ids.active")
    def _compute_single_analytic_tag_id(self):
        for line in self:
            if line.analytic_tag_ids.filtered(lambda r: r.active):
                line.single_analytic_tag_id = line.analytic_tag_ids.filtered(
                    lambda r: r.active
                )[0]
            else:
                line.single_analytic_tag_id = False
