from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_lead_type = fields.Selection(
        selection=[
            ('hot', 'Hot'),
            ('warm', 'Warm'),
            ('cold', 'Cold'),
        ],
        string='Lead Type',
        default='cold',
        tracking=True,
        help='Classify the lead based on engagement level: '
             'Hot (ready to buy), Warm (interested), Cold (early stage)',
    )
    x_next_followup_date = fields.Date(
        string='Next Follow-up Date',
        tracking=True,
        help='Scheduled date for the next follow-up with this lead',
    )

    def _get_lead_type_color(self):
        """Return kanban color index based on lead type."""
        color_map = {
            'hot': 4,      # Red
            'warm': 2,     # Orange
            'cold': 5,     # Purple
        }
        return color_map.get(self.x_lead_type, 0)

    def action_schedule_followup_activity(self):
        """Create a follow-up activity based on the next follow-up date."""
        for lead in self:
            if lead.x_next_followup_date:
                existing = lead.activity_ids.filtered(
                    lambda a: a.summary == 'Follow-up' and a.date_deadline == lead.x_next_followup_date
                )
                if not existing:
                    lead.activity_schedule(
                        'mail.mail_activity_data_todo',
                        date_deadline=lead.x_next_followup_date,
                        summary='Follow-up',
                        note=f'Scheduled follow-up for lead: {lead.name}',
                        user_id=lead.user_id.id or self.env.uid,
                    )

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        for lead in leads:
            if lead.x_next_followup_date:
                lead.action_schedule_followup_activity()
        return leads

    def write(self, vals):
        res = super().write(vals)
        if 'x_next_followup_date' in vals:
            for lead in self:
                if lead.x_next_followup_date:
                    lead.action_schedule_followup_activity()
        return res

    def _cron_followup_reminder(self):
        """Cron job to create activities for leads with upcoming follow-ups."""
        tomorrow = fields.Date.add(fields.Date.today(), days=1)
        leads = self.search([
            ('x_next_followup_date', '<=', tomorrow),
            ('x_next_followup_date', '>=', fields.Date.today()),
            ('stage_id.is_won', '=', False),
            ('active', '=', True),
        ])
        for lead in leads:
            lead.action_schedule_followup_activity()
