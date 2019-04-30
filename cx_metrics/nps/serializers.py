#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import serializers

from .models import NPSSurvey


class NPSSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    url = serializers.URLField(read_only=True)

    class Meta:
        model = NPSSurvey
        fields = ('id', 'name', 'text', 'text_enabled', 'question', 'message', 'url')


class NPSInsightsSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = NPSSurvey
        fields = ('id', 'promoters', 'passive', 'detractors')
