#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.urls import path

from ..views.api import DefaultOptionsAPIView

app_name = 'surveys_defaults'

urlpatterns = [
    path('<str:survey_type>/', DefaultOptionsAPIView.as_view(), name='list'),
]
