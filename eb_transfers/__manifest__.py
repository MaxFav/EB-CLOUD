{
    'name': "EB Transfers",
    'version': '17.0',
    'license': "LGPL-3",
    "summary": "Estella Bartlett customisations to transfers",
    'author': "Jamie",
    'category': 'Customizations',
    "application": True,    
    'depends': ['base','sale','stock','sale_management'],
    'data': [
        "views/stock_picking_views.xml", 
        "data/stock_picking_eb_picking_operations.xml", 
        "data/stock_picking_reports.xml"
    ], 
    "installable": True
}