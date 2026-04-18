from odoo import models, fields


class DearerpDemoItem(models.Model):
    _name = 'dearerp.demo.item'
    _description = 'DearERP Demo Content Item'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    section_id = fields.Many2one('dearerp.demo.section', string='Section',
                                  required=True, ondelete='cascade')
    section_type = fields.Selection(
        related='section_id.section_type',
        string='Section Type',
        store=True,
    )
    icon = fields.Char(string='Icon Class', default='fa-check-circle',
                       help='Font Awesome icon class')
    summary = fields.Text(string='Summary',
                          help='Short description shown on cards')
    content = fields.Html(string='Detailed Content',
                          help='Full content shown in expanded view')
    highlight = fields.Boolean(string='Highlight',
                                help='Mark as a key highlight point')
    badge_text = fields.Char(string='Badge Label',
                              help='Optional badge text (e.g., "New", "Popular")')
    badge_color = fields.Selection([
        ('primary', 'Blue'),
        ('success', 'Green'),
        ('warning', 'Orange'),
        ('danger', 'Red'),
        ('info', 'Cyan'),
        ('dark', 'Dark'),
    ], string='Badge Color', default='primary')
    # For comparison section
    tool_name = fields.Char(string='Tool Name',
                             help='Name of the tool being compared')
    dearerp_advantage = fields.Text(string='DearERP Advantage',
                                     help='What DearERP does better')
    # For pricing section
    price = fields.Char(string='Price Display',
                         help='Price text (e.g., "$99/month")')
    plan_features = fields.Html(string='Plan Features',
                                 help='Features included in this plan')
    is_recommended = fields.Boolean(string='Recommended Plan')
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index', default=0)

