#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.forms import model_to_dict
from django.http import Http404
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from upkook_core.businesses.models import Business, Settings
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService

from cx_metrics.multiple_choices.models import Option, MultipleChoice
from cx_metrics.multiple_choices.services import MultipleChoiceService
from cx_metrics.surveys.models import Survey
from ..models import NPSSurvey, NPSResponse
from ..serializers import NPSSerializer, NPSSerializerV11, NPSRespondSerializer, NPSRespondSerializerV11
from ..services import NPSService


class NPSSerializerTestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps']

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
        survey = Survey(
            type='TEST',
            name='name',
            business=BusinessService.get_business_by_id(1)
        )
        serializer = NPSSerializer()
        self.assertRaises(Http404, serializer.to_representation, survey)


class NPSSerializerV11TestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps']

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

    def test_serializer_with_survey_instance(self):
        instance = NPSService.get_nps_survey_by_id(1)
        serializer = NPSSerializerV11(instance.survey)
        fields = ('name', 'text', 'text_enabled', 'question', 'message')
        expected = model_to_dict(instance, fields=fields)
        expected.update({
            'id': str(instance.uuid),
            'type': instance.type,
            'url': instance.url,
            'contra_reason': None,
        })
        self.assertDictEqual(serializer.to_representation(instance.survey), expected)


class NPSRespondSerializerTestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps']

    def setUp(self):
        nps = NPSService.get_nps_survey_by_id(1)
        self.serializer = NPSRespondSerializer(survey=nps)

    def test_to_representation(self):
        nps = NPSSurvey.objects.first()
        customer = CustomerService.create_customer()
        data = {
            "customer": {
                "client_id": customer.client_id
            },
            "score": 10,
        }

        serializer = NPSRespondSerializer(data=data, survey=nps)
        self.assertTrue(serializer.is_valid())

        instance = NPSResponse(score=10, customer_uuid=customer.uuid)
        representation = serializer.to_representation(instance)
        self.assertEqual(representation['client_id'], data['customer']['client_id'])
        self.assertEqual(representation['score'], data['score'])

    def test_create_return_nps_object(self):
        customer = CustomerService.create_customer()
        data = {
            "customer": {
                "client_id": customer.client_id
            },
            "score": 10
        }

        created_nps_response = self.serializer.create(data)

        self.assertEqual(created_nps_response.score, data['score'])
        self.assertEqual(created_nps_response.survey_uuid, self.serializer.survey.uuid)
        self.assertEqual(created_nps_response.customer.client_id, data['customer']['client_id'])

    def test_create_return_none(self):
        nps = NPSSurvey(
            name='test',
            business=Business.objects.first(),
            text='text',
            question="question",
            message="message",
        )
        customer = CustomerService.create_customer()
        serializer = NPSRespondSerializer(survey=nps)
        data = {
            "customer": {
                "client_id": customer.client_id
            },
            "score": 10
        }

        created_nps_response = serializer.create(data)
        self.assertIsNone(created_nps_response)


