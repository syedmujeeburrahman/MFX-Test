{
    'name': 'CRM Lead Management',
    'version': '19.0.1.4.2',
    'summary': 'Enhanced CRM lead management with custom pipeline stages, lead classification, and advanced tracking',
    'description': """
        CRM Lead Management
        ====================
        Enhanced CRM module for structured lead management:
        - Custom pipeline stages (Prospect → Won/Lost)
        - Lead classification (Hot/Warm/Cold)
        - Next follow-up date tracking
        - Color-coded kanban view
        - Advanced filtering and search
        - Sales performance dashboard
        - Automated stage movement
        - On-demand follow-up activity scheduling (manual button only)
    """,
    'author': 'DearERP',
    'website': '',
    'category': 'Sales/CRM',
    'depends': [
        'crm',
        'sale_crm',
        'sale_management',
        'mail',
        'utm',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/utm_source_data.xml',
        'data/crm_tag_data.xml',
        'data/crm_erp_system_data.xml',
        'data/crm_contact_type_data.xml',
        'data/ir_cron_data.xml',
        'data/cleanup_automated_activities.xml',
        'views/crm_lead_filter_config_views.xml',
        'data/ir_filters_data.xml',
        'views/crm_lead_views_form.xml',
        'views/crm_lead_views_list.xml',
        'views/crm_lead_views_kanban.xml',
        'views/crm_lead_views_search.xml',
        'views/crm_lead_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'crm_lead_management/static/src/scss/lead_kanban.scss',
            'crm_lead_management/static/src/js/country_dropdown.js',
            'crm_lead_management/static/src/xml/country_dropdown.xml',
        ],
    },
    'demo': [
        'data/crm_lead_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
