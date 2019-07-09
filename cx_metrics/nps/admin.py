#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cx_metrics.surveys.admin import SurveyAdminBase
from .models import NPSSurvey, NPSResponse


@admin.register(NPSSurvey)
class NPSSurveyAdmin(SurveyAdminBase):
    exclude = ('survey', 'contra',)
    readonly_fields = (
        'contra_question', 'promoters', 'passives', 'detractors', 'updated', 'created', 'uuid', 'author'
    )
    fieldsets = (
        (None, {
            'fields': (
                'uuid', 'name', 'business', 'promoters', 'passives', 'detractors', 'updated', 'created', 'author')
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('text_enabled', 'text', 'question', 'contra_question', 'message')
        }),
    )

    def contra_question(self, instance):
        if instance.contra and instance.contra.pk:
            contra = instance.contra
            url = reverse('admin:%s_%s_change' % (contra._meta.app_label, contra._meta.model_name), args=(contra.pk,))
            return mark_safe('%(contra)s<br /><a href="%(url)s" target="_blank">%(link_text)s</a>' % {
                'contra': contra,
                'url': url,
                'link_text': _('More...'),
            })
        return None

    contra_question.short_description = _('Contra')

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super(NPSSurveyAdmin, self).save_model(request, obj, form, change)


@admin.register(NPSResponse)
class NPSResponseAdmin(admin.ModelAdmin):
    list_display = ('survey_uuid', 'customer_uuid', 'score', 'created')
    list_display_links = ('survey_uuid', 'customer_uuid')
    list_filter = ('score',)
    ordering = ('-created',)
    search_fields = ('survey_uuid', 'customer_uuid')
    date_hierarchy = 'created'
    sortable_by = ('score', 'created')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
