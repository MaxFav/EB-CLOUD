# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following field when the partner is changed:
        - Analytic Account
        """
        super(SaleOrder, self).onchange_partner_id()

        if not self.partner_id:
            self.update({
                'analytic_account_id': False
            })
            return

        values = {
            'analytic_account_id': self.partner_id.territory_id.id or False
        }
        self.update(values)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):

        result = super(SaleOrderLine, self).product_id_change()

        if not self.product_id:
            return result

        vals = {}
        if self.order_id.partner_id and self.order_id.partner_id.sales_channel_ids:
            vals['analytic_tag_ids'] = self.order_id.partner_id.sales_channel_ids.ids
        self.update(vals)

        return result
