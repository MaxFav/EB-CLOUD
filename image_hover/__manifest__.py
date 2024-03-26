{
    'name': 'Image Hover',
    'version': '1.0',
    'license': 'LGPL-3',
    'author': 'Jamie',
    'depends': ['base','website_sale','product','stock'],
    'data': ['views/products_item_view.xml'],
    'assets': {
        'web.assets_frontend': ['image_hover/static/src/css/image_hover.scss']
    },
    'installable': True
}