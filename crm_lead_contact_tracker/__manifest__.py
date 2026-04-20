{
    'name': 'CRM Lead Contact Tracker',
    'version': '18.0.1.0.0',
    'summary': 'Enhanced visual tracking for contacted CRM leads with daily reset and notifications',
    'description': """
        CRM Lead Contact Tracker
        =========================
        Track which CRM leads have been contacted each day with enhanced visual indicators.

        Features:
        - Mark leads as contacted with a single click
        - Auto-mark leads when scheduled activities are completed
        - Green ribbon and glow effect on contacted kanban cards
        - Green row highlighting in list view
        - Success banner on form view for contacted leads
        - Desktop notification on marking a lead as contacted
        - Chatter audit trail for all contact actions
        - Daily automatic reset via cron job
        - Search filters: Contacted Today, Pending, Contacted This Week
        - Contact counter to track total interactions
    """,
    'author': 'DearERP',
    'website': '',
    'category': 'Sales/CRM',
    'depends': ['crm', 'sale_management', 'mail', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/crm_lead_views_form.xml',
        'views/crm_lead_views_kanban.xml',
        'views/crm_lead_views_list.xml',
        'views/crm_lead_views_search.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crm_lead_contact_tracker/static/src/scss/contact_tracker.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