class NPSRespondSerializerV11TestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'multiple_choices', 'nps']

    def test_create_anonymous(self):
        nps_survey = NPSService.get_nps_survey_by_id(1)
        mc = MultipleChoiceService.get_by_id(1)
        nps_survey.contra = mc
        nps_survey.save()
        customer = CustomerService.create_customer()
        option = Option.objects.first()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id
            },
            'score': 5,
            'options': [option.id],

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)
        response = serializer.create(v_data)

        self.assertIsInstance(response, NPSResponse)
        self.assertEqual(response.survey_uuid, v_data['survey_uuid'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])
        self.assertEqual(response.score, v_data['score'])

    def test_create_with_email(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_EMAIL)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/68.0"
        nps_survey = NPSService.get_nps_survey_by_id(1)
        mc = MultipleChoiceService.get_by_id(1)
        nps_survey.contra = mc
        nps_survey.save()
        customer = CustomerService.create_customer(user_agent=user_agent)
        option = Option.objects.first()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
                "email": "test@test.com"
            },
            'score': 5,
            'options': [option.id],
            'user_agent': user_agent,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)
        response = serializer.create(v_data)

        self.assertIsInstance(response, NPSResponse)
        self.assertEqual(response.customer.email, "test@test.com")
        self.assertEqual(response.score, v_data['score'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_create_with_email_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_EMAIL)
        nps_survey = NPSService.get_nps_survey_by_id(1)

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'score': 10,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)

        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_create_with_mobile_number(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_MOBILE_NUMBER)
        nps_survey = NPSService.get_nps_survey_by_id(1)
        mc = MultipleChoiceService.get_by_id(1)
        nps_survey.contra = mc
        nps_survey.save()
        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
                "mobile_number": "9121234567"
            },
            'score': 10,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)
        response = serializer.create(v_data)

        self.assertIsInstance(response, NPSResponse)
        self.assertEqual(response.customer.mobile_number, "+989121234567")
        self.assertEqual(response.score, v_data['score'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_create_with_mobile_number_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_MOBILE_NUMBER)
        nps_survey = NPSService.get_nps_survey_by_id(1)

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'score': 10,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)

        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_create_with_bizz_user_id(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_BIZZ_USER_ID)
        nps_survey = NPSService.get_nps_survey_by_id(1)
        mc = MultipleChoiceService.get_by_id(1)
        nps_survey.contra = mc
        nps_survey.save()
        customer = CustomerService.create_customer()
        bizz_user_id = "test_bizz_user_id"
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
                "bizz_user_id": bizz_user_id
            },
            'score': 10,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)
        response = serializer.create(v_data)

        self.assertIsInstance(response, NPSResponse)
        self.assertEqual(response.customer.bizz_user_id, bizz_user_id)
        self.assertEqual(response.score, v_data['score'])
        self.assertEqual(response.customer.client_id, v_data['customer']['client_id'])

    def test_create_with_bizz_user_id_validation_error(self):
        business = BusinessService.get_business_by_id(1)
        Settings.objects.create(business=business, identify_by=Settings.IDENTIFY_BY_BIZZ_USER_ID)
        nps_survey = NPSService.get_nps_survey_by_id(1)

        customer = CustomerService.create_customer()
        v_data = {
            'survey_uuid': nps_survey.uuid,
            'customer': {
                "client_id": customer.client_id,
            },
            'score': 10,

        }
        serializer = NPSRespondSerializerV11(survey=nps_survey)

        self.assertRaises(ValidationError, serializer.create, v_data)

    def test_validate_options_raise_validation_error_survey_and_contra_not_related(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [1000],
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertRaises(ValidationError, serializer.validate_options, data['options'])

    def test_validate_options_raise_validation_error_survey_has_no_contra(self):
        nps_survey = NPSSurvey.objects.first()
        nps_survey.contra = None
        nps_survey.save()
        option = Option.objects.first()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [option.id],
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_contra_not_enabled(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        contra.enabled = False
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': [1],
        }

        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertIsNone(serializer.validate_options(data['options']))

    def test_validate_options_none_value(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        contra.enabled = True
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': None
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertRaises(ValidationError, serializer.validate, data)

    def test_validate_options_empty_list(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        contra.enabled = True
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            },
            'options': []
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertRaises(ValidationError, serializer.validate, data)

    def test_validate_raise_validation_error(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        contra.enabled = True
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 1,
            'customer': {
                'client_id': 1
            }
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        self.assertRaises(ValidationError, serializer.validate, data)

    def test_validate_rate_gte_9(self):
        nps_survey = NPSSurvey.objects.first()
        contra = MultipleChoice.objects.first()
        contra.enabled = True
        nps_survey.contra = contra
        nps_survey.save()
        data = {
            'score': 10,
            'customer': {
                'client_id': 1
            },
            'options': [1]
        }
        serializer = NPSRespondSerializerV11(data=data, survey=nps_survey)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data['options'], [])
