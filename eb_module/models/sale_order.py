from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def confirm_and_process_to_draft(self):
        for sale in self:            
            try:
                sale.action_confirm()
                picking = sale.picking_ids[0]                
                for move in picking:
                    move.quantity = move.product_uom_qty
                picking.button_validate()
                sale._create_invoices()             
            except Exception as e:
                raise UserError(e)