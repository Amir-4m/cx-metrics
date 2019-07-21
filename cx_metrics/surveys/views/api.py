#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from upkook_core.auth.permissions import BusinessMemberPermissions

from ..factory import survey_serializer_factory
from ..serializers import SurveySerializer
from ..services import SurveyService, SurveyCacheService


@method_decorator(cache_control(private=True), name='get')
@method_decorator(never_cache, name='get')
class SurveyAPIView(generics.ListAPIView):
    serializer_class = SurveySerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'updated')
    ordering = ('-updated',)
    permission_classes = (
        BusinessMemberPermissions('surveys', 'survey'),
    )

    def get_queryset(self):
        return SurveyService.get_surveys_by_business(self.request.user.business_id)


@method_decorator(cache_control(max_age=1 * 60), name='get')  # 1 minute
class SurveyFactoryAPIView(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = SurveyService.all()

    def get_object(self):
        obj = super(SurveyFactoryAPIView, self).get_object()
        if not obj.active:
            raise Http404
        return obj

    def get_serializer(self, instance, *args, **kwargs):
        serializer_class = survey_serializer_factory.get_serializer_class(instance.type)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(instance, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        cache_key = self.kwargs[lookup_url_kwarg]
        data = SurveyCacheService.get(cache_key)

        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            SurveyCacheService.set(cache_key, data)

        return Response(data)
