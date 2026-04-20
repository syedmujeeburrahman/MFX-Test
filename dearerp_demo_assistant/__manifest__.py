# -*- coding: utf-8 -*-
{
    'name': 'DearERP Demo Assistant',
    'version': '19.0.1.0.0',
    'summary': 'Interactive demo assistant for presenting DearERP to prospects',
    'description': """
        DearERP Demo Assistant
        ======================
        A comprehensive, interactive module for demonstrating DearERP capabilities
        to prospects. Includes sections for introduction, features, comparisons,
        complex use cases, pricing plans, and FAQ/objection handling.
    """,
    'author': 'DearERP',
    'website': 'https://dearerp.com',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/demo_section_item_views.xml',
        'views/demo_section_views.xml',
        'views/menu_views.xml',
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dearerp_demo_assistant/static/src/scss/demo_assistant.scss',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
