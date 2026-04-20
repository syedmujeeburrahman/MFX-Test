from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import datetime


class TestCrmLeadContactTracker(TransactionCase):
    """Test suite for the CRM Lead Contact Tracker module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sales = cls.env.ref('base.user_admin')
        cls.lead = cls.env['crm.lead'].create({
            'name': 'Test Lead - Contact Tracker',
            'type': 'opportunity',
            'contact_name': 'John Doe',
            'email_from': 'john@example.com',
            'phone': '+1234567890',
        })

    def test_01_default_not_contacted(self):
        """Test that leads are created with contacted flag as False."""
        self.assertFalse(self.lead.x_is_contacted_today)
        self.assertFalse(self.lead.x_contacted_date)
        self.assertFalse(self.lead.x_contacted_by)
        self.assertEqual(self.lead.x_contact_count, 0)

    def test_02_mark_as_contacted(self):
        """Test marking a lead as contacted."""
        self.lead.action_mark_contacted()
        self.assertTrue(self.lead.x_is_contacted_today)
        self.assertTrue(self.lead.x_contacted_date)
        self.assertEqual(self.lead.x_contacted_by, self.env.user)
        self.assertEqual(self.lead.x_contact_count, 1)

    def test_03_mark_contacted_returns_notification(self):
        """Test that marking returns a notification action."""
        result = self.lead.action_mark_contacted()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertEqual(result['params']['type'], 'success')

    def test_04_unmark_contacted(self):
        """Test unmarking a contacted lead."""
        self.lead.action_mark_contacted()
        self.assertTrue(self.lead.x_is_contacted_today)
        self.lead.action_unmark_contacted()
        self.assertFalse(self.lead.x_is_contacted_today)

    def test_05_unmark_returns_notification(self):
        """Test that unmarking returns a warning notification."""
        self.lead.action_mark_contacted()
        result = self.lead.action_unmark_contacted()
        self.assertEqual(result['params']['type'], 'warning')

    def test_06_contact_count_increments(self):
        """Test that the contact count increments each time."""
        self.lead.action_mark_contacted()
        self.assertEqual(self.lead.x_contact_count, 1)
        # Reset and mark again
        self.lead.write({'x_is_contacted_today': False})
        self.lead.action_mark_contacted()
        self.assertEqual(self.lead.x_contact_count, 2)

    def test_07_contact_note_in_chatter(self):
        """Test that a note is posted in chatter when marking."""
        self.lead.x_contacted_note = 'Called and discussed pricing'
        self.lead.action_mark_contacted()
        last_message = self.lead.message_ids[0]
        self.assertIn('Lead Contacted', last_message.body)
        self.assertIn('Called and discussed pricing', last_message.body)

    def test_08_chatter_message_on_unmark(self):
        """Test that a chatter message is posted when unmarking."""
        self.lead.action_mark_contacted()
        self.lead.action_unmark_contacted()
        last_message = self.lead.message_ids[0]
        self.assertIn('Contact Mark Removed', last_message.body)

    def test_09_cron_reset_contacted(self):
        """Test that the cron job resets contacted flags."""
        self.lead.action_mark_contacted()
        self.assertTrue(self.lead.x_is_contacted_today)
        # Run the cron reset
        self.env['crm.lead']._cron_reset_contacted_today()
        self.assertFalse(self.lead.x_is_contacted_today)

    def test_10_cron_preserves_contact_count(self):
        """Test that cron reset does not affect the total contact count."""
        self.lead.action_mark_contacted()
        count_before = self.lead.x_contact_count
        self.env['crm.lead']._cron_reset_contacted_today()
        self.assertEqual(self.lead.x_contact_count, count_before)

    def test_11_cron_preserves_contacted_date(self):
        """Test that cron reset does not clear the last contacted date."""
        self.lead.action_mark_contacted()
        date_before = self.lead.x_contacted_date
        self.env['crm.lead']._cron_reset_contacted_today()
        self.assertEqual(self.lead.x_contacted_date, date_before)

    def test_12_multiple_leads_mark(self):
        """Test marking multiple leads at once."""
        lead2 = self.env['crm.lead'].create({
            'name': 'Test Lead 2',
            'type': 'opportunity',
        })
        leads = self.lead | lead2
        leads.action_mark_contacted()
        self.assertTrue(self.lead.x_is_contacted_today)
        self.assertTrue(lead2.x_is_contacted_today)

    def test_13_cron_only_resets_contacted(self):
        """Test that cron only affects leads that are marked as contacted."""
        lead2 = self.env['crm.lead'].create({
            'name': 'Test Lead Pending',
            'type': 'opportunity',
        })
        self.lead.action_mark_contacted()
        # lead2 remains not contacted
        self.env['crm.lead']._cron_reset_contacted_today()
        self.assertFalse(self.lead.x_is_contacted_today)
        self.assertFalse(lead2.x_is_contacted_today)

    def test_14_activity_feedback_auto_marks(self):
        """Test that completing an activity auto-marks the lead as contacted."""
        activity_type = self.env.ref('mail.mail_activity_data_call', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([], limit=1)
        activity = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get('crm.lead').id,
            'res_id': self.lead.id,
            'activity_type_id': activity_type.id,
            'summary': 'Call the lead',
            'date_deadline': fields.Date.today(),
            'user_id': self.env.uid,
        })
        # Complete the activity via feedback
        self.lead.activity_feedback(
            'Called and discussed the proposal',
            attachment_ids=None,
        )
        self.assertTrue(self.lead.x_is_contacted_today)
        self.assertEqual(self.lead.x_contact_count, 1)
