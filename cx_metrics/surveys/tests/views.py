#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from cx_metrics.surveys.views.api import SurveyResponseAPIView
from cx_metrics.surveys.tests.serializers import TestSurveyResponseSerializer


class TestSurveyResponseAPIView(SurveyResponseAPIView):
    serializer_class = TestSurveyResponseSerializer
