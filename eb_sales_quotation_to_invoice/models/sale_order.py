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
        for rec in self:            
            try:
                rec.action_confirm()
                for picking in rec.picking_ids:
                    picking.action_assign()
                    picking.action_set_quantities_to_reservation()
                    picking.button_validate()
                rec.with_context(set_quantity_done_from_cron=True)._create_invoices()
            except Exception as e:
                raise UserError(e) 
            
    @api.model_create_multi
    def create(self,vals_list):
        res = super().create(vals_list)
        for vals in vals_list:
            if 'analytic_account_id' not in vals:
                vals['analytic_account_id'] = (res.partner_id.analytic_account_id.id or res.partner_id.parent_id.analytic_account_id.id or False)

        return res

