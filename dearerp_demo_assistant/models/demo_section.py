# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DemoSection(models.Model):
    _name = 'x_demo.section'
    _description = 'DearERP Demo Section'
    _order = 'sequence, id'

    name = fields.Char(string='Section Title', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    section_type = fields.Selection([
        ('introduction', 'Introduction'),
        ('features', 'Features & Functionalities'),
        ('comparison', 'AI Tool Comparison'),
        ('use_cases', 'Complex Use Cases'),
        ('pricing', 'Pricing & Plans'),
        ('faq', 'FAQs & Objection Handling'),
    ], string='Section Type', required=True)
    subtitle = fields.Char(string='Subtitle')
    description = fields.Html(string='Description', sanitize_style=True)
    icon_class = fields.Char(
        string='Icon Class',
        help='FontAwesome icon class, e.g. fa-rocket',
    )
    color = fields.Integer(string='Color Index')
    card_color = fields.Char(
        string='Card Gradient',
        help='CSS gradient for card background',
    )
    item_ids = fields.One2many(
        'x_demo.section.item', 'section_id', string='Items',
    )
    item_count = fields.Integer(
        string='Items Count', compute='_compute_item_count',
    )
    active = fields.Boolean(string='Active', default=True)

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)
