#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from upkook_core.auth.permissions import BusinessMemberPermissions
from ..services.nps import NPSService
from ..serializers import NPSSerializer


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
