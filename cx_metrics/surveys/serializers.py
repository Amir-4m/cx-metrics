#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import serializers

from .models import Survey


class SurveySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'type', 'name', 'url')
