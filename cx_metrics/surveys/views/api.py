#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from upkook_core.auth.permissions import BusinessMemberPermissions
from ..factory import survey_serializer_factory
from ..serializers import SurveySerializer
from ..services import SurveyService


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


class SurveyFactoryAPIView(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    queryset = SurveyService.all()

    def get_serializer(self, instance, *args, **kwargs):
        serializer_class = survey_serializer_factory.get_serializer_class(instance.type)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(instance, *args, **kwargs)
