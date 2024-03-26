{
    'name': 'EB Sales Quotation to Invoice',
    'version': '17.0',
    'license': 'LGPL-3',
    'summary': 'Sales order to invoice automation',    
    'author': 'Jamie',     
    'depends': ['base','account_accountant','sale_management','stock'],
    'data': [
        'data/sale_order_data.xml',     
    ],
    'application': True,
    'installable': True
}