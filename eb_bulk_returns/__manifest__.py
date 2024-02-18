{
    "name": "EB Bulk Returns",
    "version": "1.0",
    "summary": "Estella Bartlett Bulk Returns Module",
    "description": "Return product and create corresponding credit note",    
    "license": "LGPL-3",    
    "author": "Jamie",
    "depends": [
        "base",
        "sale",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "wizards/bulk_return_view.xml",
    ],
    "installable": True
}
