# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    sum_initial_demand = fields.Float(compute='_compute_sum_initial_demand')
    percentage_reserved = fields.Float(compute='_compute_sum_initial_demand')

    @api.depends('move_ids_without_package')
    def _compute_sum_initial_demand(self):
        delevery_product = self.env['delivery.carrier'].search([]).mapped('product_id')
        for rec in self:
            for move_id in rec.move_ids_without_package:
                if move_id.product_id not in delevery_product:
                    rec.percentage_reserved += move_id.reserved_availability
                    rec.sum_initial_demand += move_id.product_uom_qty
            if rec.sum_initial_demand:
                rec.percentage_reserved = (rec.percentage_reserved/rec.sum_initial_demand)*100
