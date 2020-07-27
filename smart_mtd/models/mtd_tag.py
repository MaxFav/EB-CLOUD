# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class MTDTag(models.Model):
    _name = 'smart_mtd.mtd_tag'
    
    name = fields.Char(string = "Name")