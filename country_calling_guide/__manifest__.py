{
    'name': '195 Countries Cold Calling Guide',
    'version': '18.0.1.0.0',
    'summary': 'Cold calling guide organized by IST time slots for 195 countries',
    'description': 'Organizes 195 countries by the best IST time to call, with local times, UTC offsets and notes.',
    'author': 'DearERP',
    'category': 'Sales/CRM',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/country_calling_guide_views.xml',
        'views/country_calling_guide_menus.xml',
        'data/country_calling_guide_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
