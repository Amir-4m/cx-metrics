#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path

from cx_metrics.surveys.tests.views import TestSurveyResponseAPIView

app_name = 'ces'

urlpatterns = [
    path('<uuid:uuid>/', TestSurveyResponseAPIView.as_view(), name='test-response'),
]
