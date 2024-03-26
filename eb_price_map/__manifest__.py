{
    'name': 'EB Price Map',
    'version': '17.0',
    'license': 'LGPL-3',
    'summary': 'Adding price map model',
    'author': 'Jamie',
    'depends': ['base','product','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/price_map_view.xml'
    ],
    'application': True,
    'installable': True
}