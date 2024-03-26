{
    'name': 'EB Transfers',
    'version': '17.0',
    'license': 'LGPL-3',
    'summary': 'Estella Bartlett customisations to transfers',
    'author': 'Jamie',   
    'depends': ['base','sale_stock','stock'],
    'data': [
        'views/stock_picking_views.xml', 
        'data/stock_picking_report_eb_picking_operations.xml', 
        'data/stock_picking_reports.xml'
    ],
    'application': True, 
    'installable': True
}