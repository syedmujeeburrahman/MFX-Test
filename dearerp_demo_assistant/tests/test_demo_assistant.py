from odoo.tests.common import TransactionCase


class TestDemoSection(TransactionCase):
    """Tests for the DearERP Demo Section model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.section = cls.env['dearerp.demo.section'].create({
            'name': 'Test Section',
            'section_type': 'features',
            'icon': 'fa-star',
            'subtitle': 'Test subtitle',
        })

    def test_section_creation(self):
        """Test that a section can be created with required fields."""
        self.assertEqual(self.section.name, 'Test Section')
        self.assertEqual(self.section.section_type, 'features')
        self.assertTrue(self.section.active)

    def test_section_item_count(self):
        """Test that item_count is computed correctly."""
        self.assertEqual(self.section.item_count, 0)
        self.env['dearerp.demo.item'].create({
            'name': 'Test Item',
            'section_id': self.section.id,
        })
        self.section.invalidate_recordset()
        self.assertEqual(self.section.item_count, 1)

    def test_section_faq_count(self):
        """Test that faq_count is computed correctly."""
        self.assertEqual(self.section.faq_count, 0)
        self.env['dearerp.demo.faq'].create({
            'name': 'Test FAQ?',
            'section_id': self.section.id,
            'answer': '<p>Test answer</p>',
            'category': 'general',
        })
        self.section.invalidate_recordset()
        self.assertEqual(self.section.faq_count, 1)


class TestDemoItem(TransactionCase):
    """Tests for the DearERP Demo Item model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.section = cls.env['dearerp.demo.section'].create({
            'name': 'Features Section',
            'section_type': 'features',
        })
        cls.item = cls.env['dearerp.demo.item'].create({
            'name': 'Test Feature',
            'section_id': cls.section.id,
            'icon': 'fa-check',
            'summary': 'A test feature',
            'highlight': True,
        })

    def test_item_creation(self):
        """Test that an item can be created with required fields."""
        self.assertEqual(self.item.name, 'Test Feature')
        self.assertEqual(self.item.section_id, self.section)
        self.assertTrue(self.item.highlight)

    def test_item_related_section_type(self):
        """Test that section_type is correctly related from the section."""
        self.assertEqual(self.item.section_type, 'features')

    def test_item_cascade_delete(self):
        """Test that items are deleted when section is deleted."""
        item_id = self.item.id
        self.section.unlink()
        self.assertFalse(
            self.env['dearerp.demo.item'].search([('id', '=', item_id)])
        )


class TestDemoFaq(TransactionCase):
    """Tests for the DearERP Demo FAQ model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.section = cls.env['dearerp.demo.section'].create({
            'name': 'FAQ Section',
            'section_type': 'faq',
        })
        cls.faq = cls.env['dearerp.demo.faq'].create({
            'name': 'Is this a test?',
            'section_id': cls.section.id,
            'answer': '<p>Yes, this is a test.</p>',
            'category': 'general',
            'difficulty': 'easy',
        })

    def test_faq_creation(self):
        """Test that a FAQ can be created with required fields."""
        self.assertEqual(self.faq.name, 'Is this a test?')
        self.assertEqual(self.faq.category, 'general')
        self.assertEqual(self.faq.difficulty, 'easy')

    def test_faq_defaults(self):
        """Test FAQ default values."""
        faq = self.env['dearerp.demo.faq'].create({
            'name': 'Another question?',
            'section_id': self.section.id,
            'answer': '<p>Another answer</p>',
        })
        self.assertEqual(faq.category, 'general')
        self.assertEqual(faq.difficulty, 'easy')
        self.assertTrue(faq.active)

    def test_faq_cascade_delete(self):
        """Test that FAQs are deleted when section is deleted."""
        faq_id = self.faq.id
        self.section.unlink()
        self.assertFalse(
            self.env['dearerp.demo.faq'].search([('id', '=', faq_id)])
        )
