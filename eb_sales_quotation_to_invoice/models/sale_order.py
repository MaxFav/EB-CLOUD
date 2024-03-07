from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pytz

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        tz_name = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if self.commitment_date and self.env.context.get('set_quantity_done_from_cron'):
            invoice_vals['invoice_date'] = self.commitment_date.astimezone(tz_name).date()
        return invoice_vals

    def confirm_and_process_to_draft(self):

        errors = []        
        for rec in self:            
            try:
                rec.action_confirm()
                for picking in rec.picking_ids:
                    picking.action_assign()
                    picking.with_context(set_quantity_done_from_cron=True).action_set_quantities_to_reservation()
                    picking.button_validate()
                rec.with_context(set_quantity_done_from_cron=True)._create_invoices()
            except:
                errors.append(rec.name)
                continue

        if len(errors) > 0:
            error_text:str = errors[0]
            for x in errors:
                if x in errors:
                    pass
                else:
                    error_text = error_text + "\n" + x
            raise UserError(_(f"Errors in Orders:\n" + error_text))
            
    @api.onchange('partner_id')
    def _update_analytic_account(self):
        if self.partner_id:
            self.analytic_account_id = (self.partner_id.analytic_account_id or False)

    @api.onchange('partner_id')
    def _update_warehouse(self):
        if self.partner_id and self.partner_id.warehouse_id:
            self.warehouse_id = (self.partner_id.warehouse_id or False)

        

