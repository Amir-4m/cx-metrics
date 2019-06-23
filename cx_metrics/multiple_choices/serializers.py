#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import MultipleChoice, Option
from .services import MultipleChoiceService


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'enabled', 'order')


class MultipleChoiceSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=True)

    class Meta:
        model = MultipleChoice
        fields = ('type', 'text', 'enabled', 'required', 'other_enabled', 'options')

    def validate_options(self, options):
        texts = [option['text'] for option in options]

        if len(texts) != len(set(texts)):
            raise ValidationError(_('You should not have duplicate option texts'))

        return options

    def create(self, validated_data):
        v_data = copy(validated_data)
        options = v_data.pop('options', [])
        instance = super(MultipleChoiceSerializer, self).create(v_data)
        MultipleChoiceService.create_options(instance, options)
        return instance

    def validate(self, attrs):
        enabled = attrs.get('enabled', True)
        options = attrs.get('options', [])

        if enabled and sum([1 for option in options if option.get('enabled', True)]) < 2:
            raise ValidationError(_('You should provide at least 2 enabled options.'))

        return attrs
