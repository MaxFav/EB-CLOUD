{
    "name": "EB Price Map",
    "version": "17.0",
    "license": "LGPL-3",
    "summary": "Adding price map model",
    "author": "Jamie",
    'category': 'Customizations',
    "application": True,
    "depends": ['base','stock','sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/price_map_view.xml'
    ],
    "installable": True
}