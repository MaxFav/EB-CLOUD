from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        # Description : Override the method to add the key value pair: 'date': the commitment_date of
        # the sale order (In all cases ? maybe add a check in the context when it is
        # called from the server (see above) ?)
        invoice_vals = super()._prepare_invoice()
        if self.commitment_date:
            invoice_vals['date_invoice'] = self.commitment_date.date()
        return invoice_vals
