#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.cache import cache
from django.test import TestCase, override_settings
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService
from upkook_core.industries.services import IndustryService

from cx_metrics.ces.models import CESSurvey
from cx_metrics.ces.services import CESInsightCacheService
from cx_metrics.ces.services.ces import CESService


class CESServiceTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def setUp(self):
        industry = IndustryService.create_industry(name="Industry_Name", icon="")
        self.business = BusinessService.create_business(
            size=5,
            name="Business_Name",
            domain="domain.com",
            industry=industry,
        )

    def _create_survey(self, name):
        return CESService.create_ces_survey(
            name=name,
            business=self.business,
            text="text",
            question="question",
            message="message"
        )

    def test_get_ces_none(self):
        self.assertIsNone(CESService.get_ces_survey_by_id(1000))

    def test_get_ces_surveys_by_business_order_by_is_none(self):
        expected_ces = self._create_survey(self.id())
        ces_surveys = CESService.get_ces_surveys_by_business(self.business, ordering=None)
        self.assertEqual(expected_ces.name, ces_surveys.first().name)

    def test_get_ces_surveys_by_business_order_by_is_given(self):
        expected_ces_surveys = CESService.get_ces_surveys_by_business(self.business, ordering=('name',))
        self.assertIn('ORDER BY "ces_cessurvey"."name" ASC', str(expected_ces_surveys.query))

    def test_create_ces(self):
        kwargs = dict(name="name", business=self.business, text="text", question="question", message="message")
        ces_survey = CESService.create_ces_survey(**kwargs)

        for (key, value) in kwargs.items():
            self.assertEqual(getattr(ces_survey, key), value)

    def test_respond_with_options(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        rate = 1
        response = CESService.respond(ces_survey, customer.uuid, rate, [1])

        self.assertIsNotNone(response)
        self.assertEqual(response.rate, rate)
        self.assertEqual(response.customer_uuid, customer.uuid)
        self.assertEqual(response.survey_uuid, ces_survey.uuid)

    def test_respond_no_options(self):
        ces_survey = CESSurvey.objects.first()
        customer = CustomerService.create_customer()
        rate = 1
        response = CESService.respond(ces_survey, customer.uuid, rate)

        self.assertIsNotNone(response)
        self.assertEqual(response.rate, rate)
        self.assertEqual(response.customer_uuid, customer.uuid)
        self.assertEqual(response.survey_uuid, ces_survey.uuid)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class CESInsightCacheServiceTestCase(TestCase):

    def test_set(self):
        data = {'name': self.id()}
        CESInsightCacheService.set(self.id(), data)
        self.assertEqual(cache.get('ces_insight-%s' % self.id()), data)

    def test_get(self):
        data = {'name': self.id()}
        CESInsightCacheService.set(self.id(), data)
        self.assertEqual(CESInsightCacheService.get(self.id()), data)
