from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError



class StockPicking(models.Model):
    _inherit = "stock.picking"

    sum_initial_demand = fields.Integer(compute='_compute_sum_initial_demand')
    percentage_reserved = fields.Float(compute='_compute_sum_initial_demand')

    @api.depends('move_ids_without_package','state')
    def _compute_sum_initial_demand(self):
        for rec in self:            
            rec.sum_initial_demand = 0
            rec.percentage_reserved = 0
            if rec.state not in ["done"]:                
                for move in rec.move_ids_without_package:
                    rec.sum_initial_demand += move.product_uom_qty
                    rec.percentage_reserved += move.quantity
                rec.percentage_reserved = round(rec.percentage_reserved / rec.sum_initial_demand)                
            elif rec.state in ["done"]:
                rec.percentage_reserved = 0