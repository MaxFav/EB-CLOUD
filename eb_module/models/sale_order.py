from odoo import models, fields, api, _

import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def confirm_and_process_to_draft(self):
        for rec in self:            
            try:
                rec.action_confirm()                
            except Exception as e:
                pass