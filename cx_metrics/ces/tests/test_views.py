#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_text
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

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
