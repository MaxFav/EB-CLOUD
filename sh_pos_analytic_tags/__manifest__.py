# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

{
    "name": "POS Analytic Account | POS Analytic Tags",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "summary": "Link Analytic Account Configure Analytic Account Set Analytic Tags Analytic Journal Items, Analytic Journal Entries Point Of Sale Analytic Account Point Of Sale Analytic Tags Odoo",
    "description": """This module helps to configure 'Analytic Account' & 'Analytic Tags' in the POS orders. You can set analytic account and analytic tag config wise. It automatically passes 'Analytic Account' & 'Analytic Tags' into the journal entries & journal items. You can analyze POS orders based on analytic reports.""",
    "version": "14.0.1",
    "license": "OPL-1",
    "depends": ["point_of_sale", "analytic"],
    "application": True,
    "data": [
        'views/assets.xml',
        'views/pos_session_custom.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": "20",
    "currency": "EUR"
}
