#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.urls import path

from ..views.api import SurveyAPIView, SurveyFactoryAPIView

app_name = 'surveys'

urlpatterns = [
    path('', SurveyAPIView.as_view(), name='list'),
    path('<uuid:uuid>/', SurveyFactoryAPIView.as_view(), name='retrieve')
]
