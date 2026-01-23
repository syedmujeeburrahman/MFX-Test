# -*- coding: utf-8 -*-
{
    'name': 'Sale & Purchase Mobile Number',
    'version': '18.0.1.2.0',
    'summary': 'Add mobile number field to Sales Quotations/Orders and RFQ/Purchase Orders',
    'description': """
        This module adds mobile number and description fields to:
        - Sales Quotations and Sales Orders
        - Request for Quotations (RFQ) and Purchase Orders

        Features:
        - Mobile number is automatically fetched from the customer/vendor
        - Description field for additional notes (on sales orders)
        - Both fields can be manually edited
        - Mobile field displayed in form and list views
    """,
    'category': 'Sales/Sales',
    'author': 'DearERP',
    'website': 'https://www.dearerp.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management',
        'purchase',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
