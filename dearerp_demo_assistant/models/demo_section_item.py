# -*- coding: utf-8 -*-
from odoo import fields, models


class DemoSectionItem(models.Model):
    _name = 'x_demo.section.item'
    _description = 'DearERP Demo Section Item'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True)
    section_id = fields.Many2one(
        'x_demo.section', string='Section',
        required=True, ondelete='cascade',
    )
    section_type = fields.Selection(
        related='section_id.section_type', store=True, readonly=True,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    content = fields.Html(string='Content', sanitize_style=True)
    icon_class = fields.Char(
        string='Icon Class',
        help='FontAwesome icon class, e.g. fa-check',
    )
    is_highlight = fields.Boolean(
        string='Highlight',
        help='Mark as a key point to emphasize during demo',
    )
    active = fields.Boolean(string='Active', default=True)

    # Comparison-specific fields
    dearerp_rating = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('limited', 'Limited'),
        ('none', 'Not Available'),
    ], string='DearERP Rating')
    competitor_name = fields.Char(string='Competitor')
    competitor_rating = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('limited', 'Limited'),
        ('none', 'Not Available'),
    ], string='Competitor Rating')

    # Pricing-specific fields
    plan_price = fields.Char(string='Price')
    plan_period = fields.Char(string='Billing Period', default='per month')
    plan_features = fields.Html(string='Plan Features')
    is_popular = fields.Boolean(string='Most Popular')

    # FAQ-specific fields
    answer = fields.Html(string='Answer', sanitize_style=True)
    faq_category = fields.Selection([
        ('general', 'General'),
        ('technical', 'Technical'),
        ('pricing', 'Pricing'),
        ('security', 'Security'),
        ('support', 'Support'),
        ('objection', 'Objection Handling'),
    ], string='FAQ Category', default='general')
