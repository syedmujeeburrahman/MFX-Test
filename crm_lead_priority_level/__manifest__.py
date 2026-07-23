{
    'name': 'CRM Lead Priority Level',
    'version': '19.0.1.0.0',
    'summary': 'Add lead priority levels for faster CRM follow-up',
    'description': """
        CRM Lead Priority Level
        =======================
        Adds a manual Lead Level field to CRM leads and opportunities, with
        list visibility, search filters, grouping, sorting, and a shared
        favorite for daily Level 1 follow-up.
    """,
    'author': 'DearERP',
    'website': '',
    'category': 'Sales/CRM',
    'depends': [
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_priority_level_views.xml',
        'data/ir_filters_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
