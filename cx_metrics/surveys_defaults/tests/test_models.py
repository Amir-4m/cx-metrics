#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from upkook_core.industries.models import Industry

from cx_metrics.surveys_defaults.models import DefaultOption


class DefaultOptionTestCase(TestCase):
    fixtures = ['industries']

    def test_str(self):
        default_option = DefaultOption(
            industry=Industry.objects.first(),
            survey_type='nps',
            question_type='contra',
            text='text',
            order=1,
        )
        self.assertEqual(str(default_option), 'text')
