#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework import generics, status
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


class SurveyResponseAPIView(generics.CreateAPIView):

    def set_client_id(self, request, response, client_id):
        cookie_client_id = request.COOKIES.get(settings.CLIENT_ID_COOKIE_NAME)
        if cookie_client_id != client_id:
            response.set_cookie(
                key=settings.CLIENT_ID_COOKIE_NAME,
                value=client_id,
                max_age=settings.CLIENT_ID_COOKIE_AGE,
                path=settings.CLIENT_ID_COOKIE_PATH,
                domain=settings.CLIENT_ID_COOKIE_DOMAIN,
                secure=settings.CLIENT_ID_COOKIE_SECURE,
                httponly=False,
            )

    def get_data(self, request):
        customer_data = request.data.get('customer', {})
        if not isinstance(customer_data, dict):
            customer_data = {}

        client_id = request.COOKIES.get(settings.CLIENT_ID_COOKIE_NAME)
        if client_id:
            customer_data.update({'client_id': client_id})

        data = copy(request.data)
        data.update({'customer': customer_data})
        return data

    def get_serializer(self, *args, **kwargs):
        survey = self.get_survey()
        if survey is None:
            raise Http404

        default_kwargs = {'survey': survey}
        default_kwargs.update(kwargs)
        return super(SurveyResponseAPIView, self).get_serializer(*args, **default_kwargs)

    def get_survey(self):
        return SurveyService.get_survey_by_uuid(self.kwargs['uuid'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.get_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        response_client_id = serializer.data.get('client_id')
        self.set_client_id(self.request, response, response_client_id)
        return response
