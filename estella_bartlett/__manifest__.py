{
    "name" : "Estella Bartlett Module",
    "version" : "1.0",
    "author" : "Smart IT ltd",
    "category" : "Other",
    "summary": "Customisations for Estella Bartlett",
    'description': "",
    'maintainer': "Smart IT ltd",
    'website': 'smart-ltd.co.uk',
    'images': [],
    "depends" : ['base', 'account', 'sale', 'account_reports', 'stock'],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/account_views.xml',
        'views/general_settings_view.xml',
        'wizard/bulk_return_view.xml',
        ],
    'qweb': [],
    "auto_install": False,
    "application": False,
    "installable": True,
}