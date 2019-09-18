#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from upkook_core.businesses.models import Settings
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService

from cx_metrics.csat.models import CSATResponse
from cx_metrics.multiple_choices.models import Option
from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..serializers import CSATSerializer, CSATRespondSerializer
from ..services.csat import CSATService, CSATSurvey


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


class CSATRespondSerializerTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def test_create_anonymous(self):
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        option = Option.objects.first()
        v_data = {
            'survey_uuid': csat_survey.uuid,
            'customer': {
                "client_id": customer.client_id
            },
            'rate': 2,
            'options': [option.id],
        }
        serializer = CSATRespondSerializer(survey=csat_survey)
        response = serializer.create(v_data)
        self.assertIsInstance(response, CSATResponse)
        self.assertEqual(response.survey_uuid, v_data['survey_uuid'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])
        self.assertEqual(response.rate, v_data['rate'])

    def test_create_with_email(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_EMAIL)
        csat_survey = CSATSurvey.objects.first()

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': csat_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
                "email": "test@test.com"
            },
            'rate': 3,
        }
        serializer = CSATRespondSerializer(survey=csat_survey)
        response = serializer.create(v_data)
        self.assertIsInstance(response, CSATResponse)
        self.assertEqual(response.survey_uuid, v_data['survey_uuid'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])
        self.assertEqual(response.customer.email, v_data['customer']['email'])
        self.assertEqual(response.rate, v_data['rate'])

    def test_create_with_email_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_EMAIL)
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': csat_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'rate': 3,
        }
        serializer = CSATRespondSerializer(survey=csat_survey)
        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_create_with_mobile_number(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_MOBILE_NUMBER)
        csat = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': csat.uuid,
            'customer': {
                "client_id": customer.client_id,
                "mobile_number": "9121234567"
            },
            'rate': 3,

        }
        serializer = CSATRespondSerializer(survey=csat)
        response = serializer.create(v_data)

        self.assertIsInstance(response, CSATResponse)
        self.assertEqual(response.customer.mobile_number, "+989121234567")
        self.assertEqual(response.rate, v_data['rate'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_create_with_mobile_number_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_MOBILE_NUMBER)
        csat = CSATSurvey.objects.first()

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': csat.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'rate': 3,

        }
        serializer = CSATRespondSerializer(survey=csat)
        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_create_with_bizz_user_id(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_BIZZ_USER_ID)
        csat = CSATSurvey.objects.first()

        customer = CustomerService.create_customer()

        bizz_user_id = "test_bizz_user_id"
        v_data = {
            'survey_uuid': csat.uuid,
            'customer': {
                "client_id": customer.client_id,
                "bizz_user_id": bizz_user_id
            },
            'rate': 3,

        }
        serializer = CSATRespondSerializer(survey=csat)
        response = serializer.create(v_data)

        self.assertIsInstance(response, CSATResponse)
        self.assertEqual(response.customer.bizz_user_id, bizz_user_id)
        self.assertEqual(response.rate, v_data['rate'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_create_with_bizz_user_id_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_BIZZ_USER_ID)
        csat = CSATSurvey.objects.first()

        customer = CustomerService.create_customer()

        v_data = {
            'survey_uuid': csat.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'rate': 3,

        }
        serializer = CSATRespondSerializer(survey=csat)
        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_validate_options(self):
        csat_survey = CSATSurvey.objects.first()
        option = Option.objects.first()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [option.id],
            'rate': 1

        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        value = serializer.validate_options(data['options'])
        self.assertListEqual(data['options'], value)

    def test_validate_options_survey_and_contra_not_related(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [1000]
        }

        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertRaisesMessage(
            ValidationError,
            "Contra option and Survey not related!",
            serializer.is_valid,
            raise_exception=True
        )

    def test_validate_options_survey_has_no_contra(self):
        csat_survey = CSATSurvey.objects.first()
        csat_survey.contra = None
        csat_survey.save()
        option = Option.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [option.id]
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_contra_not_enabled(self):
        csat_survey = CSATSurvey.objects.first()
        csat_survey.contra.enabled = False
        csat_survey.save()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': [1]
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_none_value(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': None
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_empty_list(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 2,
            'customer': {
                'client_id': 1
            },
            'options': []
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 3,
            'customer': {
                'client_id': 1
            }
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)

        attrs = serializer.validate(data)
        self.assertDictEqual(data, attrs)

    def test_validate_raise_validation_error(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 1,
            'customer': {
                'client_id': 1
            }
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        self.assertRaises(ValidationError, serializer.validate, data)

    def test_validate_rate_gte_9(self):
        csat_survey = CSATSurvey.objects.first()
        data = {
            'rate': 3,
            'customer': {
                'client_id': 1
            },
            'options': [1]
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data['options'], [])

    def test_to_representation(self):
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        data = {
            'rate': 3,
            'customer': {
                'client_id': customer.client_id
            }
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)

        self.assertTrue(serializer.is_valid())

        instance = CSATResponse(rate=3, customer_uuid=customer.uuid)
        representation = serializer.to_representation(instance)
        self.assertEqual(data['customer']['client_id'], representation['client_id'])

    def test_validate_rate(self):
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        data = {
            'rate': 4,
            'customer': {
                'client_id': customer.client_id
            }
        }
        serializer = CSATRespondSerializer(data=data, survey=csat_survey)

        self.assertRaises(ValidationError, serializer.validate_rate, data['rate'])
