from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_is_permanent_client = fields.Boolean(
        string='Permanent Client',
        tracking=True,
        help='Mark this partner as a permanent client to track ongoing support.',
    )
    x_permanent_since = fields.Date(
        string='Client Since',
        tracking=True,
    )
    x_client_notes = fields.Text(string='Client Support Notes')
    x_client_issue_ids = fields.One2many(
        'x_erp.permanent_client_issue',
        'partner_id',
        string='Issues & Queries',
    )
    x_client_issue_count = fields.Integer(
        string='Issue Count',
        compute='_compute_x_client_issue_count',
    )
    x_client_open_issue_count = fields.Integer(
        string='Open Issues',
        compute='_compute_x_client_issue_count',
    )

    @api.depends('x_client_issue_ids', 'x_client_issue_ids.state')
    def _compute_x_client_issue_count(self):
        for partner in self:
            issues = partner.x_client_issue_ids
            partner.x_client_issue_count = len(issues)
            partner.x_client_open_issue_count = len(
                issues.filtered(lambda i: i.state not in ('resolved', 'closed'))
            )

    def action_view_client_issues(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Issues & Queries — %s' % self.name,
            'res_model': 'x_erp.permanent_client_issue',
            'view_mode': 'list,form,kanban',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
