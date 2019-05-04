#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from cx_metrics.surveys.admin import SurveyAdminBase
from .models import NPSSurvey


@admin.register(NPSSurvey)
class NPSSurveyAdmin(SurveyAdminBase):
    exclude = ('survey',)
    readonly_fields = ('promoters', 'passives', 'detractors', 'updated', 'created', 'uuid')
