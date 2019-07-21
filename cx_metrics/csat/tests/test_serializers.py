#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase
from upkook_core.businesses.services import BusinessService

from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..services.csat import CSATService, CSATSurvey
from ..serializers import CSATSerializer


class CSATSerializerTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'multiple_choices', 'csat']

    def setUp(self):
        self.business = BusinessService.get_business_by_id(1)

    def test_to_representation_csat_survey_instance(self):
        instance = CSATService.get_csat_survey_by_id(1)
        serializer = CSATSerializer()
        fields = ('id', 'type', 'name', 'text', 'text_enabled', 'question', 'contra_reason', 'message', 'scale')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': {
                "text": "Multiple Choice",
                "type": "R",
                'enabled': True,
                'required': True,
                "other_enabled": False,
                "options": [
                    {"id": 1, "text": "Option", 'enabled': True, "order": 1},
                    {'id': 2, "text": "Option2", 'enabled': True, "order": 2},
                ]
            },
            'scale': instance.scale
        })

        self.assertDictEqual(serializer.to_representation(instance), expected)

    def test_to_representation_survey_instance(self):
        instance = CSATService.get_csat_survey_by_id(1)
        serializer = CSATSerializer()
        fields = ('id', 'type', 'name', 'text', 'text_enabled', 'question', 'contra_reason', 'message', 'scale')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': {
                "text": "Multiple Choice",
                "type": "R",
                'enabled': True,
                'required': True,
                "other_enabled": False,
                "options": [
                    {"id": 1, "text": "Option", 'enabled': True, "order": 1},
                    {'id': 2, "text": "Option2", 'enabled': True, "order": 2},
                ]
            },
            'scale': instance.scale
        })
        self.assertDictEqual(serializer.to_representation(instance.survey), expected)

    def test_to_representation_http_404(self):
        instance = CSATService.get_csat_survey_by_id(1).survey
        instance.id = 2
        serializer = CSATSerializer()
        self.assertRaises(Http404, serializer.to_representation, instance)

    def test_create(self):
        v_data = {
            'name': 'CSAT Survey',
            'text': 'Welcome',
            'text_enabled': True,
            'question': 'How do you rate us?',
            'contra': {
                'text': 'Hello World!',
            },
            'message': 'Thanks you',
            'business': self.business,
        }
        serializer = CSATSerializer()

        csat_survey = serializer.create(v_data)

        self.assertIsInstance(csat_survey, CSATSurvey)
        self.assertEqual(csat_survey.name, v_data['name'])
        self.assertEqual(csat_survey.text, v_data['text'])
        self.assertEqual(csat_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(csat_survey.question, v_data['question'])
        self.assertEqual(csat_survey.contra.text, v_data['contra']['text'])
        self.assertEqual(csat_survey.message, v_data['message'])
        self.assertEqual(csat_survey.business, v_data['business'])

    def test_update(self):
        v_data = {
            'name': 'Changed-Name',
            'text': 'Changed-Text',
            'text_enabled': True,
            'question': 'Changed-Question',
            'contra': {
                'text': 'test_contra_text',
                'required': False,
            },
            'message': 'test_message',
        }
        instance = CSATService.get_csat_survey_by_id(1)
        instance.contra = MultipleChoiceService.create(text=self.id())
        serializer = CSATSerializer()

        csat_survey = serializer.update(instance, v_data)

        self.assertIsInstance(csat_survey, CSATSurvey)
        self.assertEqual(csat_survey.name, v_data['name'])
        self.assertEqual(csat_survey.text, v_data['text'])
        self.assertEqual(csat_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(csat_survey.question, v_data['question'])
        self.assertEqual(csat_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(csat_survey.contra.required)
        self.assertEqual(csat_survey.message, v_data['message'])

    def test_serializer_with_survey_object(self):
        instance = CSATService.get_csat_survey_by_id(1)
        serializer = CSATSerializer(instance=instance.survey)
        fields = ('id', 'type', 'name', 'text', 'text_enabled', 'question', 'contra_reason', 'message', 'scale')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': {
                "text": "Multiple Choice",
                "type": "R",
                'enabled': True,
                'required': True,
                "other_enabled": False,
                "options": [
                    {"id": 1, "text": "Option", 'enabled': True, "order": 1},
                    {'id': 2, "text": "Option2", 'enabled': True, "order": 2},
                ]
            },
            'scale': instance.scale
        })

        self.assertDictEqual(serializer.to_representation(instance), expected)

    def test_update_csat_without_contra(self):
        v_data = {
            'name': 'Changed-Name',
            'text': 'Changed-Text',
            'text_enabled': True,
            'question': 'Changed-Question',
            'contra': {
                'text': 'test_contra_text',
                'required': False,
            },
            'message': 'test_message',
        }
        instance = CSATService.get_csat_survey_by_id(1)
        instance.contra = None
        serializer = CSATSerializer()

        csat_survey = serializer.update(instance, v_data)

        self.assertIsInstance(csat_survey, CSATSurvey)
        self.assertEqual(csat_survey.name, v_data['name'])
        self.assertEqual(csat_survey.text, v_data['text'])
        self.assertEqual(csat_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(csat_survey.question, v_data['question'])
        self.assertEqual(csat_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(csat_survey.contra.required)
        self.assertEqual(csat_survey.message, v_data['message'])
