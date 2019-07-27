#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import math

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
from .models import CSATSurvey, CSATResponse
from .services import CSATService


@register_survey_serializer('CSAT')
class CSATSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    url = serializers.URLField(read_only=True)
    contra_reason = CachedMultipleChoiceSerializer(source='contra')

    def __init__(self, instance=None, data=empty, **kwargs):
        if isinstance(instance, Survey):
            instance = CSATService.get_csat_survey(survey_id=instance.id)
        super(CSATSerializer, self).__init__(instance, data, **kwargs)
        contra = instance and instance.contra
        self.fields['contra_reason'] = CachedMultipleChoiceSerializer(source='contra', instance=contra)

    class Meta:
        model = CSATSurvey
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
            obj = CSATService.get_csat_survey(survey_id=instance.id)
            if obj is None:
                raise Http404
        return super(CSATSerializer, self).to_representation(obj)

    @transaction.atomic()
    def create(self, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']
        contra = contra_serializer.create(contra_data)
        v_data.update({'contra': contra})
        return super(CSATSerializer, self).create(v_data)

    def update(self, instance, validated_data):
        v_data = copy(validated_data)
        contra_data = v_data.pop('contra', {})
        contra_serializer = self.fields['contra_reason']

        if instance.contra and instance.contra.pk:
            contra = contra_serializer.update(instance.contra, contra_data)
        else:
            contra = contra_serializer.create(contra_data)

        v_data.update({'contra': contra})
        return super(CSATSerializer, self).update(instance, v_data)


class CSATRespondSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    options = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = CSATResponse
        fields = ('rate', 'customer', 'options', 'survey_uuid')

    def __init__(self, instance=None, data=empty, **kwargs):
        c_kwargs = copy(kwargs)
        self.survey = c_kwargs.pop('survey')
        super(CSATRespondSerializer, self).__init__(instance, data, **c_kwargs)

    def to_representation(self, instance):
        return {
            'rate': instance.rate,
            'client_id': self.validated_data['customer'].client_id
        }

    def to_internal_value(self, data):
        c_data = copy(data)
        scale = int(self.survey.scale)
        rate = c_data['rate']

        if rate >= math.ceil(scale / 2):
            c_data.update({'options': []})
        return super(CSATRespondSerializer, self).to_internal_value(c_data)

    def validate_options(self, value):
        if value and self.survey.contra and self.survey.contra.enabled:
            for option_id in value:
                if not self.survey.contra.options.filter(id=option_id).exists():
                    raise ValidationError(_("Contra option and Survey not related!"))
            return value
        return None

    def validate(self, attrs):
        scale = int(self.survey.scale)
        options = attrs.get('options')
        rate = attrs['rate']

        if rate < math.ceil(scale / 2) and self.survey.contra.required and not options:
            raise ValidationError(_('Contra is required'))
        return attrs

    def create(self, validated_data):
        customer = validated_data['customer']
        rate = validated_data['rate']
        options = validated_data.get('options')

        return CSATService.respond(
            survey=self.survey,
            customer_uuid=customer.uuid,
            rate=rate,
            option_ids=options
        )


class CSATInsightSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    contra_options = OptionTextSerializer(source='contra_response_option_texts', many=True)

    class Meta:
        model = CSATSurvey
        fields = ('id', 'name', 'scale', 'contra_options')
