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

from ..services.csat import CSATSurvey

from cx_metrics.csat.services.csat import CSATService


class CSATViewTestBase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams', 'multiple_choices', 'csat']

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
