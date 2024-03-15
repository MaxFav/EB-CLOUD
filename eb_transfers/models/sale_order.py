from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def _update_warehouse(self):
        if self.partner_id and self.partner_id.warehouse_id:
            self.warehouse_id = (self.partner_id.warehouse_id or False)