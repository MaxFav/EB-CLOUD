from odoo import fields, models

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(selection_add=[('eur_rrp', 'EUR RRP'),('usd_rrp', 'USD RRP'),('aud_rrp', 'AUD RRP')],ondelete={'eur_rrp':'set default','usd_rrp':'set default','aud_rrp':'set default'})

    def _compute_base_price(self, product, quantity, uom, date, target_currency):

        target_currency.ensure_one()

        rule_base = self.base or 'list_price'
        
        if rule_base == "eur_rrp":
            src_currency = product.eur_id
            price = product.eur_rrp
            if src_currency != target_currency:
                price = src_currency._convert(price, target_currency, self.env.company, date, round=False)
            return price
        elif rule_base == "usd_rrp":
            src_currency = product.usd_id
            price = product.usd_rrp
            if src_currency != target_currency:
                price = src_currency._convert(price, target_currency, self.env.company, date, round=False)
            return price
        elif rule_base == "aud_rrp":
            src_currency = product.aud_id
            price = product.aud_rrp
            if src_currency != target_currency:
                price = src_currency._convert(price, target_currency, self.env.company, date, round=False)
            return price                 
        elif rule_base == "cad_rrp":
            src_currency = product.usd_id
            price = product.cad_rrp
            if src_currency != target_currency:
                price = src_currency._convert(price, target_currency, self.env.company, date, round=False)
            return price
        
        return super()._compute_base_price(product, quantity, uom, date, target_currency)