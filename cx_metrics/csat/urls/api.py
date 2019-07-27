#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path

from cx_metrics.csat.views.api import CSATAPIView, CSATResponseAPIView, CSATInsightsView

app_name = 'csat'

urlpatterns = [
    path('', CSATAPIView.as_view({'post': 'create'}), name='create'),
    path('<uuid:uuid>/', CSATAPIView.as_view({'get': 'retrieve', 'put': 'update'}), name='detail'),
    path('<uuid:uuid>/responses/', CSATResponseAPIView.as_view(), name='responses-create'),
    path('<uuid:uuid>/insights/', CSATInsightsView.as_view(), name='insights')
]
