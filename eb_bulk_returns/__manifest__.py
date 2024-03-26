{
    'name': 'EB Bulk Returns',
    'version': '17.0',
    'license': 'LGPL-3',
    'summary': 'Adding bulk return wizard to inventory module',   
    'author': 'Jamie',    
    'depends': ['base','account_accountant','sale_management','stock','eb_transfers'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/bulk_return_view.xml',
    ],
    'application': True, 
    'installable': True
}