{
    'name': 'CRM Permanent Clients',
    'version': '19.0.1.0.0',
    'summary': 'Mark partners as permanent clients and track their issues & queries',
    'description': 'Adds a Permanent Clients category under CRM with a dedicated issue tracker per client.',
    'author': 'DearERP',
    'category': 'Sales/CRM',
    'license': 'LGPL-3',
    'depends': ['crm', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/permanent_client_issue_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
