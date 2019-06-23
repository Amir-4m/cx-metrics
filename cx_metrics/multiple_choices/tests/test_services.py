#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ..models import MultipleChoice, Option
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

    def test_create_options(self):
        mc = MultipleChoiceService.create(text=self.id())
        options_kwargs = [
            {'text': 'Option 1', 'order': 1},
            {'text': 'Option 2', 'order': 2},
        ]

        options = MultipleChoiceService.create_options(mc, options_kwargs)

        self.assertEqual(len(options), 2)
        for i, option in enumerate(options):
            self.assertIsInstance(option, Option)
            self.assertTrue(option.enabled)
            self.assertEqual(option.text, options_kwargs[i]['text'])
            self.assertEqual(option.order, options_kwargs[i]['order'])

    def test_create_options_raises_validation_error(self):
        mc = MultipleChoiceService.create(text=self.id())
        options_kwargs = [
            {'text': 'Option 1', 'order': 1},
            {'text': 'Option 1', 'order': 2},
        ]

        self.assertRaisesMessage(
            ValidationError,
            'Failed to create options',
            MultipleChoiceService.create_options,
            mc,
            options_kwargs,
        )
