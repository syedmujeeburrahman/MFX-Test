# -*- coding: utf-8 -*-
{
    'name': 'Sale Mobile & Description',
    'version': '18.0.1.1.0',
    'summary': 'Add mobile number and description fields to Sales Quotations/Orders',
    'description': """
        This module adds mobile number and description fields to Sales Quotations/Orders.
        - Mobile number is automatically fetched from the customer
        - Description field for additional notes about the quotation/order
        Both fields can be manually edited on the sales order.
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
