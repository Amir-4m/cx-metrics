#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from ..models import CSATSurvey
from ..services import CSATService


class CSATSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def test_get_contra_response_texts(self):
        csat = CSATSurvey()
        self.assertListEqual(csat.contra_response_option_texts, [])

    def test_has_contra_enabled(self):
        csat = CSATService.get_csat_survey_by_id(1)
        self.assertTrue(csat.has_contra())

    def test_has_contra_not_enabled(self):
        csat = CSATService.get_csat_survey_by_id(1)
        csat.contra.enabled = False
        self.assertFalse(csat.has_contra())
