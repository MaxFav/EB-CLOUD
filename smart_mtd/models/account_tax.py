# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class AccountTax(models.Model):

    _inherit = 'account.tax'
    
    include_in_vat_return = fields.Boolean(string = "Include in VAT Return"
                                           , help="If ticked, move lines associated with this tax will be included on the HMRC report to be used in a VAT Return")
    mtd_tag_ids = fields.Many2many('smart_mtd.mtd_tag', string="MTD Tags"
                                   , help="Select an MTD tag for move lines to appear in the corresponding box on the UK HMRC Report.")
    reverse_charge = fields.Boolean(string="Reverse Charge Tax", help="Tick this box if the tax is a reverse charge parent tax.")