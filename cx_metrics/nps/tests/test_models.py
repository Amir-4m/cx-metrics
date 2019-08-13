#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..services import NPSService


class NPSSurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'nps']

    def test_get_contra_response_texts(self):
        nps = NPSService.get_nps_survey_by_id(1)

        self.assertListEqual(nps.contra_response_option_texts, [])

    def test_has_contra_enabled(self):
        mc = MultipleChoiceService.get_by_id(1)
        nps = NPSService.get_nps_survey_by_id(1)
        nps.contra = mc
        nps.save()
        self.assertTrue(nps.has_contra())

    def test_has_contra_not_enabled(self):
        mc = MultipleChoiceService.get_by_id(1)
        mc.enabled = False
        nps = NPSService.get_nps_survey_by_id(1)
        nps.contra = mc
        nps.save()
        self.assertFalse(nps.has_contra())
