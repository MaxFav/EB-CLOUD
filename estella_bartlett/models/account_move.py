# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Skipping the validation if passed from the pre-payment wizard while checking the debit (although
    # it checks the credit afterwards so the transaction as a whole should still get validated).
    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self._cr.execute('''
                SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_company company ON company.id = journal.company_id
                JOIN res_currency currency ON currency.id = company.currency_id
                WHERE line.move_id IN %s
                GROUP BY line.move_id, currency.decimal_places
                HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
            ''', [tuple(self.ids)])

        res = self._cr.fetchone()
        if res and not self.env.context.get('prepayment_edit'):
            raise UserError(
                _("Cannot create unbalanced journal entry.") +
                "\n\n{}{}".format(_('Difference debit - credit: '), res[1])
            )
        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Adding the value of the debit to the displayed name in the pre-payment wizard, for ease of use.
    @api.multi
    @api.depends('ref', 'move_id', 'debit')
    def name_get(self):
        res = super(AccountMoveLine, self).name_get()
        if self.env.context.get('prepayment_wizard'):
            for num, line in enumerate(self):
                res_list = list(res[num])
                res_list[1] = res_list[1] + ", %s" % line.debit
                res[num] = tuple(res_list)
        return res
