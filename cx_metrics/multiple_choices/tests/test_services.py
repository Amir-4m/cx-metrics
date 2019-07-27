#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError

from cx_metrics.multiple_choices.services.multiple_choice import OptionResponseService
from ..models import MultipleChoice, Option
from ..services import MultipleChoiceService


class MultipleChoiceServiceTestCase(TestCase):
    fixtures = ['multiple_choices']

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

    def test_get_option_by_id(self):
        option = Option.objects.first()
        other = MultipleChoiceService.get_option_by_id(option.pk)
        self.assertIsInstance(other, Option)
        self.assertEqual(other.pk, option.pk)
        self.assertEqual(option.text, other.text)

    def test_get_option_by_id_none(self):
        self.assertIsNone(MultipleChoiceService.get_option_by_id(0))

    def test_option_exists_true(self):
        option = Option.objects.first()
        self.assertTrue(MultipleChoiceService.option_exists(option.multiple_choice, option.pk))

    def test_option_exists_false(self):
        option = Option.objects.first()
        self.assertFalse(MultipleChoiceService.option_exists(option.multiple_choice, 0))

    def test_option_text_exists_true(self):
        option = Option.objects.first()
        value = MultipleChoiceService.option_text_exists(option.multiple_choice, option.text)
        self.assertTrue(value)

    def test_option_text_exists_false(self):
        option = Option.objects.first()
        value = MultipleChoiceService.option_text_exists(
            option.multiple_choice, option.text, option.pk
        )
        self.assertFalse(value)

    def test_update_options(self):
        mc = MultipleChoiceService.create(text=self.id())
        option = MultipleChoiceService.create_option(mc, 'Option', 1)
        options_kwargs = [{'id': option.pk, 'text': 'Option 1', 'order': 1}]

        MultipleChoiceService.update_options(mc, options_kwargs)

        option.refresh_from_db()
        self.assertEqual(option.text, options_kwargs[0].get('text'))
        self.assertEqual(option.order, options_kwargs[0].get('order'))

    def test_update_options_with_new_options(self):
        mc = MultipleChoiceService.create(text=self.id())
        option = MultipleChoiceService.create_option(mc, 'Option', 1)
        options_kwargs = [
            {'id': option.pk, 'text': 'Option 1', 'order': 1},
            {'text': 'Option 2', 'order': 2}
        ]

        MultipleChoiceService.update_options(mc, options_kwargs)

        self.assertEqual(mc.options.count(), 2)
        qs = mc.options.all()
        self.assertEqual(qs[1].text, options_kwargs[1].get('text'))
        self.assertEqual(qs[1].order, options_kwargs[1].get('order'))

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_cache_representation(self):
        expected_repr = {
            "test": "test"
        }
        MultipleChoiceService.cache_representation(1, expected_repr)

        representation = MultipleChoiceService.representation_from_cache(1)

        self.assertEqual(representation, expected_repr)

    def test_generate_cache_key(self):
        expected_key = "multiple-choice-1"

        key = MultipleChoiceService.representation_cache_key(1)

        self.assertEqual(expected_key, key)


class OptionResponseServiceTestCase(TestCase):

    def test_get_option_text_not_exist(self):
        self.assertIsNone(OptionResponseService.get_option_text(id=1000))
