import re

from dateutil.relativedelta import relativedelta
from markupsafe import escape

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

from .prospect_constants import (
    CALL_RESULT_SELECTION,
    PROSPECT_PRIORITY_SELECTION,
    PROSPECT_STATUS_SELECTION,
)


class Prospect(models.Model):
    _name = 'x_erp.prospect'
    _description = 'Prospect Registry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, next_followup_date asc, date_added desc, id desc'
    _rec_name = 'name'

    active = fields.Boolean(default=True)

    # Company information
    name = fields.Char(string='Company Name', required=True, tracking=True, index=True)
    website = fields.Char(tracking=True, index=True)
    industry = fields.Char(index=True)
    company_size = fields.Selection(
        [
            ('1_10', '1-10'),
            ('11_50', '11-50'),
            ('51_200', '51-200'),
            ('201_500', '201-500'),
            ('501_1000', '501-1000'),
            ('1000_plus', '1000+'),
        ],
        string='Company Size',
    )
    country_id = fields.Many2one('res.country', string='Country', index=True)
    state_id = fields.Many2one('res.country.state', string='State', index=True)
    city = fields.Char(index=True)
    street = fields.Char(string='Address')
    street2 = fields.Char(string='Address 2')
    zip = fields.Char(string='Postal Code')
    phone = fields.Char(index=True, tracking=True)
    mobile = fields.Char(index=True, tracking=True)
    email = fields.Char(index=True, tracking=True)
    linkedin = fields.Char(string='LinkedIn', index=True)
    facebook = fields.Char()
    instagram = fields.Char()
    contact_person = fields.Char(index=True, tracking=True)
    designation = fields.Char()
    company_logo = fields.Image(string='Company Logo', max_width=1024, max_height=1024)
    gst_number = fields.Char(string='GST Number', index=True, tracking=True)

    # Sales information
    user_id = fields.Many2one(
        'res.users',
        string='Assigned Salesperson',
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )
    lead_source_id = fields.Many2one('utm.source', string='Lead Source', tracking=True)
    date_added = fields.Date(default=fields.Date.context_today, required=True, tracking=True, index=True)
    first_contact_date = fields.Date(readonly=True, tracking=True)
    last_contact_date = fields.Date(readonly=True, tracking=True, index=True)
    next_followup_date = fields.Date(tracking=True, index=True)
    number_of_calls = fields.Integer(default=0, readonly=True)
    number_of_emails = fields.Integer(default=0, readonly=True)
    number_of_whatsapp_messages = fields.Integer(string='Number of WhatsApp Messages', default=0, readonly=True)
    total_meetings = fields.Integer(default=0, readonly=True)
    priority = fields.Selection(
        PROSPECT_PRIORITY_SELECTION,
        default='medium',
        required=True,
        tracking=True,
        index=True,
    )
    status = fields.Selection(
        PROSPECT_STATUS_SELECTION,
        string='Company Status',
        default='never_contacted',
        required=True,
        tracking=True,
        index=True,
    )
    call_result = fields.Selection(CALL_RESULT_SELECTION, tracking=True, index=True)
    product_interest_ids = fields.Many2many(
        'x_erp.prospect_product',
        'x_erp_prospect_product_rel',
        'prospect_id',
        'product_id',
        string='Products Interested',
    )
    tag_ids = fields.Many2many(
        'crm.tag',
        'x_erp_prospect_tag_rel',
        'prospect_id',
        'tag_id',
        string='Tags',
    )
    notes = fields.Html(string='Notes')

    # Timeline, documents, and audit
    timeline_activity_ids = fields.One2many(
        'x_erp.prospect_activity',
        'prospect_id',
        string='Activity Timeline',
    )
    activity_count = fields.Integer(compute='_compute_counts')
    last_activity_date = fields.Date(readonly=True, index=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'x_erp_prospect_attachment_rel',
        'prospect_id',
        'attachment_id',
        string='Attachments',
    )
    audit_log_ids = fields.One2many(
        'x_erp.prospect_audit_log',
        'prospect_id',
        string='Audit Logs',
        readonly=True,
    )

    # Duplicate management
    normalized_name = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_website = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_email = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_phone = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_mobile = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_gst_number = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    normalized_linkedin = fields.Char(compute='_compute_duplicate_keys', store=True, index=True)
    duplicate_prospect_ids = fields.Many2many(
        'x_erp.prospect',
        'x_erp_prospect_duplicate_rel',
        'prospect_id',
        'duplicate_id',
        string='Possible Duplicates',
        readonly=True,
    )
    duplicate_count = fields.Integer(compute='_compute_counts')
    duplicate_detected = fields.Boolean(readonly=True, tracking=True)
    duplicate_reviewed = fields.Boolean(readonly=True, copy=False)
    duplicate_warning = fields.Text(compute='_compute_duplicate_warning')

    # CRM conversion
    lead_id = fields.Many2one('crm.lead', string='CRM Lead', readonly=True, copy=False, index=True)
    lead_count = fields.Integer(compute='_compute_counts')
    followup_activity_id = fields.Many2one('mail.activity', string='Follow-up Reminder', copy=False, readonly=True)

    @api.depends(
        'name',
        'website',
        'email',
        'phone',
        'mobile',
        'gst_number',
        'linkedin',
    )
    def _compute_duplicate_keys(self):
        for prospect in self:
            prospect.normalized_name = self._normalize_text(prospect.name)
            prospect.normalized_website = self._normalize_url(prospect.website)
            prospect.normalized_email = self._normalize_text(prospect.email)
            prospect.normalized_phone = self._normalize_phone(prospect.phone)
            prospect.normalized_mobile = self._normalize_phone(prospect.mobile)
            prospect.normalized_gst_number = self._normalize_text(prospect.gst_number)
            prospect.normalized_linkedin = self._normalize_url(prospect.linkedin)

    @api.depends('timeline_activity_ids', 'duplicate_prospect_ids', 'lead_id')
    def _compute_counts(self):
        for prospect in self:
            prospect.activity_count = len(prospect.timeline_activity_ids)
            prospect.duplicate_count = len(prospect.duplicate_prospect_ids)
            prospect.lead_count = 1 if prospect.lead_id else 0

    @api.depends(
        'duplicate_prospect_ids',
        'duplicate_prospect_ids.name',
        'duplicate_prospect_ids.user_id',
        'duplicate_prospect_ids.status',
        'duplicate_prospect_ids.last_contact_date',
    )
    def _compute_duplicate_warning(self):
        for prospect in self:
            if not prospect.duplicate_prospect_ids:
                prospect.duplicate_warning = False
                continue
            first_duplicate = prospect.duplicate_prospect_ids[:1]
            prospect.duplicate_warning = prospect._format_duplicate_warning(first_duplicate)

    @api.model
    def _normalize_text(self, value):
        return re.sub(r'\s+', ' ', (value or '').strip().lower())

    @api.model
    def _normalize_phone(self, value):
        return re.sub(r'\D+', '', value or '')

    @api.model
    def _normalize_url(self, value):
        value = (value or '').strip().lower()
        value = re.sub(r'^https?://', '', value)
        value = re.sub(r'^www\.', '', value)
        return value.rstrip('/')

    def _duplicate_terms(self):
        self.ensure_one()
        terms = []
        if self.normalized_name:
            terms.append(('normalized_name', '=', self.normalized_name))
        if self.normalized_website:
            terms.append(('normalized_website', '=', self.normalized_website))
        if self.normalized_email:
            terms.append(('normalized_email', '=', self.normalized_email))
        for phone_key in set(filter(None, [self.normalized_phone, self.normalized_mobile])):
            terms.append(('normalized_phone', '=', phone_key))
            terms.append(('normalized_mobile', '=', phone_key))
        if self.normalized_gst_number:
            terms.append(('normalized_gst_number', '=', self.normalized_gst_number))
        if self.normalized_linkedin:
            terms.append(('normalized_linkedin', '=', self.normalized_linkedin))
        return terms

    def _duplicate_domain(self):
        self.ensure_one()
        terms = self._duplicate_terms()
        if not terms:
            return [('id', '=', 0)]
        domain = expression.OR([[term] for term in terms])
        if isinstance(self.id, int):
            domain = expression.AND([domain, [('id', '!=', self.id)]])
        return domain

    def _find_duplicates(self, limit=20):
        self.ensure_one()
        return self.search(self._duplicate_domain(), limit=limit)

    def _refresh_duplicate_links(self):
        for prospect in self:
            old_duplicate_ids = set(prospect.duplicate_prospect_ids.ids)
            duplicates = prospect._find_duplicates(limit=50)
            new_duplicate_ids = set(duplicates.ids)
            prospect.with_context(
                skip_duplicate_refresh=True,
                skip_audit_log=True,
                skip_activity_timeline=True,
            ).write({
                'duplicate_prospect_ids': [(6, 0, duplicates.ids)],
                'duplicate_detected': bool(duplicates),
                'duplicate_reviewed': prospect.duplicate_reviewed if duplicates else False,
            })
            if duplicates and old_duplicate_ids != new_duplicate_ids:
                prospect.message_post(body='<p>%s</p>' % escape(prospect._format_duplicate_warning(duplicates[:1])))

    def _format_duplicate_warning(self, duplicate):
        self.ensure_one()
        status_label = dict(PROSPECT_STATUS_SELECTION).get(duplicate.status, duplicate.status or '')
        salesperson = duplicate.user_id.name or '-'
        last_contact = duplicate.last_contact_date or '-'
        return _(
            'Company Already Exists\n'
            'Company: %(company)s\n'
            'Salesperson: %(salesperson)s\n'
            'Current Status: %(status)s\n'
            'Last Contact: %(last_contact)s'
        ) % {
            'company': duplicate.name,
            'salesperson': salesperson,
            'status': status_label,
            'last_contact': last_contact,
        }

    @api.onchange('name', 'website', 'email', 'phone', 'mobile', 'gst_number', 'linkedin')
    def _onchange_duplicate_keys(self):
        for prospect in self:
            if not any([
                prospect.name,
                prospect.website,
                prospect.email,
                prospect.phone,
                prospect.mobile,
                prospect.gst_number,
                prospect.linkedin,
            ]):
                continue
            duplicates = prospect._find_duplicates(limit=5)
            prospect.duplicate_prospect_ids = [(6, 0, duplicates.ids)]
            prospect.duplicate_detected = bool(duplicates)
            if duplicates:
                return {
                    'warning': {
                        'title': _('Company Already Exists'),
                        'message': prospect._format_duplicate_warning(duplicates[:1]),
                    },
                }
        return {}

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._create_audit_log('create', '<p>Prospect created.</p>')
        records._refresh_duplicate_links()
        records._sync_followup_activity()
        return records

    def write(self, vals):
        audited_names = self._audited_field_names(vals)
        before = {record.id: record._audit_snapshot(audited_names) for record in self}
        previous_status = {record.id: record.status for record in self}
        result = super().write(vals)

        if not self.env.context.get('skip_audit_log') and audited_names:
            for record in self:
                summary = record._format_audit_changes(before.get(record.id, {}), audited_names)
                if summary:
                    record._create_audit_log('write', summary)

        duplicate_fields = {'name', 'website', 'email', 'phone', 'mobile', 'gst_number', 'linkedin'}
        if duplicate_fields.intersection(vals) and not self.env.context.get('skip_duplicate_refresh'):
            self._refresh_duplicate_links()

        if {'next_followup_date', 'user_id', 'name'}.intersection(vals) and not self.env.context.get('skip_followup_sync'):
            self._sync_followup_activity()

        if 'status' in vals and not self.env.context.get('skip_activity_timeline'):
            for record in self:
                if previous_status.get(record.id) != record.status:
                    status_label = dict(PROSPECT_STATUS_SELECTION).get(record.status, record.status)
                    self.env['x_erp.prospect_activity'].with_context(skip_prospect_activity_apply=True).create({
                        'prospect_id': record.id,
                        'activity_type': 'status_change',
                        'name': _('Status changed to %s') % status_label,
                        'status_after': record.status,
                        'user_id': self.env.user.id,
                    })
        return result

    def unlink(self):
        for record in self:
            record._create_audit_log('delete', '<p>Prospect deleted.</p>')
        return super().unlink()

    def _audited_field_names(self, vals):
        excluded = {
            'normalized_name',
            'normalized_website',
            'normalized_email',
            'normalized_phone',
            'normalized_mobile',
            'normalized_gst_number',
            'normalized_linkedin',
            'duplicate_prospect_ids',
            'duplicate_detected',
            'duplicate_warning',
            'followup_activity_id',
            'last_activity_date',
        }
        return [name for name in vals if name in self._fields and name not in excluded]

    def _audit_snapshot(self, field_names):
        self.ensure_one()
        return {name: self._display_field_value(name) for name in field_names}

    def _display_field_value(self, field_name):
        self.ensure_one()
        field = self._fields[field_name]
        value = self[field_name]
        if field.type == 'many2one':
            return value.display_name if value else ''
        if field.type in ('many2many', 'one2many'):
            return ', '.join(value.mapped('display_name')[:20])
        if field.type == 'selection':
            selection = field.selection
            if callable(selection):
                selection = selection(self)
            return dict(selection).get(value, value or '')
        if field.type == 'html':
            return _('Updated') if value else ''
        return value or ''

    def _format_audit_changes(self, before, field_names):
        self.ensure_one()
        items = []
        for name in field_names:
            old_value = before.get(name, '')
            new_value = self._display_field_value(name)
            if old_value == new_value:
                continue
            label = self._fields[name].string
            items.append(
                '<li><b>%s</b>: %s -> %s</li>' % (
                    escape(label),
                    escape(str(old_value or '')),
                    escape(str(new_value or '')),
                )
            )
        return '<ul>%s</ul>' % ''.join(items) if items else False

    def _create_audit_log(self, action, summary):
        Audit = self.env['x_erp.prospect_audit_log'].sudo()
        for record in self:
            Audit.create({
                'prospect_id': record.id if record.exists() else False,
                'prospect_name': record.display_name or record.name or _('Deleted Prospect'),
                'user_id': self.env.user.id,
                'action': action,
                'change_summary': summary,
            })

    def _sync_followup_activity(self):
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        model_id = self.env['ir.model']._get_id(self._name)
        for prospect in self:
            if not prospect.exists():
                continue
            if not prospect.next_followup_date:
                if prospect.followup_activity_id and prospect.followup_activity_id.exists():
                    prospect.followup_activity_id.unlink()
                prospect.with_context(skip_audit_log=True, skip_followup_sync=True).write({'followup_activity_id': False})
                continue
            vals = {
                'res_model_id': model_id,
                'res_id': prospect.id,
                'activity_type_id': activity_type.id,
                'summary': _('Prospect follow-up: %s') % prospect.name,
                'date_deadline': prospect.next_followup_date,
                'user_id': prospect.user_id.id or self.env.user.id,
                'note': prospect.notes or '',
            }
            if prospect.followup_activity_id and prospect.followup_activity_id.exists():
                prospect.followup_activity_id.write(vals)
            else:
                activity = self.env['mail.activity'].create(vals)
                prospect.with_context(skip_audit_log=True, skip_followup_sync=True).write({
                    'followup_activity_id': activity.id,
                })

    def _ensure_mail_activity(self, summary, deadline, note=False):
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return False
        model_id = self.env['ir.model']._get_id(self._name)
        for prospect in self:
            existing = self.env['mail.activity'].search([
                ('res_model_id', '=', model_id),
                ('res_id', '=', prospect.id),
                ('summary', '=', summary),
            ], limit=1)
            if existing:
                continue
            self.env['mail.activity'].create({
                'res_model_id': model_id,
                'res_id': prospect.id,
                'activity_type_id': activity_type.id,
                'summary': summary,
                'date_deadline': deadline,
                'user_id': prospect.user_id.id or self.env.user.id,
                'note': note or summary,
            })
        return True

    @api.model
    def _cron_create_reminders(self):
        today = fields.Date.context_today(self)
        inactive_statuses = ('customer', 'lost', 'do_not_contact', 'duplicate')
        followup_domain = [
            ('active', '=', True),
            ('status', 'not in', inactive_statuses),
            ('next_followup_date', '<=', today),
        ]
        self.search(followup_domain, limit=1000)._sync_followup_activity()

        no_activity_cutoff = today - relativedelta(days=30)
        no_activity_domain = [
            ('active', '=', True),
            ('status', 'not in', inactive_statuses),
            '|',
            ('last_activity_date', '=', False),
            ('last_activity_date', '<', no_activity_cutoff),
        ]
        self.search(no_activity_domain, limit=1000)._ensure_mail_activity(
            _('No Activity for 30 Days'),
            today,
            _('This prospect has had no recorded activity for 30 days.'),
        )

        proposal_domain = [
            ('active', '=', True),
            ('status', '=', 'proposal_sent'),
            '|',
            ('next_followup_date', '=', False),
            ('next_followup_date', '<=', today),
        ]
        self.search(proposal_domain, limit=1000)._ensure_mail_activity(
            _('Proposal Pending'),
            today,
            _('Follow up on the pending proposal.'),
        )

    def _open_activity_form(self, activity_type, summary):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': summary,
            'res_model': 'x_erp.prospect_activity',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_prospect_id': self.id,
                'default_activity_type': activity_type,
                'default_name': summary,
                'default_user_id': self.env.user.id,
            },
        }

    def action_log_call(self):
        return self._open_activity_form('call', _('Log Call'))

    def action_log_email(self):
        return self._open_activity_form('email', _('Log Email'))

    def action_log_whatsapp(self):
        return self._open_activity_form('whatsapp', _('Log WhatsApp'))

    def action_schedule_followup(self):
        return self._open_activity_form('followup', _('Schedule Follow-up'))

    def action_log_meeting(self):
        return self._open_activity_form('meeting', _('Log Meeting'))

    def action_check_duplicates(self):
        self.ensure_one()
        duplicates = self._find_duplicates(limit=20)
        self.with_context(skip_duplicate_refresh=True, skip_audit_log=True).write({
            'duplicate_prospect_ids': [(6, 0, duplicates.ids)],
            'duplicate_detected': bool(duplicates),
        })
        if not duplicates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Duplicate Found'),
                    'message': _('No matching prospect was found.'),
                    'type': 'success',
                    'sticky': False,
                },
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Company Already Exists'),
            'res_model': 'x_erp.prospect_duplicate_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_prospect_id': self.id,
                'default_duplicate_id': duplicates[0].id,
            },
        }

    def action_view_duplicates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Possible Duplicates'),
            'res_model': 'x_erp.prospect',
            'view_mode': 'list,kanban,form',
            'domain': [('id', 'in', self.duplicate_prospect_ids.ids)],
        }

    def action_view_activities(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Prospect Timeline'),
            'res_model': 'x_erp.prospect_activity',
            'view_mode': 'list,form,calendar',
            'domain': [('prospect_id', '=', self.id)],
            'context': {'default_prospect_id': self.id},
        }

    def action_view_lead(self):
        self.ensure_one()
        if not self.lead_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('CRM Lead'),
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': self.lead_id.id,
        }

    def action_convert_to_crm_lead(self):
        self.ensure_one()
        lead = self._convert_to_crm_lead()
        return {
            'type': 'ir.actions.act_window',
            'name': _('CRM Lead'),
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'res_id': lead.id,
        }

    def _convert_to_crm_lead(self):
        self.ensure_one()
        if self.lead_id:
            return self.lead_id
        lead_model = self.env['crm.lead']
        lead_fields = lead_model._fields
        timeline = ''.join(
            '<li>%s - %s</li>' % (
                escape(fields.Datetime.to_string(activity.activity_datetime)),
                escape(activity.name),
            )
            for activity in self.timeline_activity_ids.sorted('activity_datetime')
        )
        description = self.notes or ''
        if timeline:
            description += '<h3>Prospect History</h3><ul>%s</ul>' % timeline
        lead_vals = {
            'name': self.name,
            'type': 'lead',
            'contact_name': self.contact_person,
            'partner_name': self.name,
            'phone': self.phone or self.mobile,
            'email_from': self.email,
            'website': self.website,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'user_id': self.user_id.id,
            'source_id': self.lead_source_id.id,
            'description': description,
            'x_prospect_id': self.id,
        }
        lead_vals = {
            field_name: value
            for field_name, value in lead_vals.items()
            if field_name in lead_fields and value not in (False, None, '')
        }
        if 'tag_ids' in lead_fields and self.tag_ids:
            lead_vals['tag_ids'] = [(6, 0, self.tag_ids.ids)]
        lead = lead_model.create(lead_vals)
        for attachment in self.attachment_ids:
            attachment.copy({'res_model': 'crm.lead', 'res_id': lead.id})
        self.with_context(skip_audit_log=True, skip_activity_timeline=True).write({'lead_id': lead.id})
        self.env['x_erp.prospect_activity'].with_context(skip_prospect_activity_apply=True).create({
            'prospect_id': self.id,
            'activity_type': 'conversion',
            'name': _('Converted to CRM Lead %s') % lead.display_name,
            'user_id': self.env.user.id,
        })
        self._create_audit_log('convert', '<p>Converted to CRM Lead: %s</p>' % escape(lead.display_name))
        lead.message_post(body=_('Created from Prospect Registry record: %s') % self.display_name)
        return lead

    @api.model
    def _global_search_domain(self, query):
        if not query:
            return []
        terms = [
            ('name', 'ilike', query),
            ('website', 'ilike', query),
            ('phone', 'ilike', query),
            ('mobile', 'ilike', query),
            ('email', 'ilike', query),
            ('linkedin', 'ilike', query),
            ('contact_person', 'ilike', query),
            ('city', 'ilike', query),
            ('country_id.name', 'ilike', query),
            ('user_id.name', 'ilike', query),
            ('industry', 'ilike', query),
            ('status', 'ilike', query),
            ('notes', 'ilike', query),
            ('tag_ids.name', 'ilike', query),
            ('product_interest_ids.name', 'ilike', query),
        ]
        return expression.OR([[term] for term in terms])

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        domain = domain or []
        if name:
            domain = expression.AND([domain, self._global_search_domain(name)])
        records = self.search(domain, limit=limit)
        return [(record.id, record.display_name) for record in records]

    def _api_payload(self):
        self.ensure_one()
        return {
            'id': self.id,
            'company': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'website': self.website,
            'city': self.city,
            'country': self.country_id.name,
            'salesperson': self.user_id.name,
            'status': self.status,
            'priority': self.priority,
            'next_followup_date': fields.Date.to_string(self.next_followup_date) if self.next_followup_date else False,
            'last_contact_date': fields.Date.to_string(self.last_contact_date) if self.last_contact_date else False,
            'duplicate_detected': self.duplicate_detected,
            'duplicate_ids': self.duplicate_prospect_ids.ids,
            'lead_id': self.lead_id.id,
        }

    @api.model
    def api_create_prospect(self, values):
        prospect = self.create(values)
        return prospect._api_payload()

    @api.model
    def api_update_prospect(self, prospect_id, values):
        prospect = self.browse(prospect_id).exists()
        if not prospect:
            raise UserError(_('Prospect not found.'))
        prospect.write(values)
        return prospect._api_payload()

    @api.model
    def api_search_prospect(self, query='', limit=50, domain=None):
        domain = domain or []
        if query:
            domain = expression.AND([domain, self._global_search_domain(query)])
        prospects = self.search(domain, limit=limit)
        return [prospect._api_payload() for prospect in prospects]

    @api.model
    def api_convert_to_crm(self, prospect_id):
        prospect = self.browse(prospect_id).exists()
        if not prospect:
            raise UserError(_('Prospect not found.'))
        lead = prospect._convert_to_crm_lead()
        return {
            'prospect_id': prospect.id,
            'lead_id': lead.id,
            'lead_name': lead.display_name,
        }

    @api.model
    def api_fetch_history(self, prospect_id):
        prospect = self.browse(prospect_id).exists()
        if not prospect:
            raise UserError(_('Prospect not found.'))
        return {
            'prospect': prospect._api_payload(),
            'activities': [
                {
                    'id': activity.id,
                    'type': activity.activity_type,
                    'summary': activity.name,
                    'date': fields.Datetime.to_string(activity.activity_datetime),
                    'salesperson': activity.user_id.name,
                    'call_result': activity.call_result,
                    'status_after': activity.status_after,
                }
                for activity in prospect.timeline_activity_ids
            ],
            'audit_logs': [
                {
                    'id': log.id,
                    'action': log.action,
                    'date': fields.Datetime.to_string(log.change_date),
                    'user': log.user_id.name,
                    'summary': log.change_summary,
                }
                for log in prospect.audit_log_ids
            ],
        }
