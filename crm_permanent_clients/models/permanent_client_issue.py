from odoo import api, fields, models


class PermanentClientIssue(models.Model):
    _name = 'x_erp.permanent_client_issue'
    _description = 'Permanent Client Issue / Query'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_open desc, id desc'

    name = fields.Char(string='Subject', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain=[('x_is_permanent_client', '=', True)],
        ondelete='restrict',
    )
    issue_type = fields.Selection(
        [
            ('issue', 'Issue'),
            ('query', 'Query'),
            ('request', 'Feature Request'),
            ('support', 'Support'),
        ],
        string='Type',
        default='issue',
        required=True,
        tracking=True,
    )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Urgent')],
        string='Priority',
        default='1',
        tracking=True,
    )
    state = fields.Selection(
        [
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('waiting', 'Waiting on Client'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='new',
        required=True,
        tracking=True,
    )
    description = fields.Html(string='Description')
    resolution = fields.Html(string='Resolution Notes')
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        tracking=True,
    )
    date_open = fields.Datetime(
        string='Opened On',
        default=fields.Datetime.now,
        readonly=True,
    )
    date_closed = fields.Datetime(string='Closed On', readonly=True)
    tag_ids = fields.Many2many('crm.tag', string='Tags')

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_wait_client(self):
        self.write({'state': 'waiting'})

    def action_resolve(self):
        self.write({'state': 'resolved', 'date_closed': fields.Datetime.now()})

    def action_close(self):
        self.write({'state': 'closed', 'date_closed': fields.Datetime.now()})

    def action_reopen(self):
        self.write({'state': 'in_progress', 'date_closed': False})
