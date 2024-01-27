from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    territory_id = fields.Many2one("account.analytic.account", string="Territory")

    territory = fields.Selection(
        string="Territory", selection=[("UK", "UK"), ("EU", "EU"), ("USA", "USA"), ("ROW", "ROW")]
    )
    category = fields.Selection(
        string="Category",
        selection=[
            ("Department Store", "Department Store"),
            ("Multiple Retailer", "Multiple Retailer"),
            ("Online Retailer", "Online Retailer"),
            ("Indies", "Indies"),
            ("Travel Retail", "Travel Retail"),
            ("Websales", "Websales"),
            ("Retail", "Retail"),
            ("Concession", "Concession"),
            ("White Label", "White Label"),
            ("Discount Retailer", "Discount Retailer"),
            ("General", "General"),
        ],
    )
