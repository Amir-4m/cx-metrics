#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.test import TestCase, override_settings
from django.urls import reverse
from mock import patch
from django.utils.encoding import force_text
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.csat.serializers import CSATInsightSerializer
from cx_metrics.multiple_choices.models import MultipleChoice
from cx_metrics.multiple_choices.services.multiple_choice import OptionResponseService
from ..services.csat import CSATSurvey

from cx_metrics.csat.services.csat import CSATService


class CSATViewTestBase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams', 'csat']

    def setUp(self):
        super(CSATViewTestBase, self).setUp()
        User = get_user_model()
        user = User.objects.first()
        self.member = MemberService.get_member_by_id(1)
        self.business = self.member.business

        self.client = AuthClient()
        credentials = {
            User.USERNAME_FIELD: user.email,
            'password': 'test_password',
            'business': self.business.username,
        }
        self.client.login(**credentials)

        codenames = ['add_csatsurvey', 'change_csatsurvey', 'view_csatsurvey']
        self.group = self.give_member_permissions(self.member, app_label='csat', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)


class CSATSurveyTestCase(CSATViewTestBase):
    def test_post(self):
        data = {
            'id': self.id(),
            'type': self.id(),
            "name": "CSAT_name",
            "text": "CSAT_text",
            "text_enabled": True,
            "question": "CSAT_question",
            "contra_reason": {
                "text": "Why not?",
                "options": [
                    {"text": "Option 1", "order": 1},
                    {"text": "Option 2", "order": 2},
                ]
            },
            "message": "NPS_message",
            "scale": CSATSurvey.SCALE_1_TO_3,
        }

        url = reverse('cx-csat:create')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )

        response_data = json.loads(force_text(response.content))

        csat = CSATService.get_csat_survey_by_uuid(response_data['id'])

        contra_data = model_to_dict(
            csat.contra,
            ('type', 'text', 'enabled', 'required', 'other_enabled')
        )
        contra_data.update({'options': []})
        for option in csat.contra.options.order_by('order'):
            option_data = model_to_dict(option, ('id', 'text', 'enabled', 'order'))
            contra_data['options'].append(option_data)

        data.update({
            'id': str(csat.uuid),
            'url': csat.url,
            'type': csat.type,
            'contra_reason': contra_data,
        })

        self.assertEqual(csat.business.pk, self.business.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(data, response_data)

    def test_post_invalid_data(self):
        data = {'name': 'name'}
        url = reverse('cx-csat:create')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['This field is required.'], response_data['text'])

    def test_get(self):
        csat = CSATService.create_csat_survey(
            name="name",
            business=self.business,
            text="text",
            question="question",
            message="message"

        )

        url = reverse('cx-csat:detail', kwargs={'uuid': str(csat.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(csat.uuid),
            'type': csat.type,
            'name': 'name',
            'text': 'text',
            'text_enabled': True,
            'question': 'question',
            'contra_reason': None,
            'message': 'message',
            'scale': CSATSurvey.SCALE_1_TO_3,
            'url': csat.url,
        }
        response_data = json.loads(force_text(response.content))

        self.assertDictEqual(response_data, expected_data)

    def test_put(self):
        csat = CSATService.get_csat_survey_by_id(1)

        data = {
            'id': self.id(),
            'type': self.id(),
            "name": "Changed-name",
            "text": "Changed-text",
            "text_enabled": False,
            "question": "Changed-question",
            "contra_reason": {
                "text": "Changed",
                "options": [
                    {"text": "Option 1", "order": 1},
                    {"text": "Option 2", "order": 2},
                ]
            },
            "message": "Changed Message",
            "scale": CSATSurvey.SCALE_1_TO_3,
        }
        url = reverse('cx-csat:detail', kwargs={'uuid': str(csat.uuid)})
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        contra_data = model_to_dict(
            csat.contra,
            ('type', 'text', 'enabled', 'required', 'other_enabled')
        )
        contra_data.update({'options': []})
        for option in csat.contra.options.order_by('order'):
            option_data = model_to_dict(option, ('id', 'text', 'enabled', 'order'))
            contra_data['options'].append(option_data)

        data.update({
            'id': str(csat.uuid),
            'url': csat.url,
            'type': csat.type,
            'contra_reason': contra_data,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(data, response_data)


class CSATResponseAPIViewTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def test_get_survey_none(self):
        none_uuid = "76440add-0243-4eb0-a985-7c573bb2d101"
        data = {
            "rate": 1,
            "customer": {
                "client_id": 1
            }
        }

        url = reverse('cx-csat:responses-create', kwargs={'uuid': none_uuid})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_serializer(self):
        csat = CSATSurvey.objects.first()
        data = {
            "rate": 3,
            "customer": {
                "client_id": 1
            }
        }
        url = reverse('cx-csat:responses-create', kwargs={'uuid': csat.uuid})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CSATInsightsViewTestCase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams', 'csat']

    def setUp(self):
        super(CSATInsightsViewTestCase, self).setUp()
        User = get_user_model()
        user = User.objects.first()
        self.member = MemberService.get_member_by_id(1)
        self.business = self.member.business

        self.client = AuthClient()
        credentials = {
            User.USERNAME_FIELD: user.email,
            'password': 'test_password',
            'business': self.business.username,
        }
        self.client.login(**credentials)

        codenames = ['add_csatsurvey', 'change_csatsurvey', 'view_csatsurvey']
        self.group = self.give_member_permissions(self.member, app_label='csat', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)

    def test_get(self):
        csat = CSATSurvey.objects.first()
        csat.refresh_from_db()
        url = reverse('cx-csat:insights', kwargs={'uuid': str(csat.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(csat.uuid),
            'name': csat.name,
            'scale': csat.scale,
            'contra_options': csat.contra_response_option_texts
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(force_text(response.content))
        for item in response_data['contra_options']:
            option = OptionResponseService.get_option_text_by_text(item['text'])
            self.assertEqual(option.text, item['text'])

        expected_data.pop('contra_options')
        response_data.pop('contra_options')
        self.assertDictEqual(expected_data, response_data)

    @ override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_get_cached(self):
        csat = CSATService.get_csat_survey_by_id(1)
        contra = MultipleChoice.objects.first()
        csat.contra = contra
        csat.save()

        url = reverse('cx-csat:insights', kwargs={'uuid': str(csat.uuid)})
        self.client.get(url)

        with patch.object(CSATInsightSerializer, 'to_representation') as mock_to_representation:
            response = self.client.get(url)
            self.assertFalse(mock_to_representation.called)

        response_data = json.loads(force_text(response.content))
        expected_data = {
            'id': str(csat.uuid),
            'name': csat.name,
            'scale': csat.scale,
            'contra_options': csat.contra_response_option_texts
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response_data['contra_options']:
            option = OptionResponseService.get_option_text_by_text(item['text'])
            self.assertEqual(option.text, item['text'])

        expected_data.pop('contra_options')
        response_data.pop('contra_options')
        self.assertDictEqual(expected_data, response_data)
