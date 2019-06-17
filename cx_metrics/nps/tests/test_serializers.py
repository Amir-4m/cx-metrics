#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase

from upkook_core.businesses.services import BusinessService
from upkook_core.customers.models import Customer

from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..models import NPSSurvey, NPSResponse
from ..serializers import NPSSerializer, NPSSerializerV11, NPSRespondSerializer
from ..services import NPSService


class NPSSerializerTestCase(TestCase):
    fixtures = ['nps']

    def test_to_representation_nps_survey_instance(self):
        instance = NPSService.get_nps_survey_by_id(1)
        serializer = NPSSerializer()
        fields = ('name', 'text', 'text_enabled', 'question', 'message')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': None,
        })
        self.assertDictEqual(serializer.to_representation(instance), expected)

    def test_to_representation_survey_instance(self):
        instance = NPSService.get_nps_survey_by_id(1)
        serializer = NPSSerializer()
        fields = ('name', 'text', 'text_enabled', 'question', 'message')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': None,
        })
        self.assertDictEqual(serializer.to_representation(instance.survey), expected)

    def test_to_representation_http_404(self):
        instance = NPSService.get_nps_survey_by_id(1).survey
        instance.id = 2
        serializer = NPSSerializer()
        self.assertRaises(Http404, serializer.to_representation, instance)


class NPSSerializerV11TestCase(TestCase):
    fixtures = ['nps']

    def setUp(self):
        self.business = BusinessService.get_business_by_id(1)

    def test_create(self):
        v_data = {
            'name': 'NPS Survey',
            'text': 'Welcome',
            'text_enabled': True,
            'question': 'How do you rate us?',
            'contra': {
                'text': 'Hello World!',
            },
            'message': 'Thanks you',
            'business': self.business,
        }
        serializer = NPSSerializerV11()

        nps_survey = serializer.create(v_data)

        self.assertIsInstance(nps_survey, NPSSurvey)
        self.assertEqual(nps_survey.name, v_data['name'])
        self.assertEqual(nps_survey.text, v_data['text'])
        self.assertEqual(nps_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(nps_survey.question, v_data['question'])
        self.assertEqual(nps_survey.contra.text, v_data['contra']['text'])
        self.assertEqual(nps_survey.message, v_data['message'])
        self.assertEqual(nps_survey.business, v_data['business'])

    def test_update(self):
        v_data = {
            'name': 'NPS Survey',
            'text': 'Welcome',
            'text_enabled': True,
            'question': 'How do you rate us?',
            'contra': {
                'text': 'Hello World!',
                'required': False,
            },
            'message': 'Thanks you',
        }
        instance = NPSService.get_nps_survey_by_id(1)
        instance.contra = MultipleChoiceService.create(text=self.id())
        serializer = NPSSerializerV11()

        nps_survey = serializer.update(instance, v_data)

        self.assertIsInstance(nps_survey, NPSSurvey)
        self.assertEqual(nps_survey.name, v_data['name'])
        self.assertEqual(nps_survey.text, v_data['text'])
        self.assertEqual(nps_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(nps_survey.question, v_data['question'])
        self.assertEqual(nps_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(nps_survey.contra.required)
        self.assertEqual(nps_survey.message, v_data['message'])
        self.assertEqual(nps_survey.business, instance.business)

    def test_update_contra_is_none(self):
        v_data = {
            'name': 'NPS Survey',
            'text': 'Welcome',
            'text_enabled': True,
            'question': 'How do you rate us?',
            'contra': {
                'text': 'Hello World!',
                'required': False,
            },
            'message': 'Thanks you',
        }
        instance = NPSService.get_nps_survey_by_id(1)
        serializer = NPSSerializerV11()

        nps_survey = serializer.update(instance, v_data)

        self.assertIsInstance(nps_survey, NPSSurvey)
        self.assertEqual(nps_survey.name, v_data['name'])
        self.assertEqual(nps_survey.text, v_data['text'])
        self.assertEqual(nps_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(nps_survey.question, v_data['question'])
        self.assertEqual(nps_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(nps_survey.contra.required)
        self.assertEqual(nps_survey.message, v_data['message'])
        self.assertEqual(nps_survey.business, instance.business)


class NPSRespondSerializerTestCase(TestCase):
    fixtures = ['nps']

    def setUp(self):
        self.customer = Customer.objects.create()
        self.serializer = NPSRespondSerializer()

    def test_to_representation(self):
        data = {
            'score': 10,
            'customer': {
                "client_id": self.customer.client_id
            }
        }

        serializer = NPSRespondSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        instance = NPSResponse(score=10, customer_uuid=self.customer.uuid)
        representation = serializer.to_representation(instance)
        self.assertEqual(representation['client_id'], data['customer']['client_id'])
        self.assertEqual(representation['score'], data['score'])

    def test_create_return_nps_object(self):
        nps = NPSService.get_nps_survey_by_id(1)
        data = {
            "survey_uuid": str(nps.uuid),
            "customer": self.customer,
            "score": 1
        }

        created_nps_response = self.serializer.create(data)

        self.assertEqual(created_nps_response.score, data['score'])
        self.assertEqual(created_nps_response.survey_uuid, data['survey_uuid'])
        self.assertEqual(created_nps_response.customer_uuid, data['customer'].uuid)

    def test_create_return_none(self):
        invalid_uuid = "f6fd2c9a-1e53-4722-a1c1-c2f79ffb8be4"
        data = {
            "survey_uuid": invalid_uuid,
            "customer": self.customer,
            "score": 10
        }

        created_nps_response = self.serializer.create(data)
        self.assertIsNone(created_nps_response)
