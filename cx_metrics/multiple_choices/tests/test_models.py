#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from cx_metrics.multiple_choices.models import OptionText, MultipleChoice, OptionResponse


class OptionTextTestCase(TestCase):
    fixtures = ['multiple_choices']

    def test_str(self):
        option_text = OptionText(
            multiple_choice=MultipleChoice.objects.first(),
            text='text'
        )
        self.assertEqual(str(option_text), 'text')


class OptionResponseTestCase(TestCase):
    fixtures = ['multiple_choices', 'options']

    def test_str(self):
        option_text = OptionText.objects.first()
        response = OptionResponse(
            option_text=option_text,
            customer_uuid="uuid"
        )
        self.assertEqual(str(response), str(option_text))
