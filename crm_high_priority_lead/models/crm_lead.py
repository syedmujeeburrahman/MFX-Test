from odoo import models, fields, api
from odoo.tools import float_compare


HIGH_VALUE_THRESHOLD = 10000.0
STALE_DAYS_THRESHOLD = 14
DEADLINE_DAYS_THRESHOLD = 3


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_is_high_priority = fields.Boolean(
        string='High Priority',
        default=False,
        tracking=True,
        index=True,
        help='Flag this lead as high priority for focused follow-up.',
    )
    x_high_priority_reason = fields.Selection(
        selection=[
            ('high_value', 'High Deal Value'),
            ('urgent_deadline', 'Urgent Deadline'),
            ('strategic_client', 'Strategic Client'),
            ('executive_interest', 'Executive Interest'),
            ('competitor_risk', 'Competitor Risk'),
            ('other', 'Other'),
        ],
        string='Priority Reason',
        tracking=True,
        help='Primary reason this lead is treated as high priority.',
    )
    x_high_priority_note = fields.Char(
        string='Priority Note',
        help='Short note describing why this lead is flagged as high priority.',
    )
    x_high_priority_set_on = fields.Datetime(
        string='High Priority Since',
        readonly=True,
    )
    x_high_priority_auto = fields.Boolean(
        string='Auto-Flagged Priority',
        compute='_compute_high_priority_auto',
        store=True,
        help='Automatically flagged based on rules (high value, stale, nearing deadline).',
    )
    x_high_priority_effective = fields.Boolean(
        string='Effective High Priority',
        compute='_compute_high_priority_effective',
        store=True,
        search='_search_high_priority_effective',
        help='True when the lead is manually or automatically flagged as high priority.',
    )
    x_high_priority_badge = fields.Char(
        string='Priority Badge',
        compute='_compute_high_priority_badge',
    )

    @api.depends(
        'expected_revenue',
        'date_deadline',
        'activity_ids',
        'activity_ids.date_deadline',
        'write_date',
        'stage_id',
        'stage_id.is_won',
        'active',
    )
    def _compute_high_priority_auto(self):
        today = fields.Date.today()
        for lead in self:
            if not lead.active or (lead.stage_id and lead.stage_id.is_won):
                lead.x_high_priority_auto = False
                continue
            auto = False
            if lead.expected_revenue and float_compare(
                lead.expected_revenue, HIGH_VALUE_THRESHOLD, precision_digits=2
            ) >= 0:
                auto = True
            if not auto and lead.date_deadline:
                delta = (lead.date_deadline - today).days
                if 0 <= delta <= DEADLINE_DAYS_THRESHOLD:
                    auto = True
            if not auto and not lead.activity_ids and lead.write_date:
                stale_days = (fields.Datetime.now() - lead.write_date).days
                if stale_days >= STALE_DAYS_THRESHOLD:
                    auto = True
            lead.x_high_priority_auto = auto

    @api.depends('x_is_high_priority', 'x_high_priority_auto')
    def _compute_high_priority_effective(self):
        for lead in self:
            lead.x_high_priority_effective = (
                lead.x_is_high_priority or lead.x_high_priority_auto
            )

    def _search_high_priority_effective(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            return []
        want_true = (operator == '=' and value) or (operator == '!=' and not value)
        domain = ['|', ('x_is_high_priority', '=', True), ('x_high_priority_auto', '=', True)]
        if want_true:
            return domain
        return ['&', ('x_is_high_priority', '=', False), ('x_high_priority_auto', '=', False)]

    @api.depends('x_high_priority_effective', 'x_is_high_priority', 'x_high_priority_auto')
    def _compute_high_priority_badge(self):
        for lead in self:
            if lead.x_is_high_priority:
                lead.x_high_priority_badge = 'HIGH PRIORITY'
            elif lead.x_high_priority_auto:
                lead.x_high_priority_badge = 'AUTO PRIORITY'
            else:
                lead.x_high_priority_badge = False

    def action_toggle_high_priority(self):
        """One-click toggle used by kanban/list/form buttons."""
        now = fields.Datetime.now()
        for lead in self:
            if lead.x_is_high_priority:
                lead.write({
                    'x_is_high_priority': False,
                    'x_high_priority_set_on': False,
                })
                lead.message_post(body='Removed from High Priority.')
            else:
                lead.write({
                    'x_is_high_priority': True,
                    'x_high_priority_set_on': now,
                    'priority': '3',
                })
                lead.message_post(body='Marked as High Priority.')
        return True

    def action_mark_high_priority(self):
        now = fields.Datetime.now()
        for lead in self:
            if not lead.x_is_high_priority:
                lead.write({
                    'x_is_high_priority': True,
                    'x_high_priority_set_on': now,
                    'priority': '3',
                })
                lead.message_post(body='Marked as High Priority.')
        return True

    def action_unmark_high_priority(self):
        for lead in self:
            if lead.x_is_high_priority:
                lead.write({
                    'x_is_high_priority': False,
                    'x_high_priority_set_on': False,
                })
                lead.message_post(body='Removed from High Priority.')
        return True

    def write(self, vals):
        if 'x_is_high_priority' in vals and vals.get('x_is_high_priority') and 'x_high_priority_set_on' not in vals:
            vals['x_high_priority_set_on'] = fields.Datetime.now()
        if 'x_is_high_priority' in vals and not vals.get('x_is_high_priority'):
            vals.setdefault('x_high_priority_set_on', False)
        return super().write(vals)

    def _cron_high_priority_followup(self):
        """Create a follow-up activity for every active high-priority lead missing one."""
        leads = self.search([
            ('x_high_priority_effective', '=', True),
            ('active', '=', True),
            ('stage_id.is_won', '=', False),
        ])
        today = fields.Date.today()
        for lead in leads:
            has_open = lead.activity_ids.filtered(
                lambda a: a.summary == 'High-Priority Follow-up'
            )
            if has_open:
                continue
            lead.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=today,
                summary='High-Priority Follow-up',
                note='Automatic reminder: this lead is flagged as high priority.',
                user_id=lead.user_id.id or self.env.uid,
            )
