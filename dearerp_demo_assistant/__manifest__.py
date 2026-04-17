{
    'name': 'DearERP Demo Assistant',
    'version': '19.0.1.0.0',
    'summary': 'Interactive demo assistant for presenting DearERP to prospects',
    'description': """
        DearERP Demo Assistant
        =======================
        A complete interactive demo tool for presenting DearERP to prospects.

        Features:
        - Introduction to DearERP
        - Features & Functionalities breakdown
        - AI Tool Comparison (Cursor, Odoo.sh AI, etc.)
        - Complex Use Cases showcase
        - Pricing & Plans details
        - FAQs & Objection Handling

        All presented in a modern, card-based UI with expandable detail views.
    """,
    'category': 'Productivity',
    'author': 'DearERP',
    'website': 'https://dearerp.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/demo_item_views.xml',
        'views/demo_faq_views.xml',
        'views/demo_section_views.xml',
        'views/menu_views.xml',
        'data/section_data.xml',
        'data/item_data.xml',
        'data/faq_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dearerp_demo_assistant/static/src/scss/demo_assistant.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
