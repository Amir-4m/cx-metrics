#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from .models import Survey


class SurveyAdminBase(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'promoters', 'passives', 'detractors', 'updated', 'created', 'open_survey')
    list_display_links = ('name', 'uuid')
    list_filter = ('business',)
    ordering = ('-updated',)
    search_fields = ('name', 'uuid')
    autocomplete_fields = ('business',)
    readonly_fields = ('updated', 'created', 'uuid', 'open_survey')
    date_hierarchy = 'created'
    sortable_by = ('name', 'promoters', 'passives', 'detractors', 'updated')

    def open_survey(self, obj):
        return mark_safe(_('<a href="%(url)s" target="_blank">Open Survey</a>') % {'url': obj.url})
    open_survey.short_description = _('Survey Link')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super(SurveyAdminBase, self).save_model(request, obj, form, change)


@admin.register(Survey)
class SurveyAdmin(SurveyAdminBase):
    list_display = ('name', 'type', 'uuid', 'open_survey')
    list_filter = ('type', 'business')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
