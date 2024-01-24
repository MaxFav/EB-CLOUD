# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    sh_analytic_account = fields.Many2one(
        'account.analytic.account', string='Analytic Account', readonly=False)
    sh_analytic_tags = fields.Many2many(
        'account.analytic.tag', 'sh_analytic_tags_selection', string="Analytic Tag")

    def _create_balancing_line(self, data):
        res = super()._create_balancing_line(data)
        # set analytic account detail in move order line
        if self.move_id:
            if self.move_id.line_ids:
                for line in self.move_id.line_ids:
                    line.write({'analytic_account_id': self.sh_analytic_account,
                               'analytic_tag_ids': self.sh_analytic_tags})

        return res


class PosPaymentInherit(models.Model):
    _inherit = 'pos.payment'

    sh_analytic_account = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
    sh_analytic_tags = fields.Many2many(
        'account.analytic.tag', string="Analytic Tag")


class PosOrderInherit (models.Model):
    _inherit = 'pos.order'

    sh_pos_order_analytic_account = fields.Many2one(
        'account.analytic.account', string="Analytic Account")
    sh_pos_order_analytic_account_tags = fields.Many2many(
        'account.analytic.tag', string="Analytic Tags")

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        # pass analytic accuount data in pos order
        if res:
            if ui_order.get('sh_pos_order_analytic_account'):
                res.update({'sh_pos_order_analytic_account': ui_order.get(
                    'sh_pos_order_analytic_account')})
            if ui_order.get('sh_pos_order_analytic_account_tags'):
                res.update({'sh_pos_order_analytic_account_tags': ui_order.get(
                    'sh_pos_order_analytic_account_tags')})
        return res

    def _payment_fields(self, order, ui_paymentline):
        # pass analyic account data  in payment lines.
        res = super()._payment_fields(order, ui_paymentline)
        res['sh_analytic_account'] = ui_paymentline.get('sh_analytic_account')
        res['sh_analytic_tags'] = ui_paymentline.get('sh_analytic_tags')
        return res

    def _prepare_invoice_line(self, order_line):
        res = super()._prepare_invoice_line(order_line)
        if self.sh_pos_order_analytic_account:
            res['analytic_account_id'] = self.sh_pos_order_analytic_account
        if self.sh_pos_order_analytic_account_tags:
            res['analytic_tag_ids'] = self.sh_pos_order_analytic_account_tags.ids
        return res


class PosOrderlineInherit(models.Model):
    _inherit = 'pos.order.line'

    sh_pos_order_analytic_account = fields.Many2one(
        'account.analytic.account', string="Analytic Account")
    sh_pos_order_analytic_account_tags = fields.Many2many(
        'account.analytic.tag', string="Analytic Tags")


class Posconfiginherit(models.Model):
    _inherit = 'pos.config'

    sh_analytic_account = fields.Many2one(
        'account.analytic.account', string="Analytic Account")
    sh_analytic_account_tags = fields.Many2many(
        'account.analytic.tag', 'sh_pos_config_analytic_tags', string="Analytic Tags")

    def open_session_cb(self, check_coa=True):
        res = super().open_session_cb(check_coa)
        self.current_session_id.write(
            {'sh_analytic_account': self.sh_analytic_account, 'sh_analytic_tags': self.sh_analytic_account_tags})
        return res
