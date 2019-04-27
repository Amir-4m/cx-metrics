#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.urls import path

from ..views.api import SurveyAPIView

app_name = 'surveys'

urlpatterns = [
    path('', SurveyAPIView.as_view({'get': 'list'}), name='list'),
]
