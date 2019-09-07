#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from upkook_core.auth.permissions import BusinessMemberPermissions

from cx_metrics.surveys.views.api import SurveyResponseAPIView, SurveyInsightsView
from ..serializers import (
    NPSSerializer, NPSSerializerV11,
    NPSInsightsSerializer,
    NPSRespondSerializer, NPSRespondSerializerV11
)
from ..services.nps import NPSService


@method_decorator(cache_control(private=True), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class NPSAPIView(ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = NPSSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'id')
    ordering = ('-updated',)
    permission_classes = (
        BusinessMemberPermissions('nps', 'npssurvey'),
    )

    def get_serializer_class(self):
        if self.request.version == '1.1':
            return NPSSerializerV11
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(
            business_id=self.request.user.business_id,
            author=self.request.user.instance
        )

    def perform_update(self, serializer):
        serializer.save(author=self.request.user.instance)

    def get_queryset(self):
        return NPSService.get_nps_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True, max_age=1 * 60), name='get')  # 1 minute
class NPSInsightsView(SurveyInsightsView):
    survey_type = 'nps'
    serializer_class = NPSInsightsSerializer
    permission_classes = (
        BusinessMemberPermissions('nps', 'npssurvey'),
    )

    def get_queryset(self):
        return NPSService.get_nps_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True), name='post')
@method_decorator(never_cache, name='post')
class NPSResponseAPIView(SurveyResponseAPIView):
    serializer_class = NPSRespondSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('-updated',)

    def get_survey(self):
        return NPSService.get_nps_survey_by_uuid(self.kwargs['uuid'])

    def get_serializer_class(self):
        if self.request.version == '1.1':
            return NPSRespondSerializerV11
        return self.serializer_class
