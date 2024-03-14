from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    untaxed_amount_reserved11 = fields.Float(compute='_compute_untaxed_reserved', string='Untaxed Amount Reserved', store=True)
    untaxed_amount_undelivered13 = fields.Float(compute='_compute_untaxed_undelivered', string='Untaxed Undelivered', store=True)
    quantity_reserved11 = fields.Float(compute='_compute_qty_reserved', string='Quantity Reserved', store=True)
    quantity_undelivered13 = fields.Float(compute='_compute_qty_undelivered', string='Quantity Undelivered', store=True)


    @api.depends('move_ids', 'move_ids.state', 'price_unit', 'move_ids.quantity')
    def _compute_untaxed_reserved(self):
        for line in self:
            if line.move_ids:
                for delivery in line.move_ids:
                    if delivery.state not in ['cancel', 'done']:
                        currency_rate = line.order_id.currency_rate
                        if currency_rate != 0:
                            line.untaxed_amount_reserved11 = delivery.quantity * (line.price_unit - line.price_unit * line.discount / 100) / currency_rate
                    elif delivery.state in ['cancel', 'done']:
                        line.untaxed_amount_reserved11 = 0

    @api.depends('move_ids', 'move_ids.state', 'price_unit', 'move_ids.product_uom_qty', 'move_ids.quantity')
    def _compute_untaxed_undelivered(self):
        for line in self:
            if line.move_ids:
                for delivery in line.move_ids:
                    if delivery.state not in ['cancel', 'done']:
                        currency_rate = line.order_id.currency_rate
                        if currency_rate != 0:
                            line.untaxed_amount_undelivered13 = (line.product_uom_qty - line.qty_delivered) * (line.price_unit - line.price_unit * line.discount / 100) / currency_rate
                    elif delivery.state in ['cancel', 'done']:
                        line.untaxed_amount_undelivered13 = 0


    @api.depends('move_ids', 'move_ids.state', 'move_ids.quantity')
    def _compute_qty_reserved(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done', 'draft']:
                    so_line.quantity_reserved11 = delivery.quantity
                elif so_line.move_ids and delivery.state in ['cancel', 'done', 'draft']:
                    so_line.quantity_reserved11 = 0


    @api.depends('move_ids', 'move_ids.state', 'move_ids.product_uom_qty', 'move_ids.quantity')
    def _compute_qty_undelivered(self):
        for so_line in self:
            for delivery in so_line.move_ids:
                if so_line.move_ids and delivery.state not in ['cancel', 'done', 'draft']:
                    so_line.quantity_undelivered13 = so_line.product_uom_qty - so_line.qty_delivered
                    if so_line.quantity_undelivered13 < 0:
                        so_line.quantity_undelivered13 = 0
                elif so_line.move_ids and delivery.state in ['cancel']:
                    so_line.quantity_undelivered13 = 0