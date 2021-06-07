from odoo import models, fields, api, _

import pytz


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        tz_name = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        if self.commitment_date and self.env.context.get('set_quantity_done_from_cron'):
            invoice_vals['date_invoice'] = self.commitment_date.astimezone(tz_name).date()
        return invoice_vals

    def confirm_and_process_to_draft(self):
        for rec in self:
            self.env.cr.execute('SAVEPOINT validate_batch_validation')
            try:
                rec.action_confirm()
                for picking in rec.picking_ids:
                    picking.action_assign()
                    picking.with_context(set_quantity_done_from_cron=True).button_validate()
                rec.with_context(set_quantity_done_from_cron=True).action_invoice_create()
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.execute('ROLLBACK TO SAVEPOINT validate_batch_validation')
