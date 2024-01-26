from odoo import models, fields


class SaleReport(models.Model):
    _inherit = "sale.report"

    territory = fields.Selection([("UK", "UK"), ("EU", "EU"), ("USA", "USA"), ("ROW", "ROW")])
    category = fields.Selection(
        [
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
        ]
    )

    def _select_additional_fields(self):
        fields = {"territory": "s.territory", "category": "s.category"}
        return fields
