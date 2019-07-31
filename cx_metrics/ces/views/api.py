#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from upkook_core.auth.permissions import BusinessMemberPermissions

from ..services import CESInsightCacheService
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
class CESResponseAPIView(generics.CreateAPIView):
    serializer_class = CESRespondSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('-updated',)

    def get_survey(self):
        survey = CESService.get_ces_survey_by_uuid(self.kwargs['uuid'])
        if survey is None:
            raise Http404
        return survey

    def get_serializer(self, *args, **kwargs):
        survey = self.get_survey()
        default_kwargs = {'survey': survey}
        default_kwargs.update(kwargs)
        return super(CESResponseAPIView, self).get_serializer(*args, **default_kwargs)


@method_decorator(cache_control(private=True, max_age=1 * 60), name='get')  # 1 minute
class CESInsightsView(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    serializer_class = CESInsightSerializer
    permission_classes = (
        BusinessMemberPermissions('ces', 'cessurvey'),
    )

    def get_queryset(self):
        return CESService.get_ces_surveys_by_business(self.request.user.business_id)

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        cache_key = self.kwargs[lookup_url_kwarg]
        data = CESInsightCacheService.get(cache_key)

        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            CESInsightCacheService.set(cache_key, data)

        return Response(data)
