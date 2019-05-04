#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_text
from rest_framework import status
from upkook_core.auth.tests.client import AuthClient
from upkook_core.customers.models import Customer
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.nps.models import NPSSurvey
from ..services.nps import NPSService


class NPSViewTestBase(MemberPermissionTestMixin, TestCase):
    fixtures = ['users', 'industries', 'businesses', 'teams']

    def setUp(self):
        super(NPSViewTestBase, self).setUp()
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

        codenames = ['add_npssurvey', 'change_npssurvey', 'view_npssurvey']
        self.group = self.give_member_permissions(self.member, app_label='nps', codenames=codenames)

    def tearDown(self):
        self.remove_member_permissions(self.member, self.group)


class NPSSurveyTestCase(NPSViewTestBase):
    def test_post(self):
        data = {
            "name": "NPS_name",
            "text": "NPS_text",
            "text_enabled": True,
            "question": "NPS_question",
            "message": "NPS_message"
        }
        url = reverse('cx-nps:create')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        nps = NPSService.get_nps_survey_by_uuid(response_data['id'])
        data.update({'id': str(nps.uuid), 'url': nps.url})

        self.assertEqual(nps.business.pk, self.business.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(data, response_data)

    def test_post_invalid_data(self):
        data = {'name': 'name'}
        url = reverse('cx-nps:create')
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(['This field is required.'], response_data['text'])

    def test_get(self):
        nps = NPSService.create_nps_survey(
            name="name",
            business=self.business,
            text="text",
            question="question",
            message="message"
        )

        url = reverse('cx-nps:retrieve', kwargs={'uuid': str(nps.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(nps.uuid),
            'name': 'name',
            'text': 'text',
            'text_enabled': True,
            'question': 'question',
            'message': 'message',
            'url': nps.url,
        }
        response_data = json.loads(force_text(response.content))
        self.assertDictEqual(response_data, expected_data)

    def test_put(self):
        nps = NPSService.create_nps_survey(
            name="name",
            business=self.business,
            text="text",
            text_enabled=False,
            question="question",
            message="message"
        )

        data = {
            "name": "NPS_name",
            "text": "NPS_text",
            "text_enabled": True,
            "question": "NPS_question",
            "message": "NPS_message"
        }
        url = reverse('cx-nps:retrieve', kwargs={'uuid': str(nps.uuid)})
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        data.update({'id': str(nps.uuid), 'url': nps.url})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(data, response_data)


class NPSInsightsViewTestCase(NPSViewTestBase):
    def test_get(self):
        nps = NPSService.create_nps_survey(
            name="name",
            business=self.business,
            text="text",
            question="question",
            message="message"
        )
        NPSService.change_overall_score(nps.uuid, 'promoters', 1)
        nps.refresh_from_db()

        url = reverse('cx-nps:insights', kwargs={'uuid': str(nps.uuid)})
        response = self.client.get(url)

        expected_data = {
            'id': str(nps.uuid),
            'name': nps.name,
            'promoters': nps.promoters,
            'passives': nps.passives,
            'detractors': nps.detractors,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(force_text(response.content))
        self.assertEqual(response_data, expected_data)


class NPSResponseAPIViewTestCase(TestCase):
    fixtures = ['nps']

    def test_perform_create_save_object(self):
        nps = NPSSurvey.objects.first()
        customer = Customer.objects.create()
        data = {
            "score": 1,
            "customer": {
                "client_id": customer.client_id
            }
        }

        url = reverse('cx-nps:responses-create', kwargs={'uuid': str(nps.uuid)})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        response_data = json.loads(force_text(response.content))
        expected_data = {
            "score": 1,
            "client_id": customer.client_id

        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(response_data, expected_data)
