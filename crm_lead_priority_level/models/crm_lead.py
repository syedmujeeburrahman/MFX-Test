from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_lead_level = fields.Selection(
        selection=[
            ('1', 'Level 1 - Highest Priority / Serious Lead'),
            ('2', 'Level 2 - High Priority'),
            ('3', 'Level 3 - Medium Priority'),
            ('4', 'Level 4 - Low Priority'),
            ('5', 'Level 5 - Very Low Priority'),
        ],
        string='Lead Level',
        default='3',
        tracking=True,
        index=True,
        help='Manual priority level used to focus follow-up on the most serious leads first.',
    )
