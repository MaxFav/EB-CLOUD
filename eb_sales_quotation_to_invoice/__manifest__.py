{
    'name': "EB Sales Quotation to Invoice",
    'version': '17.0',
    'license': "LGPL-3",
    "summary": "Sales order to invoice automation",    
    'author': "Jamie",
    'category': 'Customizations',
    "application": True, 
    'depends': ['base','account','sale','stock','sale_management','account_accountant'],
    'data': ["data/sale_order_data.xml"],
    "installable": True
}