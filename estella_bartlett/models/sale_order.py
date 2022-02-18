# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Update the following field when the partner is changed:
        - Analytic Account
        """
        super(SaleOrder, self).onchange_partner_id()

        if not self.partner_id and not self.partner_id.parent_id:
            self.update({"analytic_account_id": False})
            return

        values = {
            "analytic_account_id": self.partner_id.territory_id.id
            or self.partner_id.parent_id.territory_id.id
            or False
        }
        self.update(values)

    # If the sale order is from the website shop, set the analytic account to the partner's/partner's parent's.
    # If not from that shop, then don't.
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.website_id and not res.analytic_account_id:
            res.analytic_account_id = (
                res.partner_id.territory_id.id
                or res.partner_id.parent_id.territory_id.id
                or False
            )
        return res

    # The main difference between this and action_invoice_create is the lines parameter and the 'for sale in lines'
    # block which restricts the sale order lines that are gone through for each sale order.
    # Otherwise, other previous returned-but-unrefunded SO lines from affected SOs are involved too.

    def create_bulk_return_credit_note(self, grouped=False, final=False, lines=False):
        inv_obj = self.env["account.move"]
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        quantities = {}

        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for order in self:
            group_key = (
                order.id
                if grouped
                else (order.partner_invoice_id.id, order.currency_id.id)
            )

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            # sequence is the natural order of order_lines
            for sale in lines:
                if sale.get("sale") == order.id:
                    sale_lines = sale.get("lines")
                    sale_line_ids = []
                    sale_line_qtys = {}
                    for sale_line in sale_lines:
                        sale_line_ids.append(sale_line["line"])
                        sale_line_qtys.update({sale_line["line"]: sale_line["qty"]})

                    sale_lines_objs = self.env["sale.order.line"].browse(sale_line_ids)
                    break
            for line in sale_lines_objs:
                if line.display_type == "line_section":
                    pending_section = line
                    continue
                # if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                #     continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)

                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.invoice_origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if (
                        order.client_order_ref
                        and order.client_order_ref not in invoices_name[group_key]
                    ):
                        invoices_name[group_key].append(order.client_order_ref)

                # if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                if final:
                    if pending_section:
                        section_invoice = pending_section.invoice_line_create_vals(
                            invoices[group_key].id, pending_section.qty_to_invoice
                        )
                        inv_line_sequence += 1
                        section_invoice[0]["sequence"] = inv_line_sequence
                        line_vals_list.append(section_invoice)
                        pending_section = None
                    inv_line_sequence += 1
                    inv_line = line._prepare_invoice_line()
                    inv_line["sequence"] = inv_line_sequence
                    inv_line["move_id"] = invoices[group_key].id
                    inv_line["quantity"] = sale_line_qtys.get(line.id)
                    inv_line["account_id"] = (
                        line.product_id.property_account_income_id.id
                        or line.product_id.categ_id.property_account_income_categ_id.id
                    )
                    line_vals_list.append(inv_line)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env["account.move.line"].with_context(
                check_move_validity=False
            ).create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write(
                {
                    # "name": ", ".join(invoices_name[group_key])[:2000],
                    "invoice_origin": ", ".join(invoices_origin[group_key]),
                }
            )
            sale_orders = references[invoices[group_key]]
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': sale_orders},
                                           subtype_id=self.env.ref('mail.mt_note').id)
            if len(sale_orders) == 1:
                invoices[group_key].ref = sale_orders.reference

        if not invoices:
            raise UserError(
                _(
                    "There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered."
                )
            )

        # self._finalize_invoices(invoices, references)
        for invoice in invoices.values():
            invoice.action_switch_invoice_into_refund_credit_note()

        return [inv.id for inv in invoices.values()]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    single_analytic_tag_id = fields.Many2one(
        "account.analytic.tag",
        string="Analytic Tag",
        compute="_compute_single_analytic_tag_id",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        SaleOrder = self.env["sale.order"]
        for vals in vals_list:
            if vals.get("is_delivery") and vals.get("order_id"):
                order = SaleOrder.browse(vals["order_id"])
                if order.partner_id and order.partner_id.sales_channel_ids:
                    vals["analytic_tag_ids"] = [
                        [6, False, order.partner_id.sales_channel_ids.ids]
                    ]
                elif (
                    order.partner_id.parent_id
                    and order.partner_id.parent_id.sales_channel_ids
                ):
                    vals["analytic_tag_ids"] = [
                        [6, False, order.partner_id.parent_id.sales_channel_ids.ids]
                    ]

        return super(SaleOrderLine, self).create(vals_list)

    @api.onchange("product_id")
    def product_id_change(self):

        result = super(SaleOrderLine, self).product_id_change()

        if not self.product_id:
            return result

        vals = {}
        if self.order_id.partner_id and self.order_id.partner_id.sales_channel_ids:
            vals["analytic_tag_ids"] = self.order_id.partner_id.sales_channel_ids.ids
        elif (
            self.order_id.partner_id.parent_id
            and self.order_id.partner_id.parent_id.sales_channel_ids
        ):
            vals[
                "analytic_tag_ids"
            ] = self.order_id.partner_id.parent_id.sales_channel_ids.ids
        self.update(vals)

        return result

    @api.depends("analytic_tag_ids", "analytic_tag_ids.active")
    def _compute_single_analytic_tag_id(self):
        for line in self:
            if line.analytic_tag_ids.filtered(lambda r: r.active):
                line.single_analytic_tag_id = line.analytic_tag_ids.filtered(
                    lambda r: r.active
                )[0]
            else:
                line.single_analytic_tag_id = False

    @api.model
    def _prepare_add_missing_fields(self, values):
        # Adding analytic_tag_ids to onchange_fields to make it populate on order lines from website sale orders.
        res = {}
        onchange_fields = ["name", "price_unit", "product_uom", "tax_id", "analytic_tag_ids"]
        if values.get("order_id") and values.get("product_id") and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res
