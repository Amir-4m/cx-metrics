#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from django.db import transaction
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from upkook_core.customers.serializers import CustomerSerializer

from cx_metrics.multiple_choices.serializers import CachedMultipleChoiceSerializer, OptionTextSerializer
from cx_metrics.surveys.decorators import register_survey_serializer
from cx_metrics.surveys.models import Survey
from .models import NPSSurvey, NPSResponse
from .services import NPSService
from .services.cache import NPSInsightCacheService


@register_survey_serializer('NPS')
class NPSSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    url = serializers.URLField(read_only=True)
    contra_reason = CachedMultipleChoiceSerializer(source='contra', read_only=True)

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
            obj = NPSService.get_nps_survey(survey_id=instance.id)
            if obj is None:
                raise Http404
        return super(NPSSerializer, self).to_representation(obj)


class NPSSerializerV11(NPSSerializer):

    def __init__(self, instance=None, data=empty, **kwargs):
        if isinstance(instance, Survey):
            instance = NPSService.get_nps_survey(survey_id=instance.id)
        super(NPSSerializerV11, self).__init__(instance, data, **kwargs)
        contra = instance and instance.contra
        self.fields['contra_reason'] = CachedMultipleChoiceSerializer(source='contra', instance=contra)

    @transaction.atomic()
    def create(self, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']
        contra = contra_serializer.create(contra_data)
        v_data.update({'contra': contra})
        return super(NPSSerializerV11, self).create(v_data)

    def update(self, instance, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']

        if instance.contra and instance.contra.pk:
            contra = contra_serializer.update(instance.contra, contra_data)
        else:
            contra = contra_serializer.create(contra_data)

        v_data.update({'contra': contra})
        return super(NPSSerializerV11, self).update(instance, v_data)


class NPSInsightsSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    contra_options = OptionTextSerializer(source='contra_response_option_texts', many=True)

    class Meta:
        model = NPSSurvey
        fields = ('id', 'name', 'promoters', 'passives', 'detractors', 'contra_options')


class NPSRespondSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = NPSResponse
        fields = ('score', 'customer')

    def __init__(self, instance=None, data=empty, **kwargs):
        c_kwargs = copy(kwargs)
        self.survey = c_kwargs.pop('survey')
        super(NPSRespondSerializer, self).__init__(instance, data, **c_kwargs)

    def to_representation(self, instance):
        return {
            'score': instance.score,
            'client_id': self.validated_data['customer'].client_id
        }

    def create(self, validated_data):
        customer = validated_data['customer']
        score = validated_data['score']
        return NPSService.respond(
            survey=self.survey,
            customer_uuid=customer.uuid,
            score=score,
        )

    def save(self, **kwargs):
        NPSInsightCacheService.delete(self.survey.uuid)
        return super(NPSRespondSerializer, self).save()


class NPSRespondSerializerV11(NPSRespondSerializer):
    options = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = NPSResponse
        fields = ('score', 'customer', 'options', 'survey_uuid')

    def to_internal_value(self, data):
        c_data = copy(data)
        if c_data['score'] >= 9:
            c_data.update({'options': []})
        return super(NPSRespondSerializerV11, self).to_internal_value(c_data)

    def validate_options(self, value):
        if value and self.survey.contra and self.survey.contra.enabled:
            for option_id in value:
                if not self.survey.contra.options.filter(id=option_id).exists():
                    raise ValidationError(_("Contra option and Survey not related!"))
            return value
        return None

    def validate(self, attrs):
        options = attrs.get('options')
        score = attrs['score']
        if score < 9 and self.survey.contra.required and not options:
            raise ValidationError(_("Contra is required!"))
        return attrs

    def create(self, validated_data):
        customer = validated_data['customer']
        score = validated_data['score']
        options = validated_data.get('options')

        return NPSService.respond(
            survey=self.survey,
            customer_uuid=customer.uuid,
            score=score,
            option_ids=options
        )
