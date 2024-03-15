# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

{
    "name": "POS Analytic Account",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "summary": "Point Of Sale Analytic Account",
    "description": """This module helps to configure 'Analytic Account' & 'Analytic Tags' in the POS orders. You can set analytic account and analytic tag config wise. It automatically passes 'Analytic Account' & 'Analytic Tags' into the journal entries & journal items. You can analyze POS orders based on analytic reports.""",
    "version": "0.0.1",
    "license": "OPL-1",
    "depends": ["point_of_sale", "analytic"],
    "application": True,
    "data": [
        'views/pos_order_views.xml',
        'views/pos_payment_views.xml',
        'views/pos_session_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sh_pos_analytic_tags/static/src/overrides/models.js'
        ]
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": "20",
    "currency": "EUR"
}
