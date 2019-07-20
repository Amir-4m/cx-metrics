from django.test import TestCase
from upkook_core.businesses.services import BusinessService
from upkook_core.industries.services import IndustryService

from cx_metrics.csat.services.csat import CSATService


class CSATServiceTestCase(TestCase):

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
