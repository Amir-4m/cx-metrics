#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_text
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from ..models import Survey


class SurveyAPIViewTestCase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams']

    def setUp(self):
        super(SurveyAPIViewTestCase, self).setUp()

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

        codenames = ['add_survey', 'change_survey', 'view_survey']
        self.group = self.give_member_permissions(self.member, app_label='surveys', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)

    def test_get(self):
        survey = Survey.objects.create(
            type='test',
            name='SurveyAPIViewTestCase.test_get',
            business=self.business,
        )

        response = self.client.get(reverse('cx-surveys:list'))
        response_data = json.loads(force_text(response.content))
        results = response_data['results']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response_data['previous'])
        self.assertIsNone(response_data['next'])
        self.assertEqual(len(results), 1)
        self.assertDictEqual(results[0], {
            'id': str(survey.uuid),
            'type': 'test',
            'name': survey.name,
            'url': survey.url,
        })
