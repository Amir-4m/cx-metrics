#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json
from http.cookies import SimpleCookie

import mock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_text
from mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from upkook_core.auth.tests.client import AuthClient
from upkook_core.businesses.models import Business
from upkook_core.businesses.services.business import BusinessService
from upkook_core.customers.models import Client
from upkook_core.industries.services import IndustryService
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.nps.services import NPSService
from ..models import Survey
from ..serializers import SurveySerializer


class MockRequest(object):
    def __init__(self, meta, cookies, data={}):
        self.META = meta
        self.COOKIES = cookies
        self.data = data


class MockCookie(object):
    def __init__(self, value, max_age, path, domain, secure, httponly):
        self.value = value
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.httponly = httponly


class MockResponse(object):
    def __init__(self):
        self.cookies = {}

    def set_cookie(self, key, *args, **kwargs):
        self.cookies.update({key: MockCookie(*args, **kwargs)})

    def get_cookie(self, key):
        return self.cookies.get(key)


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


class SurveyResponseAPIViewTestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps', 'customers']

    @mock.patch('upkook_core.customers.models.generate_client_id')
    def test_get_data_cookie_not_exist(self, mock_generate_client_id):
        client_id = "test"
        mock_generate_client_id.return_value = client_id
        nps = NPSService.get_nps_survey_by_id(1)
        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        data = {
            "score": 10,
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )
        response_data = json.loads(force_text(response.content))
        cookie_client_id = self.client.cookies.get(settings.CLIENT_ID_COOKIE_NAME).value

        self.assertEqual(cookie_client_id, client_id)
        self.assertEqual(response_data['client_id'], client_id)
        self.assertTrue(Client.objects.filter(identifier=client_id).exists())

    def test_get_data_cookie_exists(self):
        client = Client.objects.create()
        nps = NPSService.get_nps_survey_by_id(1)
        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        data = {
            "score": 10,
            "customer": {
                "client_id": client.identifier
            }
        }
        self.client.cookies = SimpleCookie({settings.CLIENT_ID_COOKIE_NAME: client.identifier})
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )
        response_data = json.loads(force_text(response.content))
        cookie_client_id = self.client.cookies.get(settings.CLIENT_ID_COOKIE_NAME).value

        self.assertEqual(cookie_client_id, client.identifier)
        self.assertEqual(response_data['client_id'], client.identifier)

    @mock.patch('upkook_core.customers.models.generate_client_id')
    def test_get_data_customer_not_dict(self, mock_generate_client_id):
        client_id = "test"
        mock_generate_client_id.return_value = client_id
        nps = NPSService.get_nps_survey_by_id(1)
        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        data = {
            "score": 10,
            "customer": 'not dict'
        }

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )

        response_data = json.loads(force_text(response.content))
        cookie_client_id = self.client.cookies.get(settings.CLIENT_ID_COOKIE_NAME).value

        self.assertEqual(response_data['client_id'], client_id)
        self.assertEqual(cookie_client_id, client_id)

    @mock.patch('upkook_core.customers.models.generate_client_id')
    def test_set_client_id_different_value(self, mock_generate_client_id):
        client_id = "test"
        mock_generate_client_id.return_value = client_id
        nps = NPSService.get_nps_survey_by_id(1)
        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        data = {
            "score": 10,
        }

        self.client.cookies = SimpleCookie({settings.CLIENT_ID_COOKIE_NAME: client_id})
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )
        self.assertTrue(mock_generate_client_id.called)
        response_data = json.loads(force_text(response.content))

        cookie_client_id = self.client.cookies.get(settings.CLIENT_ID_COOKIE_NAME).value

        self.assertEqual(response_data['client_id'], client_id)
        self.assertEqual(cookie_client_id, client_id)

    @mock.patch('upkook_core.customers.models.generate_client_id')
    def test_set_client_id_same_value_in_cookie(self, mock_generate_client_id):
        client_id = "test"
        mock_generate_client_id.return_value = client_id
        nps = NPSService.get_nps_survey_by_id(1)
        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        data = {
            "score": 10,
        }

        self.client.cookies = SimpleCookie({settings.CLIENT_ID_COOKIE_NAME: client_id})
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )

        response_data = json.loads(force_text(response.content))
        cookie_client_id = self.client.cookies.get(settings.CLIENT_ID_COOKIE_NAME).value

        self.assertEqual(response_data['client_id'], client_id)
        self.assertEqual(cookie_client_id, client_id)

    def test_get_survey_none(self):
        none_uuid = "76440add-0243-4eb0-a985-7c573bb2d101"

        url = reverse('test:test-response', kwargs={'uuid': none_uuid})
        response = self.client.post(url, data={}, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_survey(self):
        survey = Survey.objects.first()
        url = reverse('test:test-response', kwargs={'uuid': str(survey.uuid)})
        data = {
            'type': survey.type,
            'name': survey.name,
            'business': 1,
            'url': survey.url
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
