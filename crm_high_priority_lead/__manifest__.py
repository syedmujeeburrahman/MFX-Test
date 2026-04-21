{
    'name': 'CRM High-Priority Lead Management',
    'version': '19.0.1.0.0',
    'summary': 'Mark, manage, and prioritize high-priority leads with professional UI indicators',
    'description': """
        CRM High-Priority Lead Management
        ==================================
        Give critical leads the spotlight they deserve:

        * One-click toggle to mark leads as High Priority
        * Visual indicators in Kanban (ribbon + border), List (row highlight + icon), and Form (banner)
        * Dedicated "High-Priority Leads" menu and smart filter
        * Auto-highlighting rules (stale leads, high-value deals, deadlines)
        * Automatic follow-up activities for high-priority leads
        * Priority reason classification
        * Seamless integration with existing CRM pipeline
    """,
    'author': 'DearERP',
    'website': '',
    'category': 'Sales/CRM',
    'depends': [
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/crm_lead_views.xml',
        'views/crm_lead_action.xml',
        'views/crm_lead_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crm_high_priority_lead/static/src/scss/high_priority_lead.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
