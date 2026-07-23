from odoo import fields, models


class ProspectAuditLog(models.Model):
    _name = 'x_erp.prospect_audit_log'
    _description = 'Prospect Audit Log'
    _order = 'change_date desc, id desc'

    prospect_id = fields.Many2one(
        'x_erp.prospect',
        string='Prospect',
        index=True,
        ondelete='set null',
    )
    prospect_name = fields.Char(string='Prospect Name', required=True)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
    )
    action = fields.Selection(
        [
            ('create', 'Created'),
            ('write', 'Updated'),
            ('delete', 'Deleted'),
            ('activity', 'Activity Logged'),
            ('duplicate', 'Duplicate Reviewed'),
            ('convert', 'Converted to CRM'),
        ],
        required=True,
        default='write',
        readonly=True,
    )
    change_date = fields.Datetime(
        string='Date and Time',
        default=fields.Datetime.now,
        required=True,
        readonly=True,
    )
    change_summary = fields.Html(string='Changes', readonly=True)
