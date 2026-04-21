from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHighPriorityLead(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Lead = cls.env['crm.lead']

    def _make_lead(self, **vals):
        defaults = {'name': 'HP Test Lead', 'type': 'opportunity'}
        defaults.update(vals)
        return self.Lead.create(defaults)

    def test_toggle_marks_and_unmarks(self):
        lead = self._make_lead()
        self.assertFalse(lead.x_is_high_priority)
        self.assertFalse(lead.x_high_priority_effective)
        lead.action_toggle_high_priority()
        self.assertTrue(lead.x_is_high_priority)
        self.assertTrue(lead.x_high_priority_effective)
        self.assertTrue(lead.x_high_priority_set_on)
        self.assertEqual(lead.priority, '3')
        lead.action_toggle_high_priority()
        self.assertFalse(lead.x_is_high_priority)
        self.assertFalse(lead.x_high_priority_set_on)

    def test_mark_and_unmark_idempotent(self):
        lead = self._make_lead()
        lead.action_mark_high_priority()
        first_set = lead.x_high_priority_set_on
        lead.action_mark_high_priority()
        self.assertEqual(lead.x_high_priority_set_on, first_set)
        lead.action_unmark_high_priority()
        lead.action_unmark_high_priority()
        self.assertFalse(lead.x_is_high_priority)

    def test_auto_flag_high_value(self):
        lead = self._make_lead(expected_revenue=25000.0)
        lead._compute_high_priority_auto()
        self.assertTrue(lead.x_high_priority_auto)
        self.assertTrue(lead.x_high_priority_effective)

    def test_auto_flag_near_deadline(self):
        lead = self._make_lead(
            date_deadline=fields.Date.today() + timedelta(days=2),
        )
        lead._compute_high_priority_auto()
        self.assertTrue(lead.x_high_priority_auto)

    def test_no_auto_flag_for_won(self):
        won_stage = self.env['crm.stage'].search([('is_won', '=', True)], limit=1)
        if not won_stage:
            won_stage = self.env['crm.stage'].create({'name': 'Won', 'is_won': True})
        lead = self._make_lead(expected_revenue=50000.0, stage_id=won_stage.id)
        lead._compute_high_priority_auto()
        self.assertFalse(lead.x_high_priority_auto)

    def test_effective_search(self):
        hp = self._make_lead()
        hp.action_mark_high_priority()
        auto = self._make_lead(expected_revenue=25000.0)
        auto._compute_high_priority_auto()
        normal = self._make_lead()
        found = self.Lead.search([('x_high_priority_effective', '=', True)])
        self.assertIn(hp, found)
        self.assertIn(auto, found)
        self.assertNotIn(normal, found)

    def test_badge_computation(self):
        lead = self._make_lead()
        lead.action_mark_high_priority()
        self.assertEqual(lead.x_high_priority_badge, 'HIGH PRIORITY')
        lead.action_unmark_high_priority()
        self.assertFalse(lead.x_high_priority_badge)
        lead.expected_revenue = 25000.0
        lead._compute_high_priority_auto()
        lead._compute_high_priority_badge()
        self.assertEqual(lead.x_high_priority_badge, 'AUTO PRIORITY')
