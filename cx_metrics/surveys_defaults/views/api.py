#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import generics

from upkook_core.auth.permissions import BusinessMemberPermissions

from ..services.default_option import DefaultOptionService
from cx_metrics.surveys_defaults.serializers import DefaultOptionsSerializer


class DefaultOptionsAPIView(generics.ListAPIView):
    serializer_class = DefaultOptionsSerializer
    pagination_class = None
    permission_classes = (
        BusinessMemberPermissions('surveys_defaults', 'defaultoption'),
    )

    def get_queryset(self):
        lookup_url_survey_type = self.kwargs['survey_type']
        default_options = DefaultOptionService.get_default_options_by_industry_and_survey_type(
            self.request.user.business.industry_id,
            lookup_url_survey_type,
            ordering=('question_type', 'order')
        )
        return default_options
