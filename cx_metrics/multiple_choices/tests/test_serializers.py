#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ..models import MultipleChoice
from ..services import MultipleChoiceService
from ..serializers import MultipleChoiceSerializer


class MultipleChoiceSerializerTestCase(TestCase):
    def test_validate_options(self):
        serializer = MultipleChoiceSerializer()
        options = [
            {'text': 'Option 1', 'order': 1},
            {'text': 'Option 2', 'order': 2},
        ]

        v_options = serializer.validate_options(options)

        self.assertEqual(len(v_options), len(options))
        for i, option in enumerate(v_options):
            self.assertEqual(option['text'], options[i]['text'])
            self.assertEqual(option['order'], options[i]['order'])

    def test_validate_options_raises_validation_error(self):
        serializer = MultipleChoiceSerializer()
        options = [
            {'text': 'Option 1', 'order': 1},
            {'text': 'Option 1', 'order': 2},
        ]

        self.assertRaisesMessage(
            ValidationError,
            'You should not have duplicate option texts',
            serializer.validate_options,
            options,
        )

    def test_validate_options_option_id_does_not_exists(self):
        mc = MultipleChoiceService.create(text=self.id())
        serializer = MultipleChoiceSerializer(instance=mc)
        options = [{'id': 1, 'text': 'Option 1', 'order': 1}]

        self.assertRaisesMessage(
            ValidationError,
            'Option 1 does not exists',
            serializer.validate_options,
            options
        )

    def test_validate(self):
        serializer = MultipleChoiceSerializer()
        attrs = {
            'options': [
                {'text': 'Option 1', 'order': 1},
                {'text': 'Option 2', 'order': 2},
            ]
        }

        self.assertDictEqual(serializer.validate(attrs), attrs)

    def test_validate_enabled_is_false(self):
        serializer = MultipleChoiceSerializer()
        attrs = {
            'enabled': False,
            'options': [],
        }
        self.assertEqual(serializer.validate(attrs), attrs)

    def test_validate_raises_validation_error(self):
        serializer = MultipleChoiceSerializer()
        attrs = {
            'enabled': True,
            'options': [{'text': 'Option 1', 'order': 1}]
        }

        self.assertRaisesMessage(
            ValidationError,
            'You should provide at least 2 enabled options.',
            serializer.validate,
            attrs,
        )

    def test_validate_no_option_raises_validation_error(self):
        mc = MultipleChoiceService.create(text=self.id())
        serializer = MultipleChoiceSerializer(instance=mc)
        attrs = {'enabled': True, 'options': []}

        self.assertRaisesMessage(
            ValidationError,
            'You should provide at least 2 enabled options.',
            serializer.validate,
            attrs,
        )

    def test_validate_existing_option_text_raises_validation_error(self):
        mc = MultipleChoiceService.create(text=self.id())
        option = MultipleChoiceService.create_option(mc, 'Option', 1)
        serializer = MultipleChoiceSerializer(instance=mc)
        attrs = {
            'enabled': True,
            'options': [
                {'id': option.pk, 'text': 'Option', 'order': 1},
                {'text': 'Option', 'order': 2},
            ]
        }

        self.assertRaisesMessage(
            ValidationError,
            'You should not have duplicate option texts',
            serializer.validate,
            attrs,
        )

    def test_create(self):
        v_data = {
            'type': MultipleChoice.TYPE_RADIO,
            'text': self.id(),
            'enabled': True,
            'required': True,
            'other_enabled': False,
            'options': [
                {'text': 'Option 1', 'order': 1},
                {'text': 'Option 2', 'order': 2},
            ]
        }

        serializer = MultipleChoiceSerializer()
        multiple_choice = serializer.create(v_data)

        self.assertIsInstance(multiple_choice, MultipleChoice)
        self.assertEqual(multiple_choice.type, v_data['type'])
        self.assertEqual(multiple_choice.text, v_data['text'])
        self.assertEqual(multiple_choice.enabled, v_data['enabled'])
        self.assertEqual(multiple_choice.required, v_data['required'])
        self.assertEqual(multiple_choice.other_enabled, v_data['other_enabled'])

        self.assertEqual(multiple_choice.options.count(), len(v_data['options']))

        for i, option in enumerate(multiple_choice.options.all()):
            self.assertEqual(option.enabled, v_data['options'][i].get('enabled', True))
            self.assertEqual(option.text, v_data['options'][i]['text'])
            self.assertEqual(option.order, v_data['options'][i]['order'])

    def test_update(self):
        mc = MultipleChoiceService.create(text=self.id())
        option = MultipleChoiceService.create_option(mc, 'Option', 1)
        v_data = {
            'type': MultipleChoice.TYPE_RADIO,
            'text': self.id(),
            'enabled': True,
            'required': True,
            'other_enabled': False,
            'options': [
                {'id': option.pk, 'text': 'Changed Option', 'order': 3},
                {'text': 'New Option', 'order': 4},
            ]
        }

        serializer = MultipleChoiceSerializer(instance=mc)
        multiple_choice = serializer.update(mc, v_data)

        self.assertIsInstance(multiple_choice, MultipleChoice)
        self.assertEqual(multiple_choice.type, v_data['type'])
        self.assertEqual(multiple_choice.text, v_data['text'])
        self.assertEqual(multiple_choice.enabled, v_data['enabled'])
        self.assertEqual(multiple_choice.required, v_data['required'])
        self.assertEqual(multiple_choice.other_enabled, v_data['other_enabled'])

        self.assertEqual(multiple_choice.options.count(), len(v_data['options']))

        for i, option in enumerate(multiple_choice.options.all()):
            self.assertIsNotNone(option.pk)
            self.assertEqual(option.enabled, v_data['options'][i].get('enabled', True))
            self.assertEqual(option.text, v_data['options'][i]['text'])
            self.assertEqual(option.order, v_data['options'][i]['order'])
