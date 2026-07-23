from odoo import fields, models


class ProspectProduct(models.Model):
    _name = 'x_erp.prospect_product'
    _description = 'Prospect Product Interest'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
