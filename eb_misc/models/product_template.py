from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    packaging_image = fields.Image("Packaging Image", max_width=1920, max_height=1920)
    packaging_image_128 = fields.Image("Packaging Image 128", max_width=128, max_height=128)