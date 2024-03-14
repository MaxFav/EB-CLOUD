from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def create_bulk_return_credit_note(self, grouped=False, final=False, lines=False):
        inv_obj = self.env["account.move"]
        precision = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        quantities = {}

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

            self.env["account.move.line"].with_context(check_move_validity=False).create(
                line_vals_list
            )

        for group_key in invoices:
            invoices[group_key].write(
                {
                    # "name": ", ".join(invoices_name[group_key])[:2000],
                    "invoice_origin": ", ".join(invoices_origin[group_key]),
                }
            )
            sale_orders = references[invoices[group_key]]
            invoice.message_post_with_view(
                "mail.message_origin_link",
                values={"self": invoice, "origin": sale_orders},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
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