#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from ..models import CESSurvey
from ..services import CESService


class CESSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def test_ces_type(self):
        ces = CESSurvey()
        self.assertEqual(ces.type, 'CES')

    def test_get_contra_response_texts(self):
        ces = CESSurvey()
        self.assertListEqual(ces.contra_response_option_texts, [])

    def test_has_contra_enabled(self):
        ces = CESService.get_ces_survey_by_id(1)
        self.assertTrue(ces.has_contra())

    def test_has_contra_not_enabled(self):
        ces = CESService.get_ces_survey_by_id(1)
        ces.contra.enabled = False
        self.assertFalse(ces.has_contra())
