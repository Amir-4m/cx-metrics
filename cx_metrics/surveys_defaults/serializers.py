#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import serializers

from cx_metrics.surveys_defaults.models import DefaultOption


class DefaultOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultOption
        fields = ('text', 'question_type', 'order')
