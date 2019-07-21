#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache, cache_control
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from upkook_core.auth.permissions import BusinessMemberPermissions

from cx_metrics.csat.serializers import CSATSerializer
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
