#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.urls import path

from ..views.api import NPSAPIView

app_name = 'nps'

urlpatterns = [
    path('', NPSAPIView.as_view({'post': 'create'}), name='create'),
    path('<uuid:uuid>/', NPSAPIView.as_view({'get': 'retrieve', 'put': 'update'}), name='retrieve')
]
