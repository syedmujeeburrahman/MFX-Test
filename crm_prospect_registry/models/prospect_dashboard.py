from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ProspectDashboard(models.Model):
    _name = 'x_erp.prospect_dashboard'
    _description = 'Prospect Registry Dashboard'

    name = fields.Char(default='Prospect Registry Dashboard', required=True)
    total_prospects = fields.Integer(compute='_compute_metrics')
    todays_calls = fields.Integer(compute='_compute_metrics')
    todays_followups = fields.Integer(compute='_compute_metrics')
    interested_count = fields.Integer(compute='_compute_metrics')
    demo_scheduled_count = fields.Integer(compute='_compute_metrics')
    proposal_sent_count = fields.Integer(compute='_compute_metrics')
    won_count = fields.Integer(compute='_compute_metrics')
    lost_count = fields.Integer(compute='_compute_metrics')
    do_not_contact_count = fields.Integer(compute='_compute_metrics')
    duplicate_count = fields.Integer(compute='_compute_metrics')
    new_this_month_count = fields.Integer(compute='_compute_metrics')
    conversion_rate = fields.Float(compute='_compute_metrics', digits=(16, 2))

    @api.depends_context('uid')
    def _compute_metrics(self):
        Prospect = self.env['x_erp.prospect']
        Activity = self.env['x_erp.prospect_activity']
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        tomorrow = today + relativedelta(days=1)
        today_start = fields.Datetime.to_datetime(today)
        tomorrow_start = fields.Datetime.to_datetime(tomorrow)

        total = Prospect.search_count([])
        converted = Prospect.search_count([('lead_id', '!=', False)])
        for dashboard in self:
            dashboard.total_prospects = total
            dashboard.todays_calls = Activity.search_count([
                ('activity_type', '=', 'call'),
                ('activity_datetime', '>=', today_start),
                ('activity_datetime', '<', tomorrow_start),
            ])
            dashboard.todays_followups = Prospect.search_count([('next_followup_date', '=', today)])
            dashboard.interested_count = Prospect.search_count([
                ('status', 'in', ('interested', 'highly_interested')),
            ])
            dashboard.demo_scheduled_count = Prospect.search_count([('status', '=', 'demo_scheduled')])
            dashboard.proposal_sent_count = Prospect.search_count([('status', '=', 'proposal_sent')])
            dashboard.won_count = Prospect.search_count([('status', '=', 'customer')])
            dashboard.lost_count = Prospect.search_count([('status', '=', 'lost')])
            dashboard.do_not_contact_count = Prospect.search_count([('status', '=', 'do_not_contact')])
            dashboard.duplicate_count = Prospect.search_count([
                '|',
                ('status', '=', 'duplicate'),
                ('duplicate_detected', '=', True),
            ])
            dashboard.new_this_month_count = Prospect.search_count([('date_added', '>=', month_start)])
            dashboard.conversion_rate = (converted / total * 100.0) if total else 0.0

    def _prospect_action(self, name, domain):
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'x_erp.prospect',
            'view_mode': 'list,kanban,form',
            'domain': domain,
        }

    def action_total_prospects(self):
        return self._prospect_action('All Prospects', [])

    def action_todays_followups(self):
        today = fields.Date.context_today(self)
        return self._prospect_action("Today's Follow-ups", [('next_followup_date', '=', today)])

    def action_interested(self):
        return self._prospect_action('Interested Prospects', [('status', 'in', ('interested', 'highly_interested'))])

    def action_duplicates(self):
        return self._prospect_action('Duplicate Prospects', ['|', ('status', '=', 'duplicate'), ('duplicate_detected', '=', True)])
