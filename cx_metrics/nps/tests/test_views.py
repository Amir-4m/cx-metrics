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
from upkook_core.customers.services import CustomerService
from upkook_core.teams.services import MemberService
from upkook_core.teams.tests import MemberPermissionTestMixin

from cx_metrics.multiple_choices.services import MultipleChoiceService
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
        data.update({
            'id': str(nps.uuid),
            'url': nps.url,
            'type': nps.type,
            'contra_reason': None,
        })

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

    def test_post_v11(self):
        data = {
            "name": "NPS_name",
            "text": "NPS_text",
            "text_enabled": True,
            "question": "NPS_question",
            "contra_reason": {
                "text": "Why not?",
                "options": [
                    {"text": "Option 1", "order": 1},
                    {"text": "Option 2", "order": 2},
                ]
            },
            "message": "NPS_message"
        }

        url = reverse('cx-nps:create')
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )

        response_data = json.loads(force_text(response.content))
        nps = NPSService.get_nps_survey_by_uuid(response_data['id'])

        contra_data = model_to_dict(
            nps.contra,
            ('text', 'enabled', 'required', 'type', 'other_enabled')
        )
        contra_data.update({'options': []})
        for option in nps.contra.options.order_by('order'):
            option_data = model_to_dict(option, ('id', 'text', 'enabled', 'order'))
            contra_data['options'].append(option_data)

        data.update({
            'id': str(nps.uuid),
            'url': nps.url,
            'type': nps.type,
            'contra_reason': contra_data,
        })

        self.assertEqual(nps.business.pk, self.business.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(data, response_data)

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
            'type': nps.type,
            'name': 'name',
            'text': 'text',
            'text_enabled': True,
            'question': 'question',
            'contra_reason': None,
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
        data.update({
            'id': str(nps.uuid),
            'url': nps.url,
            'type': nps.type,
            'contra_reason': None,
        })

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
    fixtures = ['multiple_choices', 'nps']

    def test_post(self):
        nps = NPSService.get_nps_survey_by_id(1)
        customer = CustomerService.create_customer()
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

    def test_post_v11(self):
        customer = CustomerService.create_customer()
        data = {
            "score": 3,
            "customer": {
                "client_id": customer.client_id
            },
            "options": [1]
        }
        contra = MultipleChoiceService.get_by_id(1)
        nps = NPSService.get_nps_survey_by_id(1)
        nps.contra = contra
        nps.save()
        url = reverse('cx-nps:responses-create', kwargs={'uuid': nps.uuid})
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_ACCEPT='application/json; version=1.1',
        )

        response_data = json.loads(force_text(response.content))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['score'], data['score'])
        self.assertEqual((response_data['client_id']), data['customer']['client_id'])

    def test_get_survey(self):
        none_uuid = "76440add-0243-4eb0-a985-7c573bb2d101"
        data = {
            "score": 1,
            "customer": {
                "client_id": 1
            }
        }

        url = reverse('cx-nps:responses-create', kwargs={'uuid': none_uuid})
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
