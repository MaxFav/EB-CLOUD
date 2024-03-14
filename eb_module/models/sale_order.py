from odoo import models, fields, api, _

import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def confirm_and_process_to_draft(self):
        for sale in self:            
            try:
                sale.action_confirm()
                for picking in sale.picking_ids:
                    picking.action_assign()              
            except Exception as e:
                pass