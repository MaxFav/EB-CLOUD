from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        try:
            self.ensure_one()
            if not self.env.context.get('set_quantity_done_from_cron'):
                return super().button_validate()
            # -------New instruction to set qty_done------------
            for line in self.move_ids_without_package:
                line.quantity_done = line.product_uom_qty if (line.quantity_done != line.product_uom_qty) else line.quantity_done

            return super().button_validate()
        except Exception as e:
            print(e)
            raise Exception