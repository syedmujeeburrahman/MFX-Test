# -*- coding: utf-8 -*-
{
    'name': 'Custom Lead Qualification Stages',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Custom lead qualification stages for CRM pipeline',
    'description': """
Custom Lead Qualification Stages
================================

This module replaces the default CRM stages with custom lead qualification stages:

* New Inquiry
* Contacted
* Requirement Confirmed
* Budget Approved
* Decision Maker Engaged
* Won
* Lost

These stages provide a more structured approach to qualifying and tracking leads
through the sales pipeline.
    """,
    'author': 'DearERP',
    'website': 'https://www.dearerp.com',
    'license': 'LGPL-3',
    'depends': [
        'crm',
    ],
    'data': [
        'data/crm_stage_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
