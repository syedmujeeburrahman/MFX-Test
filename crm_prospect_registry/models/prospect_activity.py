from odoo import api, fields, models

from .prospect_constants import (
    CALL_RESULT_SELECTION,
    PROSPECT_ACTIVITY_TYPE_SELECTION,
    PROSPECT_STATUS_SELECTION,
)


class ProspectActivity(models.Model):
    _name = 'x_erp.prospect_activity'
    _description = 'Prospect Activity Timeline'
    _order = 'activity_datetime desc, id desc'

    name = fields.Char(string='Summary', required=True)
    prospect_id = fields.Many2one(
        'x_erp.prospect',
        string='Prospect',
        required=True,
        index=True,
        ondelete='cascade',
    )
    activity_type = fields.Selection(
        PROSPECT_ACTIVITY_TYPE_SELECTION,
        string='Activity Type',
        required=True,
        default='call',
    )
    activity_datetime = fields.Datetime(
        string='Activity Date',
        default=fields.Datetime.now,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        required=True,
    )
    call_result = fields.Selection(CALL_RESULT_SELECTION, string='Call Result')
    status_after = fields.Selection(PROSPECT_STATUS_SELECTION, string='Status After')
    next_followup_date = fields.Date(string='Next Follow-up Date')
    notes = fields.Html(string='Notes')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'x_erp_prospect_activity_attachment_rel',
        'activity_id',
        'attachment_id',
        string='Attachments',
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get('skip_prospect_activity_apply'):
            records._apply_to_prospects()
        return records

    def write(self, vals):
        return super().write(vals)

    def _apply_to_prospects(self):
        for activity in self:
            prospect = activity.prospect_id
            if not prospect:
                continue
            activity_date = fields.Date.to_date(activity.activity_datetime)
            vals = {
                'last_activity_date': activity_date,
            }
            if activity.activity_type in ('call', 'email', 'whatsapp', 'meeting', 'demo', 'proposal', 'followup'):
                vals['last_contact_date'] = activity_date
                if not prospect.first_contact_date:
                    vals['first_contact_date'] = activity_date
            if activity.activity_type == 'call':
                vals['number_of_calls'] = prospect.number_of_calls + 1
                if activity.call_result:
                    vals['call_result'] = activity.call_result
                if prospect.status == 'never_contacted':
                    vals['status'] = 'called'
            elif activity.activity_type == 'email':
                vals['number_of_emails'] = prospect.number_of_emails + 1
            elif activity.activity_type == 'whatsapp':
                vals['number_of_whatsapp_messages'] = prospect.number_of_whatsapp_messages + 1
            elif activity.activity_type in ('meeting', 'demo'):
                vals['total_meetings'] = prospect.total_meetings + 1
            elif activity.activity_type == 'proposal':
                vals['status'] = 'proposal_sent'
            if activity.status_after:
                vals['status'] = activity.status_after
            if activity.next_followup_date:
                vals['next_followup_date'] = activity.next_followup_date
            prospect.with_context(
                skip_activity_timeline=True,
                skip_prospect_activity_apply=True,
            ).write(vals)
            prospect._create_audit_log(
                'activity',
                '<p>%s</p>' % (activity.name or activity.activity_type),
            )
