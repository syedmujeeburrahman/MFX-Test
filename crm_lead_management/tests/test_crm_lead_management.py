from datetime import date, timedelta

from odoo.tests.common import TransactionCase


class TestCrmLeadManagement(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_prospect = cls.env.ref(
            'crm_lead_management.stage_prospect_identified'
        )
        cls.stage_discussion = cls.env.ref(
            'crm_lead_management.stage_initial_discussion'
        )
        cls.stage_technical = cls.env.ref(
            'crm_lead_management.stage_technical_discussion'
        )
        cls.stage_demo = cls.env.ref(
            'crm_lead_management.stage_demo_completed'
        )
        cls.stage_negotiation = cls.env.ref(
            'crm_lead_management.stage_negotiation'
        )
        cls.stage_won = cls.env.ref(
            'crm_lead_management.stage_won'
        )

    def test_custom_stages_created(self):
        """Test that all 6 custom pipeline stages are created."""
        stages = self.env['crm.stage'].search([('active', '=', True)])
        stage_names = stages.mapped('name')
        expected = [
            'Prospect Identified',
            'Initial Discussion',
            'Technical Discussion',
            'Demo Completed',
            'Negotiation',
            'Won',
        ]
        for name in expected:
            self.assertIn(name, stage_names, f"Stage '{name}' not found")

    def test_stage_sequence(self):
        """Test that stages are in correct sequence order."""
        self.assertLess(
            self.stage_prospect.sequence,
            self.stage_discussion.sequence,
        )
        self.assertLess(
            self.stage_discussion.sequence,
            self.stage_technical.sequence,
        )
        self.assertLess(
            self.stage_technical.sequence,
            self.stage_demo.sequence,
        )
        self.assertLess(
            self.stage_demo.sequence,
            self.stage_negotiation.sequence,
        )

    def test_won_stage_is_won(self):
        """Test that Won stage has is_won=True."""
        self.assertTrue(self.stage_won.is_won)

    def test_lead_type_field(self):
        """Test creating leads with different lead types."""
        lead_hot = self.env['crm.lead'].create({
            'name': 'Hot Lead Test',
            'x_lead_type': 'hot',
        })
        self.assertEqual(lead_hot.x_lead_type, 'hot')

        lead_warm = self.env['crm.lead'].create({
            'name': 'Warm Lead Test',
            'x_lead_type': 'warm',
        })
        self.assertEqual(lead_warm.x_lead_type, 'warm')

        lead_cold = self.env['crm.lead'].create({
            'name': 'Cold Lead Test',
            'x_lead_type': 'cold',
        })
        self.assertEqual(lead_cold.x_lead_type, 'cold')

    def test_lead_type_default(self):
        """Test that lead type defaults to 'cold'."""
        lead = self.env['crm.lead'].create({
            'name': 'Default Lead Type Test',
        })
        self.assertEqual(lead.x_lead_type, 'cold')

    def test_next_followup_date(self):
        """Test setting next follow-up date on a lead."""
        tomorrow = date.today() + timedelta(days=1)
        lead = self.env['crm.lead'].create({
            'name': 'Follow-up Test',
            'x_next_followup_date': tomorrow,
        })
        self.assertEqual(lead.x_next_followup_date, tomorrow)

    def test_followup_activity_created_on_create(self):
        """Test that activity is created when lead is created with follow-up date."""
        tomorrow = date.today() + timedelta(days=1)
        lead = self.env['crm.lead'].create({
            'name': 'Activity Auto-Create Test',
            'x_next_followup_date': tomorrow,
        })
        activities = lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        )
        self.assertTrue(
            activities,
            "Follow-up activity should be created when lead has follow-up date",
        )
        self.assertEqual(activities[0].date_deadline, tomorrow)

    def test_followup_activity_created_on_write(self):
        """Test that activity is created when follow-up date is set via write."""
        lead = self.env['crm.lead'].create({
            'name': 'Activity Write Test',
        })
        self.assertFalse(lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        ))
        next_week = date.today() + timedelta(days=7)
        lead.write({'x_next_followup_date': next_week})
        activities = lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        )
        self.assertTrue(activities, "Follow-up activity should be created on write")

    def test_no_duplicate_followup_activity(self):
        """Test that duplicate follow-up activities are not created."""
        tomorrow = date.today() + timedelta(days=1)
        lead = self.env['crm.lead'].create({
            'name': 'No Duplicate Activity Test',
            'x_next_followup_date': tomorrow,
        })
        initial_count = len(lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        ))
        # Trigger again
        lead.action_schedule_followup_activity()
        final_count = len(lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        ))
        self.assertEqual(initial_count, final_count, "Should not create duplicate activities")

    def test_lead_with_full_data(self):
        """Test creating a lead with all custom and standard fields."""
        lead = self.env['crm.lead'].create({
            'name': 'Full Data Lead',
            'contact_name': 'John Doe',
            'email_from': 'john@example.com',
            'phone': '+1234567890',
            'partner_name': 'Acme Corp',
            'function': 'CTO',
            'x_lead_type': 'hot',
            'x_next_followup_date': date.today() + timedelta(days=3),
            'city': 'Mumbai',
            'description': 'Interested in enterprise plan',
            'priority': '2',
            'stage_id': self.stage_prospect.id,
        })
        self.assertTrue(lead.exists())
        self.assertEqual(lead.contact_name, 'John Doe')
        self.assertEqual(lead.x_lead_type, 'hot')
        self.assertEqual(lead.stage_id, self.stage_prospect)

    def test_cron_followup_reminder(self):
        """Test the cron job for follow-up reminders."""
        tomorrow = date.today() + timedelta(days=1)
        lead = self.env['crm.lead'].create({
            'name': 'Cron Reminder Test',
            'x_next_followup_date': tomorrow,
            'stage_id': self.stage_prospect.id,
        })
        # Clear existing activities
        lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        ).unlink()
        # Run cron
        self.env['crm.lead']._cron_followup_reminder()
        activities = lead.activity_ids.filtered(
            lambda a: a.summary == 'Follow-up'
        )
        self.assertTrue(activities, "Cron should create follow-up activity for upcoming leads")

    def test_utm_sources_created(self):
        """Test that UTM sources are created."""
        sources = [
            'LinkedIn', 'Cold Call', 'Referral',
            'Website Inquiry', 'Trade Show',
            'Email Campaign', 'Social Media', 'Partner / Channel',
        ]
        for source_name in sources:
            source = self.env['utm.source'].search([('name', '=', source_name)])
            self.assertTrue(
                source,
                f"UTM source '{source_name}' should exist",
            )

    def test_crm_tags_created(self):
        """Test that CRM tags are created."""
        tags = [
            'Enterprise', 'SME', 'Startup', 'High Value',
            'Repeat Customer', 'Decision Maker', 'Technical Buyer', 'Urgent',
        ]
        for tag_name in tags:
            tag = self.env['crm.tag'].search([('name', '=', tag_name)])
            self.assertTrue(
                tag,
                f"CRM tag '{tag_name}' should exist",
            )
