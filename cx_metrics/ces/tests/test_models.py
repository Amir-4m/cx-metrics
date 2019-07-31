#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.ces.models import CESSurvey


class CESSurveyTestCase(TestCase):

    def test_ces_type(self):
        ces = CESSurvey()
        self.assertEqual(ces.type, 'CES')

    def test_get_contra_response_texts(self):
        ces = CESSurvey()
        self.assertListEqual(ces.contra_response_option_texts, [])
