#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cx_metrics.surveys.admin import SurveyAdminBase
from .models import CSATSurvey


@admin.register(CSATSurvey)
class CSATSurveyAdmin(SurveyAdminBase):
    list_display = ('name', 'uuid', 'scale', 'updated', 'created', 'open_survey')
    sortable_by = ('name', 'scale', 'updated')

    exclude = ('survey', 'contra')
    readonly_fields = (
        'author', 'uuid', 'created', 'updated', 'contra_question'
    )
    fieldsets = (
        (None, {
            'fields': (
                'uuid', 'name', 'business', 'updated', 'created', 'author', 'scale',)
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
