#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from upkook_core.auth.permissions import BusinessMemberPermissions

from cx_metrics.csat.serializers import CSATSerializer, CSATRespondSerializer, CSATInsightSerializer
from cx_metrics.csat.services.cache import CSATInsightCacheService
from cx_metrics.surveys.views.api import SurveyResponseAPIView
from ..services.csat import CSATService


@method_decorator(cache_control(private=True), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CSATAPIView(ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = CSATSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'id')
    ordering = ('-updated',)
    permission_classes = (
        BusinessMemberPermissions('csat', 'csatsurvey'),
    )

    def perform_create(self, serializer):
        serializer.save(
            business_id=self.request.user.business_id,
            author=self.request.user.instance
        )

    def perform_update(self, serializer):
        serializer.save(author=self.request.user.instance)

    def get_queryset(self):
        return CSATService.get_csat_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True), name='post')
@method_decorator(never_cache, name='post')
class CSATResponseAPIView(SurveyResponseAPIView):
    serializer_class = CSATRespondSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('-updated',)

    def get_survey(self):
        return CSATService.get_csat_survey_by_uuid(self.kwargs['uuid'])


@method_decorator(cache_control(private=True, max_age=1 * 60), name='get')  # 1 minute
class CSATInsightsView(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    serializer_class = CSATInsightSerializer
    permission_classes = (
        BusinessMemberPermissions('csat', 'csatsurvey'),
    )

    def get_queryset(self):
        return CSATService.get_csat_surveys_by_business(self.request.user.business_id)

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        cache_key = self.kwargs[lookup_url_kwarg]
        data = CSATInsightCacheService.get(cache_key)

        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            CSATInsightCacheService.set(cache_key, data)

        return Response(data)
