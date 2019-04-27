#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from upkook_core.auth.permissions import BusinessMemberPermissions
from ..serializers import SurveySerializer
from ..services import SurveyService


class SurveyAPIView(ListModelMixin, GenericViewSet):
    serializer_class = SurveySerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'updated')
    ordering = ('-updated',)
    permission_classes = (
        BusinessMemberPermissions('surveys', 'survey'),
    )

    def get_queryset(self):
        return SurveyService.get_surveys_by_business(self.request.user.business_id)
