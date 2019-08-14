#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from rest_framework import serializers
from rest_framework.fields import empty

from ..models import Survey


class TestSurveyResponseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'type', 'name', 'business', 'url')

    def __init__(self, instance=None, data=empty, **kwargs):
        c_kwargs = copy(kwargs)
        self.survey = c_kwargs.pop('survey')
        super(TestSurveyResponseSerializer, self).__init__(instance, data, **c_kwargs)

    def create(self, validated_data):
        validated_data.pop('user_agent')

        return super(TestSurveyResponseSerializer, self).create(validated_data)
