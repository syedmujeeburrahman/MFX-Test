from odoo import models, fields, api
from datetime import date


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_is_contacted_today = fields.Boolean(
        string='Contacted Today',
        default=False,
        tracking=True,
        help='Indicates whether this lead has been contacted or handled today.',
    )
    x_contacted_date = fields.Datetime(
        string='Last Contacted On',
        readonly=True,
        tracking=True,
        help='Date and time when this lead was last marked as contacted.',
    )
    x_contacted_by = fields.Many2one(
        'res.users',
        string='Contacted By',
        readonly=True,
        tracking=True,
        help='User who marked this lead as contacted.',
    )
    x_contacted_note = fields.Char(
        string='Contact Note',
        help='Brief note about the contact interaction.',
    )
    x_contact_count = fields.Integer(
        string='Times Contacted',
        default=0,
        readonly=True,
        help='Total number of times this lead has been marked as contacted.',
    )

    def action_mark_contacted(self):
        """Mark the lead as contacted today with a visual confirmation."""
        for lead in self:
            lead.write({
                'x_is_contacted_today': True,
                'x_contacted_date': fields.Datetime.now(),
                'x_contacted_by': self.env.uid,
                'x_contact_count': lead.x_contact_count + 1,
            })
            # Post a message in the chatter for audit trail
            lead.message_post(
                body=(
                    '<div class="o_mail_notification">'
                    '<strong>&#9989; Lead Contacted</strong><br/>'
                    'Marked as contacted by <b>%s</b>%s'
                    '</div>'
                ) % (
                    self.env.user.name,
                    (' - ' + lead.x_contacted_note) if lead.x_contacted_note else '',
                ),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            # Send a notification to the current user
            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                'simple_notification',
                {
                    'title': 'Lead Contacted!',
                    'message': '"%s" has been marked as contacted. Move on to the next lead!' % lead.name,
                    'type': 'success',
                    'sticky': False,
                },
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Lead Contacted!',
                'message': 'Lead has been marked as contacted. You can move on to the next one!',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }

    def action_unmark_contacted(self):
        """Remove the contacted marker from the lead."""
        for lead in self:
            lead.write({
                'x_is_contacted_today': False,
            })
            lead.message_post(
                body=(
                    '<div class="o_mail_notification">'
                    '<strong>&#8635; Contact Mark Removed</strong><br/>'
                    'Unmarked by <b>%s</b>'
                    '</div>'
                ) % self.env.user.name,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Mark Removed',
                'message': 'The contacted mark has been removed from this lead.',
                'type': 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }

    def _action_auto_mark_contacted(self):
        """Called when an activity is completed to auto-mark the lead."""
        for lead in self:
            if not lead.x_is_contacted_today:
                lead.action_mark_contacted()

    def activity_feedback(self, act_feedback, attachment_ids=None, subtype_xmlid=False):
        """Override to auto-mark lead as contacted when an activity is completed."""
        res = super().activity_feedback(
            act_feedback,
            attachment_ids=attachment_ids,
            subtype_xmlid=subtype_xmlid,
        )
        self._action_auto_mark_contacted()
        return res

    @api.model
    def _cron_reset_contacted_today(self):
        """Daily cron job to reset the 'Contacted Today' flag for all leads."""
        leads = self.search([('x_is_contacted_today', '=', True)])
        if leads:
            leads.write({'x_is_contacted_today': False})
