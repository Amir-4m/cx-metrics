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

    def test_create_csat(self):
        kwargs = dict(name="name", business=self.business, text="text", question="question", message="message")
        csat_survey = CSATService.create_csat_survey(**kwargs)

        for (key, value) in kwargs.items():
            self.assertEqual(getattr(csat_survey, key), value)
