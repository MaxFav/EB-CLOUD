from odoo import models, fields, api, _

import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def confirm_and_process_to_draft(self):
        for rec in self:            
                try:
                    rec.action_confirm()
                    for picking in rec.picking_ids:
                        picking.with_context(set_quantity_done_from_cron=True).action_assign()                        
                        picking.with_context(set_quantity_done_from_cron=True).button_validate()
                    rec.with_context(set_quantity_done_from_cron=True)._create_invoices()
                except Exception as e:
                    pass