# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestDemoSection(TransactionCase):
    """Test cases for DearERP Demo Assistant module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DemoSection = cls.env['x_demo.section']
        cls.DemoItem = cls.env['x_demo.section.item']

        cls.section = cls.DemoSection.create({
            'name': 'Test Section',
            'section_type': 'features',
            'subtitle': 'Test subtitle',
            'icon_class': 'fa-star',
            'card_color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        })

    def test_section_creation(self):
        """Test that a demo section can be created."""
        self.assertEqual(self.section.name, 'Test Section')
        self.assertEqual(self.section.section_type, 'features')
        self.assertTrue(self.section.active)

    def test_item_creation(self):
        """Test that demo items can be created and linked to a section."""
        item = self.DemoItem.create({
            'name': 'Test Item',
            'section_id': self.section.id,
            'icon_class': 'fa-check',
            'content': '<p>Test content</p>',
        })
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.section_id, self.section)
        self.assertEqual(item.section_type, 'features')
        self.assertTrue(item.active)

    def test_item_count_computed(self):
        """Test that item_count is computed correctly."""
        self.assertEqual(self.section.item_count, 0)

        self.DemoItem.create({
            'name': 'Item 1',
            'section_id': self.section.id,
        })
        self.DemoItem.create({
            'name': 'Item 2',
            'section_id': self.section.id,
        })
        self.section.invalidate_recordset(['item_count'])
        self.assertEqual(self.section.item_count, 2)

    def test_item_cascade_delete(self):
        """Test that items are deleted when section is deleted."""
        item = self.DemoItem.create({
            'name': 'Cascade Test Item',
            'section_id': self.section.id,
        })
        item_id = item.id
        self.section.unlink()
        self.assertFalse(self.DemoItem.search([('id', '=', item_id)]))

    def test_faq_item_fields(self):
        """Test FAQ-specific fields on items."""
        faq_section = self.DemoSection.create({
            'name': 'FAQ Section',
            'section_type': 'faq',
        })
        faq_item = self.DemoItem.create({
            'name': 'Test Question?',
            'section_id': faq_section.id,
            'faq_category': 'technical',
            'answer': '<p>Test answer</p>',
        })
        self.assertEqual(faq_item.faq_category, 'technical')
        self.assertEqual(faq_item.section_type, 'faq')

    def test_pricing_item_fields(self):
        """Test pricing-specific fields on items."""
        pricing_section = self.DemoSection.create({
            'name': 'Pricing Section',
            'section_type': 'pricing',
        })
        pricing_item = self.DemoItem.create({
            'name': 'Pro Plan',
            'section_id': pricing_section.id,
            'plan_price': '$149',
            'plan_period': 'per month',
            'is_popular': True,
        })
        self.assertEqual(pricing_item.plan_price, '$149')
        self.assertTrue(pricing_item.is_popular)

    def test_comparison_item_fields(self):
        """Test comparison-specific fields on items."""
        comp_section = self.DemoSection.create({
            'name': 'Comparison Section',
            'section_type': 'comparison',
        })
        comp_item = self.DemoItem.create({
            'name': 'Feature X',
            'section_id': comp_section.id,
            'dearerp_rating': 'excellent',
            'competitor_name': 'Competitor A',
            'competitor_rating': 'limited',
        })
        self.assertEqual(comp_item.dearerp_rating, 'excellent')
        self.assertEqual(comp_item.competitor_rating, 'limited')

    def test_section_ordering(self):
        """Test that sections are ordered by sequence."""
        section2 = self.DemoSection.create({
            'name': 'Second Section',
            'section_type': 'faq',
            'sequence': 5,
        })
        sections = self.DemoSection.search([
            ('id', 'in', [self.section.id, section2.id])
        ])
        self.assertEqual(sections[0], section2)

    def test_all_section_types(self):
        """Test that all section types can be created."""
        section_types = [
            'introduction', 'features', 'comparison',
            'use_cases', 'pricing', 'faq',
        ]
        for stype in section_types:
            section = self.DemoSection.create({
                'name': f'Test {stype}',
                'section_type': stype,
            })
            self.assertEqual(section.section_type, stype)
