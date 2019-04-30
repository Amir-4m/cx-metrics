#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4
from django.test import TestCase

from upkook_core.industries.services import IndustryService
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService
from ..services.nps import NPSService
from ..models import NPSSurvey


class NPSSurveyServiceTestCase(TestCase):

    def setUp(self):
        industry = IndustryService.create_industry(name="Industry_Name", icon="")
        self.business = BusinessService.create_business(
            size=5,
            name="Business_Name",
            domain="domain.com",
            industry=industry,
        )

    def _create_survey(self, name):
        return NPSService.create_nps_survey(
            name=name,
            business=self.business,
            text="text",
            question="question",
            message="message"
        )

    def test_get_nps_none(self):
        self.assertIsNone(NPSService.get_nps_survey_by_id(1000))

    def test_create_nps(self):
        kwargs = dict(name="name", business=self.business, text="text", question="question", message="message")
        nps_survey = NPSSurvey.objects.create(**kwargs)

        for (key, value) in kwargs.items():
            self.assertEqual(getattr(nps_survey, key), value)

    def test_get_nps_surveys_by_business_order_by_is_none(self):
        expected_nps = self._create_survey(self.id())
        nps_surveys = NPSService.get_nps_surveys_by_business(self.business, ordering=None)
        self.assertEqual(expected_nps.name, nps_surveys.first().name)

    def test_get_nps_surveys_by_business_order_by_is_given(self):
        expected_nps_surveys = NPSService.get_nps_surveys_by_business(self.business, ordering=('name',))
        self.assertIn('ORDER BY "nps_npssurvey"."name" ASC', str(expected_nps_surveys.query))

    def test_change_overall_score(self):
        nps_survey = self._create_survey(self.id())
        count = NPSService.change_overall_score(nps_survey.uuid, NPSService.PROMOTERS, 1)
        self.assertEqual(count, 1)
        nps_survey.refresh_from_db()
        self.assertEqual(nps_survey.promoters, 1)

    def test_respond_promoter(self):
        nps_survey = self._create_survey(self.id())
        customer = CustomerService.create_customer()
        score = 10
        response = NPSService.respond(nps_survey.uuid, customer.uuid, score)

        nps_survey.refresh_from_db()
        self.assertEqual(nps_survey.promoters, 1)
        self.assertEqual(nps_survey.passives, 0)
        self.assertEqual(nps_survey.detractors, 0)

        self.assertEqual(response.score, score)
        self.assertEqual(response.survey_uuid, nps_survey.uuid)
        self.assertEqual(response.customer_uuid, customer.uuid)

    def test_respond_passives(self):
        nps_survey = self._create_survey(self.id())
        customer = CustomerService.create_customer()
        score = 8
        response = NPSService.respond(nps_survey.uuid, customer.uuid, score)

        nps_survey.refresh_from_db()
        self.assertEqual(nps_survey.promoters, 0)
        self.assertEqual(nps_survey.passives, 1)
        self.assertEqual(nps_survey.detractors, 0)

        self.assertEqual(response.score, score)
        self.assertEqual(response.survey_uuid, nps_survey.uuid)
        self.assertEqual(response.customer_uuid, customer.uuid)

    def test_respond_detractor(self):
        nps_survey = self._create_survey(self.id())
        customer = CustomerService.create_customer()
        score = 3
        response = NPSService.respond(nps_survey.uuid, customer.uuid, score)

        nps_survey.refresh_from_db()
        self.assertEqual(nps_survey.promoters, 0)
        self.assertEqual(nps_survey.passives, 0)
        self.assertEqual(nps_survey.detractors, 1)

        self.assertEqual(response.score, score)
        self.assertEqual(response.survey_uuid, nps_survey.uuid)
        self.assertEqual(response.customer_uuid, customer.uuid)

    def test_respond_survey_not_found(self):
        survey_uuid = uuid4()
        customer_uuid = uuid4()
        response = NPSService.respond(survey_uuid, customer_uuid, 0)
        self.assertIsNone(response)
