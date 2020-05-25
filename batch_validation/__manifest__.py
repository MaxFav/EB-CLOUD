# -*- coding: utf-8 -*-
{
    'name': "Estella - Success Pack - Batch validation",

    'summary': """
        Option Confirm selected quotations""",

    'description': """
        Option Confirm selected quotations
    """,

    'author': "Odoo S.A.",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'actions/sale_order.xml'
    ],
}