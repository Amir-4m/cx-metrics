#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json
from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_text
from rest_framework import status
from rest_framework.test import APIClient
from upkook_core.auth.tests.client import AuthClient
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin
from upkook_core.industries.services import IndustryService
from upkook_core.businesses.services.business import BusinessService
from upkook_core.businesses.models import Business

from ..models import Survey
from ..serializers import SurveySerializer


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


class SurveyFactoryAPIViewTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams']

    def setUp(self):
        super(SurveyFactoryAPIViewTestCase, self).setUp()
        self.client = APIClient()
        self.member = MemberService.get_member_by_id(1)

    def test_get(self):
        survey = Survey.objects.create(
            type='test',
            name='SurveyFactoryAPIViewTestCase.test_get',
            business=self.member.business,
        )

        url = reverse('cx-surveys:retrieve', kwargs={'uuid': str(survey.uuid)})
        response = self.client.get(url)
        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response_data, {
            'id': str(survey.uuid),
            'type': 'test',
            'name': survey.name,
            'url': survey.url,
        })

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_get_cached(self):
        survey = Survey.objects.create(
            type='test',
            name='SurveyFactoryAPIViewTestCase.test_get_cache',
            business=self.member.business,
        )

        url = reverse('cx-surveys:retrieve', kwargs={'uuid': str(survey.uuid)})
        self.client.get(url)

        with patch.object(SurveySerializer, 'to_representation') as mock_to_representation:
            response = self.client.get(url)
            self.assertFalse(mock_to_representation.called)

        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response_data, {
            'id': str(survey.uuid),
            'type': 'test',
            'name': survey.name,
            'url': survey.url,
        })

    def test_get_business_is_not_active(self):
        new_industry = IndustryService.create_industry('Industry', '')
        new_business = BusinessService.create_business(
            username=self.id(),
            name='business',
            industry=new_industry,
            size=Business.SIZE_1_TO_5,
            domain='domain',
            is_active=False,
        )
        survey = Survey.objects.create(
            type='test',
            name='SurveyFactoryAPIViewTestCase.test_get',
            business=new_business,
        )

        url = reverse('cx-surveys:retrieve', kwargs={'uuid': str(survey.uuid)})
        response = self.client.get(url)
        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response_data, {'detail': 'Not found.'})
