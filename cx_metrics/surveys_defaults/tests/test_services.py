#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from upkook_core.industries.models import Industry

from cx_metrics.surveys_defaults.models import DefaultOption
from cx_metrics.surveys_defaults.services.default_option import DefaultOptionService


class DefaultOptionServiceTestCase(TestCase):
    fixtures = ['industries']

    def test_get_default_options_by_industry_and_survey_type_order_by_is_none(self):
        expected_default_option = DefaultOption.objects.create(
            industry=Industry.objects.first(),
            survey_type='nps',
            question_type='contra',
            text='text',
            order=1,
        )
        default_options = DefaultOptionService.get_default_options_by_industry_and_survey_type(
            industry=Industry.objects.first(),
            survey_type='nps'
        )

        self.assertEqual(expected_default_option.industry, default_options.first().industry)
        self.assertEqual(expected_default_option.text, default_options.first().text)
        self.assertEqual(expected_default_option.order, default_options.first().order)
        self.assertEqual(expected_default_option.question_type, default_options.first().question_type)
        self.assertEqual(expected_default_option.survey_type, default_options.first().survey_type)

    def test_get_default_options_by_industry_and_survey_type_order_by_is_given(self):
        default_options = DefaultOptionService.get_default_options_by_industry_and_survey_type(
            industry=Industry.objects.first(),
            survey_type='nps',
            ordering=('text',)
        )
        self.assertIn('ORDER BY "surveys_defaults_defaultoption"."text" ASC', str(default_options.query))
