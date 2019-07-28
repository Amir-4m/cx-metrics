#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase
from upkook_core.businesses.services import BusinessService

from cx_metrics.ces.models import CESSurvey
from ..serializers import CESSerializer
from ..services.ces import CESService


class CESSerializerTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'multiple_choices', 'ces']

    def setUp(self):
        self.business = BusinessService.get_business_by_id(1)

    def test_to_representation_ces_survey_instance(self):
        instance = CESService.get_ces_survey_by_id(1)
        serializer = CESSerializer()
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
        instance = CESService.get_ces_survey_by_id(1)
        serializer = CESSerializer(instance.survey)
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
        instance = CESService.get_ces_survey_by_id(1).survey
        instance.id = 2
        serializer = CESSerializer()
        self.assertRaises(Http404, serializer.to_representation, instance)

    def test_create(self):
        v_data = {
            'name': 'CES Survey',
            'text': 'Welcome',
            'text_enabled': True,
            'question': 'How do you rate us?',
            'contra': {
                'text': 'Hello World!',
            },
            'message': 'Thanks you',
            'business': self.business,
        }
        serializer = CESSerializer()

        ces_survey = serializer.create(v_data)

        self.assertIsInstance(ces_survey, CESSurvey)
        self.assertEqual(ces_survey.name, v_data['name'])
        self.assertEqual(ces_survey.text, v_data['text'])
        self.assertEqual(ces_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(ces_survey.question, v_data['question'])
        self.assertEqual(ces_survey.contra.text, v_data['contra']['text'])
        self.assertEqual(ces_survey.message, v_data['message'])
        self.assertEqual(ces_survey.business, v_data['business'])
