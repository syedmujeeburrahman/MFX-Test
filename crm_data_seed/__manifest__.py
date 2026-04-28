{
    "name": "CRM Data Seed",
    "version": "19.0.1.0.0",
    "summary": "Imports historical CRM stages, partners, and opportunities from a prior Odoo instance.",
    "description": """
CRM Data Seed
=============

One-shot data module that loads the CRM stages, partners, and opportunity
records exported from the prior production instance into this database.

The module only ships data files — no Python models or views — and uses the
existing crm, crm_lead_management, crm_high_priority_lead, and
crm_lead_contact_tracker fields and stages.
""",
    "author": "DearERP",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "sale_crm",
        "crm_lead_management",
        "crm_high_priority_lead",
        "crm_lead_contact_tracker",
    ],
    "data": [
        "data/crm_stage_data.xml",
        "data/res_partner_data.xml",
        "data/crm_lead_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
