from odoo import fields, models


class CrmErpSystem(models.Model):
    _name = 'x_erp.crm_erp_system'
    _description = 'CRM ERP System'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
