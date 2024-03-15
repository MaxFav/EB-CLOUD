from odoo import models, fields, api, _
import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def confirm_and_process_to_draft(self):
        for sale in self:
            if sale.state not in ["sale"]:         
                sale.action_confirm()
            if sale.picking_ids:
                for picking in sale.picking_ids:               
                    for move in picking.move_ids:
                        move.quantity = move.product_uom_qty
                    picking.button_validate()
                sale._create_invoices() 

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        tz_name = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if self.commitment_date and self.env.context.get('set_quantity_done_from_cron'):
            invoice_vals['invoice_date'] = self.commitment_date.astimezone(tz_name).date()
        return invoice_vals            
    
    @api.onchange('partner_id')
    def _update_analytic_account(self):
        if self.partner_id:
            self.analytic_account_id = (self.partner_id.analytic_account_id or False)

