#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.nps.services import NPSService


class NPSSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'nps']

    def test_get_contra_response_texts(self):
        nps = NPSService.get_nps_survey_by_id(1)

        self.assertListEqual(nps.contra_response_option_texts, [])
