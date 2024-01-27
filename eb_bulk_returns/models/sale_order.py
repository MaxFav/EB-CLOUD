from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    user_id = fields.Many2one("res.users", domain=False)

    @api.onchange("user_id")
    def onchange_user_id_for_warehouse(self):
        # Ticket 25712: Ensure correct warehouse is set
        super(SaleOrder, self).onchange_user_id()
        if self.partner_id and self.partner_id.warehouse_id:
            self.warehouse_id = self.partner_id.warehouse_id
