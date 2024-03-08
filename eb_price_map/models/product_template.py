from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    #Currency ID
    gbp_id = fields.Many2one('res.currency',string="GBP",default=lambda self: self.env.ref('base.GBP'))
    eur_id = fields.Many2one('res.currency',string="EUR",default=lambda self: self.env.ref('base.EUR'))
    usd_id = fields.Many2one('res.currency',string="USD",default=lambda self: self.env.ref('base.USD'))
    aud_id = fields.Many2one('res.currency',string="AUD",default=lambda self: self.env.ref('base.AUD'))
    cad_id = fields.Many2one('res.currency',string="CAD",default=lambda self: self.env.ref('base.CAD'))
    #RRP
    gbp_rrp = fields.Monetary(string="GBP RRP",currency_field="gbp_id",store=True)
    eur_rrp = fields.Monetary(string="EUR RRP",currency_field="eur_id",store=True,compute="_compute_prices")
    usd_rrp = fields.Monetary(string="USD RRP",currency_field="usd_id",store=True,compute="_compute_prices")
    aud_rrp = fields.Monetary(string="AUD RRP",currency_field="aud_id",store=True,compute="_compute_prices")
    cad_rrp = fields.Monetary(string="CAD RRP",currency_field="cad_id",store=True,compute="_compute_prices")
    #WSP
    gbp_wsp = fields.Monetary(string="GBP WSP",currency_field="gbp_id",store=True,compute="_compute_prices")
    #Price Map ID     
    price_map_id = fields.Many2one("price.map",string="Price Map Id",store=True,compute="_compute_prices")

    @api.depends("gbp_rrp")
    def _compute_prices(self):
        for product in self:         
            product.price_map_id = self.env["price.map"].search([("gbp","=",product.gbp_rrp)])              
            product.eur_rrp = product.price_map_id.eur
            product.usd_rrp = product.price_map_id.usd
            product.aud_rrp = product.price_map_id.aud
            product.cad_rrp = product.price_map_id.cad
            product.list_price = product.gbp_rrp / 1.2
            product.gbp_wsp = product.gbp_rrp / 2.5
           
     

    