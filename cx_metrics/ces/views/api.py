#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from upkook_core.auth.permissions import BusinessMemberPermissions

from cx_metrics.surveys.views.api import SurveyResponseAPIView, SurveyInsightsView
from ..serializers import CESSerializer, CESRespondSerializer, CESInsightSerializer
from ..services import CESService


@method_decorator(cache_control(private=True), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CESAPIView(ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CESSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'id')
    ordering = ('-updated',)
    permission_classes = (
        BusinessMemberPermissions('ces', 'cessurvey'),
    )

    def perform_create(self, serializer):
        serializer.save(
            business_id=self.request.user.business_id,
            author=self.request.user.instance
        )

    def perform_update(self, serializer):
        serializer.save(author=self.request.user.instance)

    def get_queryset(self):
        return CESService.get_ces_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True), name='post')
@method_decorator(never_cache, name='post')
class CESResponseAPIView(SurveyResponseAPIView):
    serializer_class = CESRespondSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('-updated',)

    def get_survey(self):
        return CESService.get_ces_survey_by_uuid(self.kwargs['uuid'])


@method_decorator(cache_control(private=True, max_age=1 * 60), name='get')  # 1 minute
class CESInsightsView(SurveyInsightsView):
    survey_type = 'ces'
    serializer_class = CESInsightSerializer
    permission_classes = (
        BusinessMemberPermissions('ces', 'cessurvey'),
    )

    def get_queryset(self):
        return CESService.get_ces_surveys_by_business(self.request.user.business_id)
