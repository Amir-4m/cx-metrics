#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework import serializers

from upkook_core.customers.serializers import CustomerSerializer

from cx_metrics.nps.services.nps import NPSService
from .models import NPSSurvey, NPSResponse


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
