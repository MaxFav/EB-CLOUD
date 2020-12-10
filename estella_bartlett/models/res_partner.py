# -*- coding: utf-8 -*-
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ResPartner(models.Model):
    _inherit = "res.partner"

    territory_id = fields.Many2one('account.analytic.account', string="Sales Channel")
    sales_channel_ids = fields.Many2many('account.analytic.tag', string="Territory")
    outstanding_purchase_order_count = fields.Integer(compute='_compute_outstanding_purchase_order_count', string='Purchase Order Count')

    @api.multi
    def schedule_meeting(self):
        partner_ids = self.ids
        partner_ids.append(self.env.user.partner_id.id)
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action['context'] = {
            'default_partner_ids': partner_ids,
        }
        return action

    @api.multi
    def _compute_outstanding_purchase_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        purchase_order_groups = self.env['purchase.order'].read_group(
            domain=[('partner_id', 'in', all_partners.ids), ('outstanding_balance', '>', 0.00), ('state', '=', 'purchase')],
            fields=['partner_id', 'outstanding_balance', 'state'], groupby=['partner_id', 'outstanding_balance', 'state']
        )
        for group in purchase_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.outstanding_purchase_order_count += group['partner_id_count']
                partner = partner.parent_id
