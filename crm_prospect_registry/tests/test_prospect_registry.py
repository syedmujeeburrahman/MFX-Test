from odoo.tests.common import TransactionCase


class TestProspectRegistry(TransactionCase):

    def test_duplicate_detection_by_website(self):
        Prospect = self.env['x_erp.prospect']
        first = Prospect.create({
            'name': 'ABC Technologies',
            'website': 'https://www.example.com',
            'email': 'hello@example.com',
        })
        second = Prospect.create({
            'name': 'Different Name',
            'website': 'example.com/',
        })

        self.assertTrue(second.duplicate_detected)
        self.assertIn(first, second.duplicate_prospect_ids)

    def test_convert_to_crm_lead(self):
        prospect = self.env['x_erp.prospect'].create({
            'name': 'Demo Prospect',
            'contact_person': 'Demo Contact',
            'phone': '+1 555 0100',
            'email': 'demo@example.com',
        })

        lead = prospect._convert_to_crm_lead()

        self.assertEqual(prospect.lead_id, lead)
        self.assertEqual(lead.x_prospect_id, prospect)
        self.assertEqual(lead.partner_name, prospect.name)
