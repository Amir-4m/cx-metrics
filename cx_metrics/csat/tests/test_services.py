from django.core.cache import cache
from django.test import TestCase, override_settings
from upkook_core.businesses.services import BusinessService
from upkook_core.customers.services import CustomerService
from upkook_core.industries.services import IndustryService

from cx_metrics.csat.models import CSATSurvey
from cx_metrics.csat.services.cache import CSATInsightCacheService
from cx_metrics.csat.services.csat import CSATService


class CSATServiceTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def setUp(self):
        industry = IndustryService.create_industry(name="Industry_Name", icon="")
        self.business = BusinessService.create_business(
            size=5,
            name="Business_Name",
            domain="domain.com",
            industry=industry,
        )

    def _create_survey(self, name):
        return CSATService.create_csat_survey(
            name=name,
            business=self.business,
            text="text",
            question="question",
            message="message"
        )

    def test_create_csat(self):
        kwargs = dict(name="name", business=self.business, text="text", question="question", message="message")
        csat_survey = CSATService.create_csat_survey(**kwargs)

        for (key, value) in kwargs.items():
            self.assertEqual(getattr(csat_survey, key), value)

    def test_get_csat_none(self):
        self.assertIsNone(CSATService.get_csat_survey_by_id(1000))

    def test_get_csat_surveys_by_business_order_by_is_none(self):
        expected_csat = self._create_survey(self.id())
        csat_surveys = CSATService.get_csat_surveys_by_business(self.business, ordering=None)
        self.assertEqual(expected_csat.name, csat_surveys.first().name)

    def test_get_csat_surveys_by_business_order_by_is_given(self):
        expected_csat_surveys = CSATService.get_csat_surveys_by_business(self.business, ordering=('name',))
        self.assertIn('ORDER BY "csat_csatsurvey"."name" ASC', str(expected_csat_surveys.query))

    def test_respond_with_options(self):
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        rate = 1
        response = CSATService.respond(csat_survey, customer.uuid, rate, [1])

        self.assertIsNotNone(response)
        self.assertEqual(response.rate, rate)
        self.assertEqual(response.customer_uuid, customer.uuid)
        self.assertEqual(response.survey_uuid, csat_survey.uuid)

    def test_respond_no_options(self):
        csat_survey = CSATSurvey.objects.first()
        customer = CustomerService.create_customer()
        rate = 1
        response = CSATService.respond(csat_survey, customer.uuid, rate)

        self.assertIsNotNone(response)
        self.assertEqual(response.rate, rate)
        self.assertEqual(response.customer_uuid, customer.uuid)
        self.assertEqual(response.survey_uuid, csat_survey.uuid)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class CSATInsightCacheServiceTestCase(TestCase):

    def test_set(self):
        data = {'name': self.id()}
        CSATInsightCacheService.set(self.id(), data)
        self.assertEqual(cache.get('csat_insight-%s' % self.id()), data)

    def test_get(self):
        data = {'name': self.id()}
        CSATInsightCacheService.set(self.id(), data)
        self.assertEqual(CSATInsightCacheService.get(self.id()), data)
