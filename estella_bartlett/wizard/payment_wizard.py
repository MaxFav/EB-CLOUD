from odoo import api, fields, models, _


class PaymentWizard(models.TransientModel):
    _name = 'payment.wizard'

    def _default_purchase_order_id(self):
        return self.env['purchase.order'].browse(self._context.get('active_id'))

    purchase_order_id = fields.Many2one('purchase.order', default=_default_purchase_order_id, readonly=True)
    payment_ids = fields.One2many('account.payment', related="purchase_order_id.linked_payment_ids")

    def button_save(self):
        return {'type': 'ir.actions.act_window_close'}

    def button_new_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'target': 'new',
            'context': {'source_purchase_order': self.purchase_order_id.id,
                        'new_payment_type': 'outbound',
                        'payment_partner': self.purchase_order_id.partner_id.id,
                        'new_partner_type': 'supplier',
                        'wizard_generated': True}
        }
