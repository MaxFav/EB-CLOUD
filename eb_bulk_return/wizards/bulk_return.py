from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BulkReturn(models.TransientModel):
    _name = "bulk.return"

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    return_line_ids = fields.One2many(
        "bulk.return.line", "return_id", string="Return Lines", required=True
    )
    scrap_all = fields.Boolean(string="Scrap All")