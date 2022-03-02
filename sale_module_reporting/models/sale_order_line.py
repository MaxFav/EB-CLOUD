from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    untaxed_amount_reserved11 = fields.Float(compute='_compute_untaxed_reserved', string='Untaxed Amount Reserved', store=True)
    untaxed_amount_undelivered13 = fields.Float(compute='_compute_untaxed_undelivered', string='Untaxed Undelivered', store=True)
    quantity_reserved11 = fields.Float(compute='_compute_qty_reserved', string='Quantity Reserved', store=True)
    quantity_undelivered13 = fields.Float(compute='_compute_qty_undelivered', string='Quantity Undelivered', store=True)

#     @api.multi
    @api.depends('move_ids', 'move_ids.state', 'price_unit', 'move_ids.reserved_availability')
    def _compute_untaxed_reserved(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done']:
                    if so_line.order_id.date_order:
                        currency_rate = so_line.env['res.currency.rate'].search(
                            ['&', ('currency_id.name', '=', so_line.order_id.pricelist_id.currency_id.name),
                             ('name', '<=', so_line.order_id.create_date)], limit=1)
                        if currency_rate.rate != 0:
                            so_line.untaxed_amount_reserved11 = (delivery.reserved_availability * (so_line.price_unit - so_line.price_unit * so_line.discount / 100)) / currency_rate.rate
                elif so_line.move_ids and delivery.state in ['cancel', 'done']:
                    so_line.untaxed_amount_reserved11 = 0

#     @api.multi
    @api.depends('move_ids', 'move_ids.state', 'price_unit', 'move_ids.product_uom_qty', 'move_ids.quantity_done')
    def _compute_untaxed_undelivered(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done']:
                    if so_line.order_id.date_order:
                        currency_rate = so_line.env['res.currency.rate'].search(
                            ['&', ('currency_id.name', '=', so_line.order_id.pricelist_id.currency_id.name),
                             ('name', '<=', so_line.order_id.create_date)], limit=1)
                        if currency_rate.rate != 0:
                            so_line.untaxed_amount_undelivered13 = (so_line.product_uom_qty - so_line.qty_delivered) * (so_line.price_unit - so_line.price_unit * so_line.discount / 100) / currency_rate.rate
                            if so_line.untaxed_amount_undelivered13 < 0:
                                so_line.untaxed_amount_undelivered13 = 0
                elif so_line.move_ids and delivery.state in ['cancel', 'done']:
                    so_line.untaxed_amount_undelivered13 = 0

#     @api.multi
    @api.depends('move_ids', 'move_ids.state', 'move_ids.reserved_availability')
    def _compute_qty_reserved(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done']:
                    so_line.quantity_reserved11 = delivery.reserved_availability
                elif so_line.move_ids and delivery.state in ['cancel', 'done']:
                    so_line.quantity_reserved11 = 0

#     @api.multi
    @api.depends('move_ids', 'move_ids.state', 'move_ids.product_uom_qty', 'move_ids.quantity_done')
    def _compute_qty_undelivered(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done']:
                    so_line.quantity_undelivered13 = so_line.product_uom_qty - so_line.qty_delivered
                    if so_line.quantity_undelivered13 < 0:
                        so_line.quantity_undelivered13 = 0
                elif so_line.move_ids and delivery.state in ['cancel']:
                    so_line.quantity_undelivered13 = 0
