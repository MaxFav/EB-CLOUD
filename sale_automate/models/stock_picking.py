from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate_estella(self):
        # Description : adapt from the method button_validate to force the quantity_done on the stock move to the initial
        # demand when it is not the case
        #Remove all thrown errors and returned actions linked to empty qty_done.
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        
        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)
        
        #-------New instruction to set qty_done------------
        for line in self.move_ids_without_package:
            line.quantity_done = line.product_uom_qty if (line.quantity_done != line.product_uom_qty) else line.quantity_done

 
        self.action_done()
        return
    

