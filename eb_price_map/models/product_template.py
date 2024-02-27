from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    gbp_id = fields.Many2one('res.currency',string="GBP",default=lambda self: self.env.ref('base.GBP'))
    eur_id = fields.Many2one('res.currency',string="EUR",default=lambda self: self.env.ref('base.EUR'))
    usd_id = fields.Many2one('res.currency',string="USD",default=lambda self: self.env.ref('base.USD'))
    aud_id = fields.Many2one('res.currency',string="AUD",default=lambda self: self.env.ref('base.AUD'))
    cad_id = fields.Many2one('res.currency',string="CAD",default=lambda self: self.env.ref('base.CAD'))
    gbp_rrp = fields.Monetary(string="GBP RRP",currency_field="gbp_id",store=True)
    eur_rrp = fields.Monetary(string="EUR RRP",currency_field="eur_id",store=True,compute="_compute_prices")
    usd_rrp = fields.Monetary(string="USD RRP",currency_field="usd_id",store=True,compute="_compute_prices")
    aud_rrp = fields.Monetary(string="AUD RRP",currency_field="aud_id",store=True,compute="_compute_prices")
    cad_rrp = fields.Monetary(string="CAD RRP",currency_field="cad_id",store=True,compute="_compute_prices")   
    gbp_wsp = fields.Monetary(string="GBP WSP",currency_field="gbp_id",compute="_compute_prices")
    eur_wsp = fields.Monetary(string="EUR WSP",currency_field="eur_id",compute="_compute_prices")
    usd_wsp = fields.Monetary(string="USD WSP",currency_field="usd_id",compute="_compute_prices")
    aud_wsp = fields.Monetary(string="AUD WSP",currency_field="aud_id",compute="_compute_prices")
    cad_wsp = fields.Monetary(string="CAD WSP",currency_field="cad_id",compute="_compute_prices")
    price_map_id = fields.Many2one("price.map",string="Price Map Id",store=True,compute="_compute_prices")

    @api.depends("gbp_rrp")
    def _compute_prices(self):
        try:         
            self.price_map_id = self.env["price.map"].sudo().search([("gbp","=",self.gbp_rrp)])              
            self.eur_rrp = self.price_map_id.sudo().eur
            self.usd_rrp = self.price_map_id.sudo().usd
            self.aud_rrp = self.price_map_id.sudo().aud
            self.cad_rrp = self.price_map_id.sudo().cad
            self.list_price = self.gbp_rrp / 1.2
            self.gbp_wsp = self.gbp_rrp / 2.5
            self.eur_wsp = self.eur_rrp / 2.5
            self.usd_wsp = self.usd_rrp / 2.5
            self.aud_wsp = self.aud_rrp / 2.2
            self.cad_wsp = self.cad_rrp / 2.5  
        except:
            pass

    