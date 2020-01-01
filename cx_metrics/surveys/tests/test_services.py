#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import datetime
from uuid import uuid4
from django.test import TestCase
from upkook_core.businesses.services import BusinessService
from upkook_core.industries.services import IndustryService

from ..models import Survey
from ..services import SurveyService


class MockResponse(object):
    def __init__(self, created):
        self.created = created


class SurveyServiceTestCase(TestCase):
    def setUp(self):
        industry = IndustryService.create_industry(name='name', icon='')
        self.business = BusinessService.create_business(
            size=5,
            name="name",
            domain="domain.com",
            industry=industry,
        )

    def test_get_surveys_by_business(self):
        survey = Survey.objects.create(
            type='test',
            name='test_get_surveys_by_business',
            business=self.business,
        )

        surveys = SurveyService.get_surveys_by_business(self.business)
        self.assertEqual(len(surveys), 1)
        obj = surveys.first()
        self.assertIsInstance(obj, Survey)
        self.assertEqual(obj.pk, survey.pk)

    def test_get_surveys_by_business_order_by_is_given(self):
        surveys = SurveyService.get_surveys_by_business(self.business, ('name',))
        self.assertIn('ORDER BY "surveys_survey"."name" ASC', str(surveys.query))

    def test_survey_with_uuid_exists_true(self):
        survey = Survey.objects.create(
            type='test',
            name='test_get_surveys_by_business',
            business=self.business,
        )

        self.assertTrue(SurveyService.survey_with_uuid_exists(survey.uuid))

    def test_survey_with_uuid_exists_false(self):
        self.assertFalse(SurveyService.survey_with_uuid_exists(uuid4()))

    def test_is_duplicate_response(self):
        response = MockResponse(created=datetime.datetime(2016, 11, 15, 9, 59, 25, 608206))

        self.assertFalse(SurveyService.is_duplicate_response(response))
