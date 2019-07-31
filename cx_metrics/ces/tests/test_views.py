#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_text
from mock import patch
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.ces.serializers import CESInsightSerializer
from cx_metrics.multiple_choices.models import MultipleChoice
from cx_metrics.multiple_choices.services.multiple_choice import OptionResponseService
from ..services import CESService
from ..models import CESSurvey


class CESViewTestBase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams', 'ces']

    def setUp(self):
        super(CESViewTestBase, self).setUp()
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

        codenames = ['add_cessurvey', 'change_cessurvey', 'view_cessurvey']
        self.group = self.give_member_permissions(self.member, app_label='ces', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)


class CESSurveyTestCase(CESViewTestBase):
    def test_post(self):
        data = {
            'id': self.id(),
            'type': self.id(),
            "name": "CES_name",
            "text": "CES_text",
            "text_enabled": True,
            "question": "CES_question",
            "contra_reason": {
                "text": "Why not?",
                "options": [
                    {"text": "Option 1", "order": 1},
                    {"text": "Option 2", "order": 2},
                ]
            },
            "message": "NPS_message",
            "scale": CESSurvey.SCALE_1_TO_3,
        }

        url = reverse('cx-ces:create')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )

        response_data = json.loads(force_text(response.content))

        ces = CESService.get_ces_survey_by_uuid(response_data['id'])

        contra_data = model_to_dict(
            ces.contra,
            ('type', 'text', 'enabled', 'required', 'other_enabled')
        )
        contra_data.update({'options': []})
        for option in ces.contra.options.order_by('order'):
            option_data = model_to_dict(option, ('id', 'text', 'enabled', 'order'))
            contra_data['options'].append(option_data)

        data.update({
            'id': str(ces.uuid),
            'url': ces.url,
            'type': ces.type,
            'contra_reason': contra_data,
        })

        self.assertEqual(ces.business.pk, self.business.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(data, response_data)

    def test_post_invalid_data(self):
        data = {'name': 'name'}
        url = reverse('cx-ces:create')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['This field is required.'], response_data['text'])

    def test_get(self):
        ces = CESService.create_ces_survey(
            name="name",
            business=self.business,
            text="text",
            question="question",
            message="message"

        )

        url = reverse('cx-ces:detail', kwargs={'uuid': str(ces.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(ces.uuid),
            'type': ces.type,
            'name': 'name',
            'text': 'text',
            'text_enabled': True,
            'question': 'question',
            'contra_reason': None,
            'message': 'message',
            'scale': CESSurvey.SCALE_1_TO_3,
            'url': ces.url,
        }
        response_data = json.loads(force_text(response.content))

        self.assertDictEqual(response_data, expected_data)

    def test_put(self):
        ces = CESService.get_ces_survey_by_id(1)

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
            "scale": CESSurvey.SCALE_1_TO_3,
        }
        url = reverse('cx-ces:detail', kwargs={'uuid': str(ces.uuid)})
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        contra_data = model_to_dict(
            ces.contra,
            ('type', 'text', 'enabled', 'required', 'other_enabled')
        )
        contra_data.update({'options': []})
        for option in ces.contra.options.order_by('order'):
            option_data = model_to_dict(option, ('id', 'text', 'enabled', 'order'))
            contra_data['options'].append(option_data)

        data.update({
            'id': str(ces.uuid),
            'url': ces.url,
            'type': ces.type,
            'contra_reason': contra_data,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(data, response_data)


class CESResponseAPIViewTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def test_get_survey_none(self):
        none_uuid = "76440add-0243-4eb0-a985-7c573bb2d101"
        data = {
            "rate": 1,
            "customer": {
                "client_id": 1
            }
        }

        url = reverse('cx-ces:responses-create', kwargs={'uuid': none_uuid})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_serializer(self):
        ces = CESSurvey.objects.first()
        data = {
            "rate": 3,
            "customer": {
                "client_id": 1
            }
        }
        url = reverse('cx-ces:responses-create', kwargs={'uuid': ces.uuid})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CESInsightsViewTestCase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams', 'ces']

    def setUp(self):
        super(CESInsightsViewTestCase, self).setUp()
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

        codenames = ['add_cessurvey', 'change_cessurvey', 'view_cessurvey']
        self.group = self.give_member_permissions(self.member, app_label='ces', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)

    def test_get(self):
        ces = CESSurvey.objects.first()
        ces.refresh_from_db()
        url = reverse('cx-ces:insights', kwargs={'uuid': str(ces.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(ces.uuid),
            'name': ces.name,
            'scale': ces.scale,
            'contra_options': ces.contra_response_option_texts
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(force_text(response.content))
        for item in response_data['contra_options']:
            option = OptionResponseService.get_option_text_by_text(item['text'])
            self.assertEqual(option.text, item['text'])

        expected_data.pop('contra_options')
        response_data.pop('contra_options')
        self.assertDictEqual(expected_data, response_data)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_get_cached(self):
        ces = CESService.get_ces_survey_by_id(1)
        contra = MultipleChoice.objects.first()
        ces.contra = contra
        ces.save()

        url = reverse('cx-ces:insights', kwargs={'uuid': str(ces.uuid)})
        self.client.get(url)

        with patch.object(CESInsightSerializer, 'to_representation') as mock_to_representation:
            response = self.client.get(url)
            self.assertFalse(mock_to_representation.called)

        response_data = json.loads(force_text(response.content))
        expected_data = {
            'id': str(ces.uuid),
            'name': ces.name,
            'scale': ces.scale,
            'contra_options': ces.contra_response_option_texts
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response_data['contra_options']:
            option = OptionResponseService.get_option_text_by_text(item['text'])
            self.assertEqual(option.text, item['text'])

        expected_data.pop('contra_options')
        response_data.pop('contra_options')
        self.assertDictEqual(expected_data, response_data)
