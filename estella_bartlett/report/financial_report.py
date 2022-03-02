from dateutil.relativedelta import relativedelta

from odoo import models, api, fields, _
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class ReportAccountAgedReceivableByCurrency(models.AbstractModel):
    _name = "account.aged.receivable.currency"
    _description = "Aged Receivable By Currency"
    _inherit = "account.aged.partner"

    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountAgedReceivableByCurrency, self)._get_options(previous_options=previous_options)
        options['filter_account_type'] = 'receivable'
        options['by_partner_currency'] = True
        return options

    @api.model
    def _get_report_name(self):
        return _("Aged Receivable by Currency")


class ReportAccountAgedPayableByCurrency(models.AbstractModel):
    _name = "account.aged.payable.currency"
    _description = "Aged Payable By Currency"
    _inherit = "account.aged.partner"

    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountAgedPayableByCurrency, self)._get_options(previous_options=previous_options)
        options['filter_account_type'] = 'payable'
        options['by_partner_currency'] = True
        return options

    @api.model
    def _get_report_name(self):
        return _("Aged Payable by Currency")


class AccountingReport(models.AbstractModel):
    _inherit = 'account.accounting.report'

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
        ''' Inherit to show report in partner currency. '''
        ctx = self._context
        periods = {}
        date_from = fields.Date.from_string(date_from)
        start = date_from
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5 - (i + 1)) * period_length + 1) + '-' + str((5 - i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        partner_clause = ''
        cr = self.env.cr
        user_company = self.env.user.company_id
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type), date_from, date_from,)
        if ctx.get('partner_ids'):
            partner_clause = 'AND (l.partner_id IN %s)'
            arg_list += (tuple(ctx['partner_ids'].ids),)
        if ctx.get('partner_categories'):
            partner_clause += 'AND (l.partner_id IN %s)'
            partner_ids = self.env['res.partner'].search([('category_id', 'in', ctx['partner_categories'].ids)]).ids
            arg_list += (tuple(partner_ids or [0]),)
        arg_list += (date_from, tuple(company_ids))
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND (
                        l.reconciled IS FALSE
                        OR l.id IN(
                            SELECT credit_move_id FROM account_partial_reconcile where max_date > %s
                            UNION ALL
                            SELECT debit_move_id FROM account_partial_reconcile where max_date > %s
                        )
                    )
                    ''' + partner_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.date_maturity, l.date)'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0

                # Calculate line amount in line currency
                line_amount = line.amount_currency
                if self._ignore_line_amount(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount += partial_line.debit_amount_currency
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount -= partial_line.credit_amount_currency

                if not self._ignore_line_amount(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines.setdefault(partner_id, [])
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                    })
            history.append(partners_amount)

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s
                ORDER BY COALESCE(l.date_maturity, l.date)'''
        cr.execute(query, (
            tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0

            # Calculate line amount in line currency
            line_amount = line.amount_currency
            if self._ignore_line_amount(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    line_amount += partial_line.debit_amount_currency
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    line_amount -= partial_line.credit_amount_currency

            if not self._ignore_line_amount(line_amount):
                undue_amounts[partner_id] += line_amount
                lines.setdefault(partner_id, [])
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                # browse the partner name and trust field in sudo, as we may not have full access to the record (but we still have to see it in the report)
                browsed_partner = self.env['res.partner'].sudo().browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[
                                                                                              0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)

        return res, total, lines

    @api.model
    def _get_lines(self, options, line_id=None):
        if 'by_partner_currency' in options:
            sign = 1.0 if options['filter_account_type'] == 'receivable' else -1.0,
            lines = []
            account_types = [options.get('filter_account_type')]
            results, total, amls = self._get_partner_move_lines(account_types, options['date']['date_to'], 'posted', 30)
            for values in results:
                if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                    continue

                currency_id = self.env['res.partner'].browse([values['partner_id']])[
                    0].property_product_pricelist.currency_id
                vals = {
                    'id': 'partner_%s' % (values['partner_id'],),
                    'name': values['name'],
                    'level': 2,
                    'columns': [{'name': ''}] * 4 + [
                        {'name': self.amount_formatter(v, sign, currency_id),
                         'currency_id': currency_id,
                         'no_format': self.get_no_format_value(v, sign)
                         } for v in
                        [values['direction'], values['4'], values['3'], values['2'], values['1'], values['0'],
                         values['total']]
                    ],
                    'trust': values['trust'],
                    'unfoldable': True,
                    'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                }

                lines.append(vals)
                if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                    for line in amls[values['partner_id']]:
                        aml = line['line']
                        caret_type = 'account.move'
                        if aml.payment_id:
                            caret_type = 'account.payment'

                        # figure out line date
                        if caret_type == 'account.payment':
                            line_date = aml.date
                        elif caret_type == 'account.move':
                            line_date = aml.date_maturity or aml.date
                        else:
                            line_date = ''

                        if not self._context.get('no_format') and line_date:
                            line_date = format_date(self.env, line_date)
                        vals = {
                            'id': aml.id,
                            'name': aml.move_id.name,
                            'class': 'date',
                            'caret_options': caret_type,
                            'level': 4,
                            'parent_id': 'partner_%s' % (values['partner_id'],),
                            'columns': [{'name': v, 'no_format': v} for v in
                                        [line_date, aml.journal_id.code, aml.account_id.name, '']] + \
                                       [{'name': self.amount_formatter(v, sign, currency_id),
                                         'no_format': self.get_no_format_value(v, sign)} for v in
                                        [line['period'] == 6 - i and line['amount'] or '' for i in range(7)]],
                        }
                        lines.append(vals)
            return lines
        else:
            return super(AccountingReport, self)._get_lines(options, line_id)

    def amount_formatter(self, amount, sign, currency_id):
        if type(amount) == float:
            return self.format_value(amount * sign[0], currency_id)
        else:
            return amount

    def get_no_format_value(self, value, sign):
        if type(value) == str:
            return 0
        else:
            return int(value) * sign[0]

    def _ignore_line_amount(self, line_amount):
        return 0.005 > line_amount > -0.005

    def _get_cell_type_value(self, cell):
        if 'currency_id' in cell and isinstance(cell['name'], float):
            currency_id = cell['currency_id']
            return 'text', self.format_value(cell.get('name', 0), currency_id)
        return super(AccountingReport, self)._get_cell_type_value(cell)
