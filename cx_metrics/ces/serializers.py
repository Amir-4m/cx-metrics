#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from copy import copy
from django.db import transaction
from django.http import Http404
from rest_framework import serializers
from rest_framework.fields import empty

from cx_metrics.ces.models import CESSurvey
from cx_metrics.ces.services import CESService
from cx_metrics.multiple_choices.serializers import CachedMultipleChoiceSerializer
from cx_metrics.surveys.decorators import register_survey_serializer
from cx_metrics.surveys.models import Survey


@register_survey_serializer('CES')
class CESSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    url = serializers.URLField(read_only=True)
    contra_reason = CachedMultipleChoiceSerializer(source='contra')

    def __init__(self, instance=None, data=empty, **kwargs):
        if isinstance(instance, Survey):
            instance = CESService.get_ces_survey(survey_id=instance.id)
        super(CESSerializer, self).__init__(instance, data, **kwargs)
        contra = instance and instance.contra
        self.fields['contra_reason'] = CachedMultipleChoiceSerializer(source='contra', instance=contra)

    class Meta:
        model = CESSurvey
        fields = (
            'id', 'type', 'name',
            'text', 'text_enabled',
            'question',
            'contra_reason',
            'message',
            'scale',
            'url'
        )

    def to_representation(self, instance):
        obj = instance
        if isinstance(instance, Survey):
            obj = CESService.get_ces_survey(survey_id=instance.id)
            if obj is None:
                raise Http404
        return super(CESSerializer, self).to_representation(obj)

    @transaction.atomic()
    def create(self, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']
        contra = contra_serializer.create(contra_data)
        v_data.update({'contra': contra})
        return super(CESSerializer, self).create(v_data)

    def update(self, instance, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']

        if instance.contra and instance.contra.pk:
            contra = contra_serializer.update(instance.contra, contra_data)
        else:
            contra = contra_serializer.create(contra_data)

        v_data.update({'contra': contra})
        return super(CESSerializer, self).update(instance, v_data)
