#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from upkook_core.auth.permissions import BusinessMemberPermissions
from ..services.nps import NPSService
from ..serializers import NPSSerializer, NPSInsightsSerializer, NPSRespondSerializer


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

    def perform_create(self, serializer):
        serializer.save(business_id=self.request.user.business_id)

    def get_queryset(self):
        return NPSService.get_nps_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True, max_age=1 * 60), name='get')  # 1 minute
class NPSInsightsView(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    serializer_class = NPSInsightsSerializer
    permission_classes = (
        BusinessMemberPermissions('nps', 'npssurvey'),
    )

    def get_queryset(self):
        return NPSService.get_nps_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(private=True), name='post')
@method_decorator(never_cache, name='post')
class NPSResponseAPIView(generics.CreateAPIView):
    serializer_class = NPSRespondSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('-updated',)

    def perform_create(self, serializer):
        serializer.save(survey_uuid=self.kwargs['uuid'])
