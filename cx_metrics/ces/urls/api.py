#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path

from cx_metrics.ces.views.api import CESAPIView, CESResponseAPIView, CESInsightsView

app_name = 'ces'

urlpatterns = [
    path('', CESAPIView.as_view({'post': 'create'}), name='create'),
    path('<uuid:uuid>/', CESAPIView.as_view({'get': 'retrieve', 'put': 'update'}), name='detail'),
    path('<uuid:uuid>/responses/', CESResponseAPIView.as_view(), name='responses-create'),
    path('<uuid:uuid>/insights/', CESInsightsView.as_view(), name='insights')
]
