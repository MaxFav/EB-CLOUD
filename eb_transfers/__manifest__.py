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
        "views/product_template_views.xml",
        "views/stock_picking_views.xml", 
        "data/stock_picking_report_eb_picking_operations.xml", 
        "data/stock_picking_reports.xml"
    ], 
    "installable": True
}