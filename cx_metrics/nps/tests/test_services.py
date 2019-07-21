#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4

from django.test import TestCase
from upkook_core.businesses.models import Business
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService
from upkook_core.industries.services import IndustryService

from cx_metrics.multiple_choices.models import Option
from ..models import NPSSurvey, ContraOption, NPSResponse
from ..services import NPSService, ContraService


class NPSSurveyServiceTestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps']

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
        response = NPSService.respond(nps_survey, customer.uuid, score)

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
        response = NPSService.respond(nps_survey, customer.uuid, score)

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
        response = NPSService.respond(nps_survey, customer.uuid, score)

        nps_survey.refresh_from_db()
        self.assertEqual(nps_survey.promoters, 0)
        self.assertEqual(nps_survey.passives, 0)
        self.assertEqual(nps_survey.detractors, 1)

        self.assertEqual(response.score, score)
        self.assertEqual(response.survey_uuid, nps_survey.uuid)
        self.assertEqual(response.customer_uuid, customer.uuid)

    def test_respond_survey_not_found(self):
        nps = NPSSurvey(
            name='test',
            business=Business.objects.first(),
            text='text',
            question="question",
            message="message",
        )
        customer_uuid = uuid4()
        response = NPSService.respond(nps, customer_uuid, 0)
        self.assertIsNone(response)

    def test_respond_with_options(self):
        nps_survey = self._create_survey(self.id())
        customer = CustomerService.create_customer()
        score = 5
        option = Option.objects.first()
        response = NPSService.respond(nps_survey, customer.uuid, score, [option.id])

        self.assertIsNotNone(response)
        self.assertEqual(response.score, score)
        self.assertEqual(response.customer_uuid, customer.uuid)
        self.assertEqual(response.survey_uuid, nps_survey.uuid)


class ContraServiceTestCase(TestCase):
    fixtures = ['industries', 'businesses', 'nps']

    def setUp(self):
        industry = IndustryService.create_industry(name="Industry_Name", icon="")
        self.business = BusinessService.create_business(
            size=5,
            name="Business_Name",
            domain="domain.com",
            industry=industry,
        )
        self.nps = NPSService.create_nps_survey(
            name='nps',
            business=self.business,
            text="text",
            question="question",
            message="message"
        )
        self.response = NPSResponse.objects.create(
            survey_uuid=self.nps.uuid,
            customer_uuid=self.nps.uuid,
            score=10
        )
        self.customer = CustomerService.create_customer()

    def _create_contra_option(self, text='text'):
        return ContraOption.objects.create(
            nps_survey=self.nps,
            text=text
        )

    def test_create_contra_response(self):
        contra_option = self._create_contra_option()
        response = NPSResponse.objects.create(
            survey_uuid=self.nps.uuid,
            customer_uuid=self.customer.uuid,
            score=10
        )
        kwargs = dict(nps_response=response, contra_option=contra_option)
        contra_response = ContraService.create_contra_response(
            nps_response=response,
            contra_option=contra_option
        )
        for (key, value) in kwargs.items():
            self.assertEqual(getattr(contra_response, key), value)

    def test_get_or_create_contra_option_new(self):
        defaults = {'nps_survey': self.nps}
        contra_option, created = ContraService.get_or_create_contra_option(defaults=defaults, text="default_text")
        self.assertTrue(created)
        self.assertEqual(contra_option.text, 'default_text')

    def test_get_or_create_contra_option_exists(self):
        contra_option = self._create_contra_option()
        defaults = {'nps_survey': self.nps}
        other, created = ContraService.get_or_create_contra_option(defaults=defaults, text="text")
        self.assertFalse(created)
        self.assertEqual(contra_option.id, other.id)

    def test_update_contra_option_count(self):
        contra_option = self._create_contra_option()
        count = ContraService.change_contra_option_count(contra_option, 'count', 1)
        self.assertEqual(count, 1)
        contra_option.refresh_from_db()
        self.assertEqual(contra_option.count, 1)
