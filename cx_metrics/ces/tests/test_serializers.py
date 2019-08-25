#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService

from cx_metrics.ces.models import CESSurvey, CESResponse
from cx_metrics.multiple_choices.models import Option
from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..serializers import CESSerializer, CESRespondSerializer
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
        instance = CESService.get_ces_survey_by_id(1)
        instance.contra = MultipleChoiceService.create(text=self.id())
        serializer = CESSerializer()

        ces_survey = serializer.update(instance, v_data)

        self.assertIsInstance(ces_survey, CESSurvey)
        self.assertEqual(ces_survey.name, v_data['name'])
        self.assertEqual(ces_survey.text, v_data['text'])
        self.assertEqual(ces_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(ces_survey.question, v_data['question'])
        self.assertEqual(ces_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(ces_survey.contra.required)
        self.assertEqual(ces_survey.message, v_data['message'])

    def test_update_ces_without_contra(self):
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
        instance = CESService.get_ces_survey_by_id(1)
        instance.contra = None
        serializer = CESSerializer()

        ces_survey = serializer.update(instance, v_data)

        self.assertIsInstance(ces_survey, CESSurvey)
        self.assertEqual(ces_survey.name, v_data['name'])
        self.assertEqual(ces_survey.text, v_data['text'])
        self.assertEqual(ces_survey.text_enabled, v_data['text_enabled'])
        self.assertEqual(ces_survey.question, v_data['question'])
        self.assertEqual(ces_survey.contra.text, v_data['contra']['text'])
        self.assertFalse(ces_survey.contra.required)
        self.assertEqual(ces_survey.message, v_data['message'])

    def test_serializer_with_survey_object(self):
        instance = CESService.get_ces_survey_by_id(1)
        serializer = CESSerializer(instance=instance.survey)
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


class CESRespondSerializerTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def test_create_anonymous(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        option = Option.objects.first()
        v_data = {
            'survey_uuid': ces_survey.uuid,
            'customer': {
                "client_id": customer.client_id
            },
            'rate': 2,
            'options': [option.id],
        }
        serializer = CESRespondSerializer(survey=ces_survey)
        response = serializer.create(v_data)
        self.assertIsInstance(response, CESResponse)
        self.assertEqual(response.survey_uuid, v_data['survey_uuid'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])
        self.assertEqual(response.rate, v_data['rate'])

    def test_create_with_email(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        option = Option.objects.first()
        v_data = {
            'survey_uuid': ces_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
                "email": "test@test.com"
            },
            'rate': 2,
            'options': [option.id],
        }
        serializer = CESRespondSerializer(survey=ces_survey)
        response = serializer.create(v_data)
        self.assertIsInstance(response, CESResponse)
        self.assertEqual(response.survey_uuid, v_data['survey_uuid'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])
        self.assertEqual(response.rate, v_data['rate'])
        self.assertEqual(response.customer.email, v_data['customer']['email'])

    def test_create_with_mobile_number(self):
        ces = CESService.get_ces_survey_by_id(1)

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': ces.uuid,
            'customer': {
                "client_id": customer.client_id,
                "mobile_number": "9121234567"
            },
            'rate': 3,

        }
        serializer = CESRespondSerializer(survey=ces)
        response = serializer.create(v_data)

        self.assertIsInstance(response, CESResponse)
        self.assertEqual(response.customer.mobile_number, "+989121234567")
        self.assertEqual(response.rate, v_data['rate'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_validate_options(self):
        ces_survey = CESSurvey.objects.first()
        option = Option.objects.first()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [option.id],
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        value = serializer.validate_options(data['options'])
        self.assertListEqual(data['options'], value)

    def test_validate_options_survey_and_contra_not_related(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [1000]
        }

        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertRaises(ValidationError, serializer.validate_options, data['options'])

    def test_validate_options_survey_has_no_contra(self):
        ces_survey = CESSurvey.objects.first()
        ces_survey.contra = None
        ces_survey.save()
        option = Option.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [option.id]
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_contra_not_enabled(self):
        ces_survey = CESSurvey.objects.first()
        ces_survey.contra.enabled = False
        ces_survey.save()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [1]
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_none_value(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': None
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_empty_list(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': []
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 3,
            'customer': {
                'client_id': 1
            }
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)

        attrs = serializer.validate(data)
        self.assertDictEqual(data, attrs)

    def test_validate_raise_validation_error(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 1,
            'customer': {
                'client_id': 1
            }
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        self.assertRaises(ValidationError, serializer.validate, data)

    def test_validate_rate_gte_9(self):
        ces_survey = CESSurvey.objects.first()
        data = {
            'rate': 3,
            'customer': {
                'client_id': 1
            },
            'options': [1]
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data['options'], [])

    def test_to_representation(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        data = {
            'rate': 3,
            'customer': {
                'client_id': customer.client_id
            }
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)

        self.assertTrue(serializer.is_valid())

        instance = CESResponse(rate=3, customer_uuid=customer.uuid)
        representation = serializer.to_representation(instance)
        self.assertEqual(data['customer']['client_id'], representation['client_id'])

    def test_validate_rate(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        data = {
            'rate': 4,
            'customer': {
                'client_id': customer.client_id
            }
        }
        serializer = CESRespondSerializer(data=data, survey=ces_survey)

        self.assertRaises(ValidationError, serializer.validate_rate, data['rate'])
