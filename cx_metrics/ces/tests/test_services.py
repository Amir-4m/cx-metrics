#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.ces.services.ces import CESService


class CESServiceTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'ces']

    def test_get_ces_none(self):
        self.assertIsNone(CESService.get_ces_survey_by_id(1000))
