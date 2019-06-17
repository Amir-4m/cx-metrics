#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from django.http import Http404
from rest_framework import serializers

from upkook_core.customers.serializers import CustomerSerializer
from cx_metrics.surveys.models import Survey
from cx_metrics.surveys.decorators import register_survey_serializer
from cx_metrics.multiple_choices.serializers import MultipleChoiceSerializer

from .services import NPSService
from .models import NPSSurvey, NPSResponse


@register_survey_serializer('NPS')
class NPSSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    url = serializers.URLField(read_only=True)
    contra_reason = MultipleChoiceSerializer(source='contra', read_only=True)

    class Meta:
        model = NPSSurvey
        fields = (
            'id', 'type', 'name',
            'text', 'text_enabled',
            'question',
            'contra_reason',
            'message',
            'url'
        )

    def to_representation(self, instance):
        obj = instance
        if isinstance(instance, Survey):
            obj = NPSService.get_nps_survey_by_id(instance.id)
            if obj is None:
                raise Http404
        return super(NPSSerializer, self).to_representation(obj)


class NPSSerializerV11(NPSSerializer):
    contra_reason = MultipleChoiceSerializer(source='contra')

    def create(self, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = MultipleChoiceSerializer()
        contra = contra_serializer.create(contra_data)
        v_data.update({'contra': contra})
        return super(NPSSerializerV11, self).create(v_data)

    def update(self, instance, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = MultipleChoiceSerializer()

        if instance.contra and instance.contra.pk:
            contra = contra_serializer.update(instance.contra, contra_data)
        else:
            contra = contra_serializer.create(contra_data)

        v_data.update({'contra': contra})
        return super(NPSSerializerV11, self).update(instance, v_data)


class NPSInsightsSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = NPSSurvey
        fields = ('id', 'name', 'promoters', 'passives', 'detractors')


class NPSRespondSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = NPSResponse
        fields = ('score', 'customer')

    def to_representation(self, instance):
        return {
            'score': instance.score,
            'client_id': self.validated_data['customer'].client_id
        }

    def create(self, validated_data):
        survey_uuid = validated_data['survey_uuid']
        customer = validated_data['customer']
        score = validated_data['score']
        return NPSService.respond(
            survey_uuid=survey_uuid,
            customer_uuid=customer.uuid,
            score=score
        )
