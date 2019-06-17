#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from ..models import MultipleChoice
from ..services import MultipleChoiceService


class MultipleChoiceServiceTestCase(TestCase):
    def test_create_default_values(self):
        mc = MultipleChoiceService.create(text=self.id())
        self.assertIsInstance(mc, MultipleChoice)
        self.assertEqual(mc.text, self.id())
        self.assertTrue(mc.enabled)
        self.assertTrue(mc.required)
        self.assertEqual(mc.type, MultipleChoice.TYPE_RADIO)
        self.assertTrue(mc.other_enabled)

    def test_create(self):
        mc = MultipleChoiceService.create(
            text=self.id(),
            enabled=False,
            required=False,
            type_=MultipleChoice.TYPE_SELECT,
            other_enabled=False,
        )
        self.assertIsInstance(mc, MultipleChoice)
        self.assertEqual(mc.text, self.id())
        self.assertFalse(mc.enabled)
        self.assertFalse(mc.required)
        self.assertEqual(mc.type, MultipleChoice.TYPE_SELECT)
        self.assertFalse(mc.other_enabled)

    def test_get_by_id(self):
        mc = MultipleChoiceService.create(text=self.id())
        other = MultipleChoiceService.get_by_id(mc.pk)
        self.assertEqual(other.text, self.id())

    def test_get_by_id_none(self):
        self.assertIsNone(MultipleChoiceService.get_by_id(0))
