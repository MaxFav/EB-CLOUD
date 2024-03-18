{
    'name': "EB Bulk Returns",
    'version': '17.0',
    'license': "LGPL-3",
    'summary': "Adding bulk return wizard to inventory module",   
    'author': "Jamie",    
    'category': 'Customizations',
    "application": True,    
    'depends': ['base','account','sale','stock','sale_management','account_accountant'],
    'data': ["security/ir.model.access.csv","wizards/bulk_return_view.xml",],
    "installable": True
}