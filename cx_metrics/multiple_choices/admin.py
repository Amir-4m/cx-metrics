#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin

from .models import MultipleChoice, Option


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


@admin.register(MultipleChoice)
class MultipleChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'enabled', 'required', 'type', 'other_enabled', 'updated')
    list_filter = ('enabled', 'required', 'type', 'other_enabled')
    ordering = ('-updated',)
    search_fields = ('text',)
    sortable_by = ('updated',)
    inlines = [
        OptionInline
    ]
