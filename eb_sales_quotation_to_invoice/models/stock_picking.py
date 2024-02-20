from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sum_initial_demand = fields.Integer(compute='_compute_sum_initial_demand')
    percentage_reserved = fields.Float(compute='_compute_sum_initial_demand')

    @api.depends('move_ids_without_package')
    def _compute_sum_initial_demand(self):
        delivery_product = self.env['delivery.carrier'].search([]).mapped('product_id')
        for rec in self:
            rec.percentage_reserved = 0
            for move_id in rec.move_ids_without_package:
                if move_id.product_id not in delivery_product:
                    rec.percentage_reserved += move_id.reserved_availability
                    rec.sum_initial_demand += move_id.product_uom_qty
            if rec.sum_initial_demand:
                rec.percentage_reserved = (rec.percentage_reserved / rec.sum_initial_demand) * 100
            if rec.state == 'done':
                for move_line_ids in rec.move_ids_without_package:
                    rec.sum_initial_demand += move_line_ids.qty_done