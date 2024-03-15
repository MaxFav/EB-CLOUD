from odoo import api, fields, models, _


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)

        bulk_return_lines = self.env.context.get("bulk_return")
        if bulk_return_lines:
            # Todo: somehow only find those moves from the bulk return's list of dictionaries with lists,
            # rather than all the picking's moves. Pass move IDs and quantities over in context?
            product_return_moves_data = False
            product_return_moves = []
            line_fields = [f for f in self.env["stock.return.picking.line"]._fields.keys()]
            product_return_moves_data_tmpl = self.env["stock.return.picking.line"].default_get(
                line_fields
            )
            for move in bulk_return_lines:
                quantity = move.get("qty")
                # Todo: original calls float_round here, should I?
                product_return_moves_data = dict(product_return_moves_data_tmpl)
                product_return_moves_data.update(
                    {
                        "product_id": move.get("product"),
                        "quantity": quantity,
                        "move_id": move.get("move"),
                        "uom_id": move.get("uom"),
                    }
                )
                product_return_moves.append((0, 0, product_return_moves_data))
                if "product_return_moves" in fields:
                    res.update({"product_return_moves": product_return_moves})

        return res