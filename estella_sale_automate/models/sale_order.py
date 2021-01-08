from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.commitment_date:
            invoice_vals['date_invoice'] = self.commitment_date.date()
        return invoice_vals
