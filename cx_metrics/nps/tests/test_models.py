#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4

from django.test import TestCase

from ..models import ContraOption, NPSSurvey, NPSResponse, ContraResponse


class ContraOptionTestCase(TestCase):
    fixtures = ['multiple_choices', 'nps']

    def test_str(self):
        contra_option = ContraOption(
            nps_survey=NPSSurvey.objects.first(),
            text="text",
        )
        self.assertEqual(str(contra_option), "text")


class ContraResponseTestCase(TestCase):
    def test_str(self):
        nps_response = NPSResponse(
            survey_uuid=uuid4(),
            customer_uuid=uuid4(),
            score=1
        )
        contra_option = ContraOption(
            nps_survey=NPSSurvey.objects.first(),
            text="text",
        )
        contra_response = ContraResponse(
            nps_response=nps_response,
            contra_option=contra_option
        )

        self.assertEqual(str(contra_response), "text")
