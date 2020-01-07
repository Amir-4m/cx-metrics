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
from upkook_core.customers.services import CustomerService

from cx_metrics.multiple_choices.serializers import (
    CachedMultipleChoiceSerializer,
    OptionTextSerializer,
    MultipleChoiceRespondSerializer
)
from cx_metrics.surveys.decorators import register_survey_serializer
from cx_metrics.surveys.models import Survey
from .models import NPSSurvey, NPSResponse
from .services import NPSService
from cx_metrics.surveys.services import SurveyInsightCacheService, SurveyService


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
            'client_id': instance.customer.client_id
        }

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
        last_response = NPSService.get_last_response(customer)
        if SurveyService.is_duplicate_response(last_response):
            raise ValidationError(
                {
                    "non_field_errors": _("You could not submit responses within specific time !")
                }
            )

        score = validated_data['score']
        contra_options = validated_data.get('contra_options')
        return NPSService.respond(
            survey=self.survey,
            customer_uuid=customer.uuid,
            score=score,
            contra_options_ids=contra_options
        )

    def save(self, **kwargs):
        SurveyInsightCacheService.delete(self.survey.type, self.survey.uuid)
        return super(NPSRespondSerializer, self).save(**kwargs)


class NPSRespondSerializerV11(NPSRespondSerializer):
    contra_options = serializers.ListField(child=serializers.IntegerField(), required=False)

    def __init__(self, instance=None, data=empty, **kwargs):
        c_kwargs = copy(kwargs)
        self.survey = c_kwargs.pop('survey')
        super(NPSRespondSerializer, self).__init__(instance, data, **c_kwargs)
        self.fields["contra_options"] = MultipleChoiceRespondSerializer(mc_id=self.survey.contra_id, required=False)

    class Meta:
        model = NPSResponse
        fields = ('score', 'customer', 'contra_options', 'survey_uuid')

    def validate_contra_options(self, value):
        if value and self.survey.has_contra():
            return value
        return None

    def validate(self, attrs):
        contra_options = attrs.get('contra_options')
        score = attrs['score']
        if score and score >= 9:
            attrs.update({'contra_options': []})
        if score < 9 and self.survey.has_contra() and self.survey.contra.required and not contra_options:
            raise ValidationError(_("Contra is required!"))
        return attrs
