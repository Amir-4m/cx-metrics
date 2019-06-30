#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_text
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.industries.models import Industry
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.surveys_defaults.models import DefaultOption


class DefaultOptionAPIViewTestCase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams']

    def setUp(self):
        super(DefaultOptionAPIViewTestCase, self).setUp()
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

        codenames = ['add_defaultoption', 'change_defaultoption', 'view_defaultoption']
        self.group = self.give_member_permissions(self.member, app_label='surveys_defaults', codenames=codenames)

    def tearDown(self):
        self.member.groups.all().delete()
        self.remove_member_permissions(self.member, self.group)

    def test_get(self):
        default_option = DefaultOption.objects.create(
            industry=Industry.objects.first(),
            survey_type='nps',
            question_type='contra',
            text='text',
            order=1,
        )
        url = reverse('survey-defaults:list', kwargs={'survey_type': 'nps'})
        response = self.client.get(url)
        response_data = json.loads(force_text(response.content))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response_data, [{
            'text': default_option.text,
            'question_type': default_option.question_type,
            'order': default_option.order
        }])
