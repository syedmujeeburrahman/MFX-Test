from odoo import api, models, fields


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
        """Manually create a follow-up activity based on the next follow-up date.

        Triggered explicitly by the user from the form/list button — leads
        never get an auto-scheduled activity from create/write or any cron.
        """
        for lead in self:
            if not lead.x_next_followup_date:
                continue
            existing = lead.activity_ids.filtered(
                lambda a: a.summary == 'Follow-up' and a.date_deadline == lead.x_next_followup_date
            )
            if existing:
                continue
            lead.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=lead.x_next_followup_date,
                summary='Follow-up',
                note=f'Scheduled follow-up for lead: {lead.name}',
                user_id=lead.user_id.id or self.env.uid,
            )

    @api.model
    def _dearerp_cleanup_automated_activities(self):
        """Delete every automated activity ever scheduled on a lead.

        Why: legacy crons in this and the high-priority module used to
        bulk-schedule follow-up activities daily. Those crons are now
        disabled, but the activities they already created stayed on the
        leads. This is called from a data file on every module upgrade so
        the cleanup keeps running until no stale rows remain (subsequent
        runs are no-ops).
        """
        self.env['mail.activity'].sudo().search([
            ('res_model', '=', 'crm.lead'),
            ('automated', '=', True),
        ]).unlink()
