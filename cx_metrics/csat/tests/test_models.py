#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.csat.models import CSATSurvey


class CSATSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def test_get_contra_response_texts(self):
        csat = CSATSurvey()
        self.assertListEqual(csat.contra_response_option_texts, [])
