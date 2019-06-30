#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin

from cx_metrics.surveys_defaults.models import DefaultOption


@admin.register(DefaultOption)
class DefaultOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'survey_type')
    list_filter = ('question_type', 'survey_type', 'industry')
    ordering = ('question_type',)
    search_fields = ('text',)
    autocomplete_fields = ('industry',)
