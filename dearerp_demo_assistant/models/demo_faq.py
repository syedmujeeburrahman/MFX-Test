from odoo import models, fields


class DearerpDemoFaq(models.Model):
    _name = 'dearerp.demo.faq'
    _description = 'DearERP Demo FAQ'
    _order = 'sequence, id'

    name = fields.Char(string='Question', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    section_id = fields.Many2one('dearerp.demo.section', string='Section',
                                  required=True, ondelete='cascade')
    answer = fields.Html(string='Answer', sanitize_style=True, required=True)
    category = fields.Selection([
        ('general', 'General'),
        ('technical', 'Technical'),
        ('pricing', 'Pricing'),
        ('security', 'Security & Privacy'),
        ('comparison', 'Comparison'),
        ('implementation', 'Implementation'),
    ], string='Category', default='general', required=True)
    difficulty = fields.Selection([
        ('easy', 'Easy to Answer'),
        ('medium', 'Moderate'),
        ('hard', 'Tough Objection'),
    ], string='Difficulty', default='easy',
       help='How challenging this question typically is')
    suggested_response = fields.Html(string='Suggested Response Script',
                                      help='Word-for-word script for tough questions')
    active = fields.Boolean(default=True)
