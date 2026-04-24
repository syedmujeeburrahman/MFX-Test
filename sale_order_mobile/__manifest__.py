{
    'name': 'Sale Order Mobile Number',
    'version': '19.0.1.0.0',
    'summary': 'Adds a Mobile Number field on the sale order form',
    'author': 'DearERP',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale', 'sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
