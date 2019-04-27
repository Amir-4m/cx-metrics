#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from .models import Survey


class SurveyAdminBase(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'open_survey')
    list_filter = ('business',)
    ordering = ('-updated',)
    search_fields = ('name', 'uuid')
    readonly_fields = ('updated', 'created', 'uuid', 'open_survey')

    def open_survey(self, obj):
        return mark_safe(_('<a href="%(url)s" target="_blank">Open Survey</a>') % {'url': obj.url})
    open_survey.short_description = _('Survey Link')


@admin.register(Survey)
class SurveyAdmin(SurveyAdminBase):
    list_display = ('name', 'type', 'uuid', 'open_survey')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
