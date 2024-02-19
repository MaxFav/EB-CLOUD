# Part of Softhealer Technologies.
# Copyright (C) Softhealer Technologies.
{
    "name": "POS Default Customer",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "summary": "Point Of Sale Default Customer",
    "description": """In some business, there are walking customers who buy small things and to manage that kind of customers order difficult and make speed slow for order processing, This module useful to set default customer or walking customer in pos. It will be the default selected customer after pos load, next order button, new order.""",
    "version": "16.0.1",
    "depends": ["point_of_sale"],
    "application": True,
    "data": [
        'views/res_config_settings.xml',
    ],
    'assets': {'point_of_sale.assets': ['sh_pos_default_customer/static/src/js/pos.js', ]},
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "price": "15",
    "currency": "EUR"
}
