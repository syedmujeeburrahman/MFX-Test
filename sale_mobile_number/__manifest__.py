# -*- coding: utf-8 -*-
{
    'name': 'Sale Mobile Number',
    'version': '18.0.1.0.0',
    'summary': 'Add mobile number field to Sales Orders',
    'description': """
        This module adds a mobile number field to Sales Orders.
        The mobile number is automatically fetched from the customer
        and can be manually edited on the sales order.
    """,
    'category': 'Sales/Sales',
    'author': 'DearERP',
    'website': 'https://www.dearerp.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
