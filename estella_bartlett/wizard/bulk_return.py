# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkReturn(models.TransientModel):
    _name = "bulk.return"

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    return_line_ids = fields.One2many(
        "bulk.return.line", "return_id", string="Return Lines", required=True
    )
    scrap_all = fields.Boolean(string="Scrap All")

    @api.onchange("scrap_all")
    def _onchange_scrap_all(self):
        if self.scrap_all:
            for return_line in self.return_line_ids:
                return_line.scrap_product = True

    def button_return(self):
        if not self.return_line_ids:
            raise UserError(
                _(
                    "Products must be entered into the wizard to be returned before a bulk return can be processed."
                )
            )

        error_products = []
        insufficient_qty_products = []

        matching_pickings_moves = []
        matching_sale_orders_lines = []

        for line in self.return_line_ids:
            # This search is intended to find valid stock moves that can be returned, with matching product, partner,
            # quantity, state, picking type, not being linked to an existing return, and being from an order within
            # the last 18 months.
            matching_lines = self.env["stock.move"].search(
                [
                    ("product_id", "=", line.returned_product_id.id),
                    (
                        "sale_line_id.order_id.partner_invoice_id",
                        "=",
                        self.partner_id.id,
                    ),
                    ("state", "=", "done"),
                    ("picking_type_id.code", "=", "outgoing"),
                    (
                        "sale_line_id.order_id.date_order",
                        ">=",
                        datetime.today() - relativedelta(months=18),
                    ),
                ],
                order="id desc",
            )

            # Check each matching line that it hasn't been fully-returned already.
            qty_to_return = line.quantity
            for matching_line in matching_lines:
                diff = matching_line.product_uom_qty - sum(
                    matching_line.move_dest_ids.mapped("product_uom_qty")
                )
                if qty_to_return > 0:
                    # v - If there's still product from the Bulk Wizard to return, keep going. Otherwise, append a part
                    # return and break.
                    if diff > 0:
                        if qty_to_return - matching_line.product_uom_qty >= 0:
                            # v - Search if the found move's picking is already in the results list.
                            # If so, append to that pickings entry for allowing to return multiple moves
                            # if in same picking.
                            for matching_picking in matching_pickings_moves:
                                if (
                                    matching_picking.get("picking")
                                    == matching_line.picking_id.id
                                ):
                                    matching_picking["moves"].append(
                                        {
                                            "move": matching_line.id,
                                            "sale_line": matching_line.sale_line_id.id,
                                            "scrap": line.scrap_product,
                                            "qty": diff,
                                            "product": matching_line.product_id.id,
                                            "uom": matching_line.product_uom.id,
                                        }
                                    )
                                    qty_to_return -= diff
                                    break
                            else:
                                # No move from move's picking in list yet, create new list item for the picking
                                # with the move in.
                                matching_pickings_moves.append(
                                    {
                                        "picking": matching_line.picking_id.id,
                                        "location": matching_line.location_id.id,
                                        "sale": matching_line.picking_id.sale_id.id,
                                        "moves": [
                                            {
                                                "move": matching_line.id,
                                                "sale_line": matching_line.sale_line_id.id,
                                                "scrap": line.scrap_product,
                                                "qty": diff,
                                                "product": matching_line.product_id.id,
                                                "uom": matching_line.product_uom.id,
                                            }
                                        ],
                                    }
                                )
                                qty_to_return -= diff
                            # Check to see if the sale order of the matching line has been found before.
                            # If not, create a new entry for the sale order. If so, add the matching line's sale id
                            # under the sale order.
                            for matching_sale in matching_sale_orders_lines:
                                if (
                                    matching_sale.get("sale")
                                    == matching_line.picking_id.sale_id.id
                                ):
                                    matching_sale["lines"].append(
                                        {"line": matching_line.sale_line_id.id}
                                    )
                                    break
                            else:
                                matching_sale_orders_lines.append(
                                    {
                                        "sale": matching_line.picking_id.sale_id.id,
                                        "lines": [
                                            {"line": matching_line.sale_line_id.id}
                                        ],
                                    }
                                )
                        else:
                            # The entire move can't be returned, so part of the move is being returned instead.
                            for matching_picking in matching_pickings_moves:
                                if (
                                    matching_picking.get("picking")
                                    == matching_line.picking_id.id
                                ):
                                    matching_picking["moves"].append(
                                        {
                                            "move": matching_line.id,
                                            "sale_line": matching_line.sale_line_id.id,
                                            "scrap": line.scrap_product,
                                            "qty": qty_to_return,
                                            "product": matching_line.product_id.id,
                                            "uom": matching_line.product_uom.id,
                                        }
                                    )
                                    qty_to_return -= qty_to_return
                                    # Picking found in results, move added inside it, breaking to avoid creating new
                                    # picking in results.
                                    break
                            else:
                                matching_pickings_moves.append(
                                    {
                                        "picking": matching_line.picking_id.id,
                                        "location": matching_line.location_id.id,
                                        "sale": matching_line.picking_id.sale_id.id,
                                        "moves": [
                                            {
                                                "move": matching_line.id,
                                                "sale_line": matching_line.sale_line_id.id,
                                                "scrap": line.scrap_product,
                                                "qty": qty_to_return,
                                                "product": matching_line.product_id.id,
                                                "uom": matching_line.product_uom.id,
                                            }
                                        ],
                                    }
                                )
                                qty_to_return -= qty_to_return
                            for matching_sale in matching_sale_orders_lines:
                                if (
                                    matching_sale.get("sale")
                                    == matching_line.picking_id.sale_id.id
                                ):
                                    matching_sale["lines"].append(
                                        {"line": matching_line.sale_line_id.id}
                                    )
                                    break
                            else:
                                matching_sale_orders_lines.append(
                                    {
                                        "sale": matching_line.picking_id.sale_id.id,
                                        "lines": [
                                            {"line": matching_line.sale_line_id.id}
                                        ],
                                    }
                                )
                            # All product in Bulk Return Line returned, breaking to move onto the next line in the
                            # return_line_ids.
                            break
                else:
                    break

            if qty_to_return > 0 and matching_lines:
                insufficient_qty_products.append(line.returned_product_id.name)
            if not matching_lines:
                error_products.append(line.returned_product_id.name)
                continue

        error_msg = ""
        if error_products:
            error_msg += (
                "The following product(s) cannot be found at all on previous sales within the past 18 months "
                "for this customer: "
            )
            error_prodstr = ", ".join(error_products)
            error_msg += error_prodstr + "\n"
        if insufficient_qty_products:
            error_msg += (
                "The following product(s) cannot be found with the provided quantities in previous sales "
                " within the past 18 months for this customer: "
            )
            error_prodstr = ", ".join(insufficient_qty_products)
            error_msg += error_prodstr + "\n"
        if error_products or insufficient_qty_products:
            raise UserError(error_msg)

        for picking in matching_pickings_moves:
            return_picking_wizard = (
                self.with_context(
                    active_id=picking.get("picking"), bulk_return=picking.get("moves")
                )
                .env["stock.return.picking"]
                .sudo()
                .create(
                    {
                        "location_id": picking.get("location"),
                        "original_location_id": picking.get("location"),
                        "picking_id": picking.get("picking"),
                    }
                )
            )
            for refund_line in return_picking_wizard.product_return_moves:
                refund_line.to_refund = True
            stock_return = return_picking_wizard.create_returns()

            # Browse to find the newly-created return picking and validate said stock picking
            # (and the immediate transfer when applicable).
            returned_picking = self.env["stock.picking"].browse(
                stock_return.get("res_id")
            )

            returned_picking.action_assign()
            for move in returned_picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            returned_picking._action_done()

            # Go through each line that was marked as scrap and create a new scrap record for it,
            # then validate that scrap record.
            for move in (
                scrap_move
                for scrap_move in picking.get("moves")
                if scrap_move.get("scrap") is True
            ):
                scrap_product_dict = returned_picking.button_scrap()
                if scrap_product_dict:
                    scrap_product_dict_context = scrap_product_dict.get("context")
                    scrap_product_record = (
                        self.with_context(scrap_product_dict_context)
                        .env["stock.scrap"]
                        .create(
                            {
                                "product_id": move.get("product"),
                                "scrap_qty": move.get("qty"),
                                "product_uom_id": move.get("uom"),
                                "location_id": returned_picking.location_dest_id.id
                            }
                        )
                    )
                    scrap_product_record.action_validate()

        # Creating a single credit note for each sale order line linked to the returned stock moves.
        matching_sales = self.env["sale.order"].browse(
            set([picking["sale"] for picking in matching_pickings_moves])
        )
        sale_orders_lines = []
        for picking in matching_pickings_moves:
            vals = {'sale': picking.get('sale')}
            lines = []
            for move in picking.get('moves'):
                lines.append({
                    'line': move.get("sale_line"),
                    "qty": move.get("qty")
                })
            vals['lines'] = lines
            sale_orders_lines.append(vals)
        credit_note = matching_sales.create_bulk_return_credit_note(
            final=True, lines=sale_orders_lines
        )
        return matching_sales.action_view_invoice()


class BulkReturnLine(models.TransientModel):
    _name = "bulk.return.line"

    return_id = fields.Many2one("bulk.return")
    returned_product_id = fields.Many2one(
        "product.product", string="Returned Product", required=True
    )
    quantity = fields.Float(string="Quantity", required=True)
    scrap_product = fields.Boolean(string="Scrap")

    @api.constrains("quantity")
    def validate_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise UserError(
                    _("The quantity of product returned on each line must be above 0.")
                )
