from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    eur_id = fields.Many2one('res.currency',string="EUR",default=lambda self: self.env.ref('base.EUR'))
    usd_id = fields.Many2one('res.currency',string="USD",default=lambda self: self.env.ref('base.USD'))
    aud_id = fields.Many2one('res.currency',string="AUD",default=lambda self: self.env.ref('base.AUD'))
    cad_id = fields.Many2one('res.currency',string="CAD",default=lambda self: self.env.ref('base.CAD'))
    eur_rrp = fields.Monetary(string="EUR RRP",currency_field="eur_id",store=True,compute="_compute_prices")
    usd_rrp = fields.Monetary(string="USD RRP",currency_field="usd_id",store=True,compute="_compute_prices")
    aud_rrp = fields.Monetary(string="AUD RRP",currency_field="aud_id",store=True,compute="_compute_prices")
    cad_rrp = fields.Monetary(string="CAD RRP",currency_field="cad_id",store=True,compute="_compute_prices")
    price_map_id = fields.Many2one("price.map",string="Price Map Id",store=True,compute="_compute_prices")

    @api.depends("list_price")
    def _compute_prices(self):
        try:         
            self.price_map_id = self.env["price.map"].search([("gbp","=",self.list_price)])              
            self.eur_rrp = self.price_map_id.eur
            self.usd_rrp = self.price_map_id.usd 
            self.aud_rrp = self.price_map_id.aud
            self.cad_rrp = self.price_map_id.cad
        except:
            self.eur_rrp = 0
            self.usd_rrp = 0  
            self.aud_rrp = 0
            self.cad_rrp = 0

    