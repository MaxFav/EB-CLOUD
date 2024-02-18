from odoo import models, fields

class PriceMap(models.Model):
    _name = "price.map"
    _description = "Price Map"

    gbp = fields.Float(string="GBP",store=True)
    eur = fields.Float(string="EUR",store=True)
    usd = fields.Float(string="USD",store=True)
    aud = fields.Float(string="AUD",store=True)
    