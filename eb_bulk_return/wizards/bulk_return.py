from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkReturn(models.TransientModel):
    _name = "bulk.return"
    _description = "Estella Bartlett Returns"

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    return_line_ids = fields.One2many(
        "bulk.return.line", "return_id", string="Return Lines", required=True
    )
    scrap_all = fields.Boolean(string="Scrap All")

class BulkReturnLine(models.TransientModel):
    _name = "bulk.return.line"
    _description = "Bulk Return Line"

    return_id = fields.Many2one("bulk.return")
    returned_product_id = fields.Many2one(
        "product.product", string="Returned Product", required=True
    )
    quantity = fields.Float(string="Quantity", required=True)
    scrap_product = fields.Boolean(string="Scrap")
