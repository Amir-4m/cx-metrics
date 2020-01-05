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
from upkook_core.customers.services import CustomerService

from cx_metrics.ces.models import CESSurvey, CESResponse
from cx_metrics.ces.services import CESService
from cx_metrics.multiple_choices.serializers import (
    CachedMultipleChoiceSerializer,
    OptionTextSerializer,
    MultipleChoiceRespondSerializer
)
from cx_metrics.surveys.decorators import register_survey_serializer
from cx_metrics.surveys.models import Survey
from cx_metrics.surveys.services import SurveyInsightCacheService, SurveyService


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


class CESRespondSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    options = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = CESResponse
        fields = ('rate', 'customer', 'options', 'survey_uuid')

    def __init__(self, instance=None, data=empty, **kwargs):
        c_kwargs = copy(kwargs)
        self.survey = c_kwargs.pop('survey')
        super(CESRespondSerializer, self).__init__(instance, data, **c_kwargs)
        self.fields["options"] = MultipleChoiceRespondSerializer(mc_id=self.survey.contra_id, required=False)

    def to_representation(self, instance):
        return {
            'rate': instance.rate,
            'client_id': instance.customer.client_id
        }

    def validate_options(self, value):
        if value and self.survey.has_contra():
            return value
        return None

    def validate_rate(self, value):
        scale = int(self.survey.scale)
        if value > scale:
            raise ValidationError(_("Rate is out of range!"))
        return value

    def validate(self, attrs):
        scale = int(self.survey.scale)
        options = attrs.get('options')
        rate = attrs['rate']
        if rate and rate >= math.ceil(scale / 2):
            attrs.update({'options': []})
        if rate < math.ceil(scale / 2) and self.survey.has_contra() and self.survey.contra.required and not options:
            raise ValidationError(_('Contra is required'))
        return attrs

    def create(self, validated_data):
        customer_data = validated_data.get('customer', {})

        client_id = customer_data.get('client_id')
        user_agent = validated_data.get('user_agent', None)

        business = self.survey.business
        if business.is_identified_by_email():
            email = customer_data.get('email')
            if not email:
                raise ValidationError(_('Email is required'))
            customer = CustomerService.identify_by_email(
                business=self.survey.business, email=email, client_id=client_id, user_agent=user_agent
            )
        elif business.is_identified_by_mobile_number():
            mobile_number = customer_data.get('mobile_number')
            if not mobile_number:
                raise ValidationError(_('Mobile number is required'))
            customer = CustomerService.identify_by_mobile_number(
                business=self.survey.business, mobile_number=mobile_number, client_id=client_id, user_agent=user_agent
            )
        elif business.is_identified_by_bizz_user_id():
            bizz_user_id = customer_data.get('bizz_user_id')
            if not bizz_user_id:
                raise ValidationError(_('Business UserID is required'))
            customer = CustomerService.identify_by_bizz_user_id(
                business=self.survey.business, bizz_user_id=bizz_user_id, client_id=client_id, user_agent=user_agent
            )
        else:
            customer = CustomerService.identify_anonymous(
                business=self.survey.business, client_id=client_id
            )

        last_response = CESService.get_last_response(customer)
        if SurveyService.is_duplicate_response(last_response):
            raise ValidationError(
                {
                    "non_field_errors": _("You could not submit responses within specific time !")
                }
            )

        rate = validated_data['rate']
        options = validated_data.get('options')

        return CESService.respond(
            survey=self.survey,
            customer_uuid=customer.uuid,
            rate=rate,
            option_ids=options
        )

    def save(self, **kwargs):
        SurveyInsightCacheService.delete(self.survey.type, self.survey.uuid)
        return super(CESRespondSerializer, self).save(**kwargs)


class CESInsightSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    contra_options = OptionTextSerializer(source='contra_response_option_texts', many=True)

    class Meta:
        model = CESSurvey
        fields = ('id', 'name', 'scale', 'contra_options')
