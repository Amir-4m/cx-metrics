#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib import admin

from .models import MultipleChoice, Option
from .serializers import MultipleChoiceSerializer
from .services import MultipleChoiceService


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

    @staticmethod
    def to_representation(mc):
        serializer = MultipleChoiceSerializer(mc)
        representation = serializer.to_representation(mc)
        return representation

    def save_model(self, request, obj, form, change):
        super(MultipleChoiceAdmin, self).save_model(request, obj, form, change)
        self.saved_obj = obj

    def save_related(self, request, form, formsets, change):
        super(MultipleChoiceAdmin, self).save_related(request, form, formsets, change)
        representation = self.to_representation(self.saved_obj)
        MultipleChoiceService.cache_representation(self.saved_obj.id, representation)
