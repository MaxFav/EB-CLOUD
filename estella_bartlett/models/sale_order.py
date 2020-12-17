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

    # The main difference between this and action_invoice_create is the lines parameter and the 'for sale in lines'
    # block which restricts the sale order lines that are gone through for each sale order.
    # Otherwise, other previous returned-but-unrefunded SO lines from affected SOs are involved too.
    @api.multi
    def create_bulk_return_credit_note(self, grouped=False, final=False, lines=False):
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}

        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            # sequence is the natural order of order_lines
            for sale in lines:
                if sale.get('sale') == order.id:
                    sale_lines = sale.get('lines')
                    sale_line_ids = []
                    for sale_line in sale_lines:
                        sale_line_ids.append(sale_line['line'])
                    sale_lines_objs = self.env['sale.order.line'].browse(sale_line_ids)
                    break
            for line in sale_lines_objs:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        section_invoice = pending_section.invoice_line_create_vals(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice
                        )
                        inv_line_sequence += 1
                        section_invoice[0]['sequence'] = inv_line_sequence
                        line_vals_list.extend(section_invoice)
                        pending_section = None

                    inv_line_sequence += 1
                    inv_line = line.invoice_line_create_vals(
                        invoices[group_key].id, line.qty_to_invoice
                    )
                    inv_line[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(inv_line)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key])[:2000],
                                       'origin': ', '.join(invoices_origin[group_key])})
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        self._finalize_invoices(invoices, references)
        return [inv.id for inv in invoices.values()]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    single_analytic_tag_id = fields.Many2one('account.analytic.tag', string="Analytic Tag",
                                             compute="_compute_single_analytic_tag_id", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        SaleOrder = self.env['sale.order']
        for vals in vals_list:
            if vals.get('is_delivery') and vals.get('order_id'):
                order = SaleOrder.browse(vals['order_id'])
                if order.partner_id and order.partner_id.sales_channel_ids:
                    vals['analytic_tag_ids'] = [[6, False, order.partner_id.sales_channel_ids.ids]]

        return super(SaleOrderLine, self).create(vals_list)

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

    @api.depends('analytic_tag_ids', 'analytic_tag_ids.active')
    def _compute_single_analytic_tag_id(self):
        for line in self:
            if line.analytic_tag_ids.filtered(lambda r: r.active):
                line.single_analytic_tag_id = line.analytic_tag_ids.filtered(lambda r: r.active)[0]
            else:
                line.single_analytic_tag_id = False
