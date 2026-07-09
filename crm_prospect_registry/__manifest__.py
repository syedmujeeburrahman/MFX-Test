{
    'name': 'CRM Prospect Registry & Duplicate Prevention',
    'version': '19.0.1.0.0',
    'summary': 'Pre-CRM prospect registry with duplicate detection, follow-ups, and lead conversion',
    'description': """
        Prospect Registry & Duplicate Contact Prevention
        =================================================
        Centralized CRM-only registry for contacted companies before they become leads.
        Includes duplicate detection, timeline logging, reminders, dashboard metrics,
        calendar follow-ups, audit logs, and one-click conversion to CRM leads.
    """,
    'author': 'DearERP',
    'category': 'Sales/CRM',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'mail',
        'contacts',
        'utm',
        'calendar',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/prospect_product_data.xml',
        'data/prospect_dashboard_data.xml',
        'data/ir_cron_data.xml',
        'views/prospect_product_views.xml',
        'views/prospect_activity_views.xml',
        'views/prospect_audit_log_views.xml',
        'views/prospect_duplicate_wizard_views.xml',
        'views/prospect_dashboard_views.xml',
        'views/prospect_views.xml',
        'views/crm_lead_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
