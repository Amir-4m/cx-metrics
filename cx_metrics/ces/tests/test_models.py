#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.ces.services.ces import CESService


class CESSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def test_get_contra_response_texts(self):
        ces = CESService.get_ces_survey_by_id(1)
        self.assertEqual(ces.type, 'CES')
