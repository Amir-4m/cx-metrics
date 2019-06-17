#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import serializers

from .models import MultipleChoice


class MultipleChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoice
        fields = ('type', 'text', 'enabled', 'required', 'other_enabled')
