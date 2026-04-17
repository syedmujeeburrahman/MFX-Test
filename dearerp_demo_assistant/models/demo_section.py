from odoo import models, fields, api


class DearerpDemoSection(models.Model):
    _name = 'dearerp.demo.section'
    _description = 'DearERP Demo Section'
    _order = 'sequence, id'
    _inherit = ['mail.thread']

    name = fields.Char(string='Section Title', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    section_type = fields.Selection([
        ('introduction', 'Introduction'),
        ('features', 'Features & Functionalities'),
        ('comparison', 'AI Tool Comparison'),
        ('use_cases', 'Complex Use Cases'),
        ('pricing', 'Pricing & Plans'),
        ('faq', 'FAQs & Objection Handling'),
    ], string='Section Type', required=True, tracking=True)
    icon = fields.Char(string='Icon Class', default='fa-star',
                       help='Font Awesome icon class (e.g., fa-star, fa-rocket)')
    color = fields.Integer(string='Color Index', default=0)
    subtitle = fields.Char(string='Subtitle')
    description = fields.Html(string='Section Overview')
    item_ids = fields.One2many('dearerp.demo.item', 'section_id', string='Content Items')
    faq_ids = fields.One2many('dearerp.demo.faq', 'section_id', string='FAQs')
    item_count = fields.Integer(string='Items', compute='_compute_item_count')
    faq_count = fields.Integer(string='FAQs', compute='_compute_faq_count')
    active = fields.Boolean(default=True)
    cover_image = fields.Binary(string='Cover Image', attachment=True)

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    @api.depends('faq_ids')
    def _compute_faq_count(self):
        for record in self:
            record.faq_count = len(record.faq_ids)
