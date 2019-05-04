#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.nps.models import NPSResponse, NPSSurvey
from cx_metrics.nps.serializers import NPSRespondSerializer
from upkook_core.customers.models import Customer


class NPSRespondSerializerTestCase(TestCase):
    fixtures = ['nps']

    def setUp(self):
        self.customer = Customer.objects.create()
        self.serializer = NPSRespondSerializer()

    def test_to_representation(self):
        data = {
            'score': 10,
            'customer': {
                "client_id": self.customer.client_id
            }
        }

        serializer = NPSRespondSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        instance = NPSResponse(score=10, customer_uuid=self.customer.uuid)
        representation = serializer.to_representation(instance)
        self.assertEqual(representation['client_id'], data['customer']['client_id'])
        self.assertEqual(representation['score'], data['score'])

    def test_create_return_nps_object(self):
        nps = NPSSurvey.objects.first()
        data = {
            "survey_uuid": str(nps.uuid),
            "customer": self.customer,
            "score": 1
        }

        created_nps_response = self.serializer.create(data)

        self.assertEqual(created_nps_response.score, data['score'])
        self.assertEqual(created_nps_response.survey_uuid, data['survey_uuid'])
        self.assertEqual(created_nps_response.customer_uuid, data['customer'].uuid)

    def test_create_return_none(self):
        invalid_uuid = "f6fd2c9a-1e53-4722-a1c1-c2f79ffb8be4"
        data = {
            "survey_uuid": invalid_uuid,
            "customer": self.customer,
            "score": 10
        }

        created_nps_response = self.serializer.create(data)
        self.assertIsNone(created_nps_response)
