from odoo import fields, models


class CrmContactType(models.Model):
    _name = 'x_erp.crm_contact_type'
    _description = 'CRM Contact Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
