#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase, override_settings
from mock import patch
from rest_framework.exceptions import ValidationError

from ..models import MultipleChoice, Option
from ..services import MultipleChoiceService
from ..serializers import MultipleChoiceSerializer, CachedMultipleChoiceSerializer, MultipleChoiceRespondSerializer


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


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class CachedMultipleChoiceSerializerTestCase(TestCase):
    fixtures = ['multiple_choices']

    def test_to_representation_cached(self):
        mc = MultipleChoiceService.get_by_id(1)
        expected = MultipleChoiceSerializer().to_representation(mc)
        MultipleChoiceService.cache_representation(mc.id, expected)

        serializer = CachedMultipleChoiceSerializer(mc)

        with patch.object(MultipleChoiceSerializer, 'to_representation') as mock_to_representation:
            representation = serializer.to_representation(mc)
            self.assertFalse(mock_to_representation.called)
        self.assertEqual(representation, expected)

    def test_to_representation_not_cached(self):
        mc = MultipleChoiceService.create(text=self.id())
        serializer = MultipleChoiceSerializer()
        cache_serializer = CachedMultipleChoiceSerializer(mc)
        expected_representation = serializer.to_representation(mc)

        representation = cache_serializer.to_representation(mc)

        self.assertEqual(representation, expected_representation)


class MultipleChoiceRespondSerializerTestCase(TestCase):
    fixtures = ['multiple_choices']

    def test_validate(self):
        multiple_choice_id = MultipleChoice.objects.first().id
        option = Option.objects.first()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [option.id],
        }
        serializer = MultipleChoiceRespondSerializer(mc_id=multiple_choice_id)
        value = serializer.validate(data['options'])
        self.assertListEqual(data['options'], value)

    def test_validate_raise_validation_error_contra_and_option_not_related(self):
        multiple_choice_id = MultipleChoice.objects.first().id
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [1000],
        }
        serializer = MultipleChoiceRespondSerializer(mc_id=multiple_choice_id)

        self.assertRaisesMessage(
            ValidationError,
            "Contra option and Survey not related!",
            serializer.validate,
            data['options']
        )

    def test_validate_raise_validation_error_has_no_contra(self):
        option = Option.objects.first()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [option.id],
        }
        serializer = MultipleChoiceRespondSerializer()
        self.assertRaisesMessage(
            ValidationError,
            "Contra could not be none !",
            serializer.validate,
            data['options'])

    def test_validate_none_value(self):
        multiple_choice_id = MultipleChoice.objects.first().id
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': None
        }
        serializer = MultipleChoiceRespondSerializer(mc_id=multiple_choice_id)
        self.assertIsNone(serializer.validate(data['options']))

    def test_validate_options_empty_list(self):
        multiple_choice_id = MultipleChoice.objects.first().id
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': []
        }
        serializer = MultipleChoiceRespondSerializer(mc_id=multiple_choice_id)
        self.assertEqual(serializer.validate(data['options']), [])
