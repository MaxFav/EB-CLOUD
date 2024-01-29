from odoo import api, fields, models, _


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self,fields):
        res = super(ReturnPicking, self).default_get(fields)

        return res
       