#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import MultipleChoice, Option
from .services import MultipleChoiceService


class OptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Option
        fields = ('id', 'text', 'enabled', 'order')


class MultipleChoiceSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=True)

    class Meta:
        model = MultipleChoice
        fields = ('type', 'text', 'enabled', 'required', 'other_enabled', 'options')

    def validate_options(self, options):
        for option in options:
            option_id = option.get('id')
            if option_id and not (self.instance and MultipleChoiceService.option_exists(self.instance, option_id)):
                raise ValidationError(_('Option %(id)s does not exists') % {'id': option_id})

        texts = [option['text'] for option in options]
        if len(texts) != len(set(texts)):
            raise ValidationError(_('You should not have duplicate option texts'))

        return options

    def create(self, validated_data):
        v_data = copy(validated_data)
        options = v_data.pop('options', [])
        instance = super(MultipleChoiceSerializer, self).create(v_data)
        MultipleChoiceService.create_options(instance, options)
        serializer = MultipleChoiceSerializer(instance)
        representation = serializer.to_representation(instance)
        MultipleChoiceService.cache_representation(instance.id, representation)
        return instance

    def update(self, instance, validated_data):
        v_data = copy(validated_data)
        options = v_data.pop('options', [])
        instance = super(MultipleChoiceSerializer, self).update(instance, v_data)
        MultipleChoiceService.update_options(instance, options)
        serializer = MultipleChoiceSerializer(instance)
        representation = serializer.to_representation(instance)
        MultipleChoiceService.cache_representation(instance.id, representation)
        return instance

    def validate(self, attrs):
        enabled = attrs.get('enabled', True)
        options = attrs.get('options', [])

        if self.instance:
            for option in options:
                text = option.get('text')
                option_id = option.get('id')
                if MultipleChoiceService.option_text_exists(self.instance, text, option_id):
                    raise ValidationError(_('You should not have duplicate option texts'))

        if enabled and sum([1 for option in options if option.get('enabled', True)]) < 2:
            raise ValidationError(_('You should provide at least 2 enabled options.'))

        return attrs


class CachedMultipleChoiceSerializer(MultipleChoiceSerializer):
    def to_representation(self, instance):
        representation = MultipleChoiceService.representation_from_cache(instance.id)

        if not representation:
            representation = super(CachedMultipleChoiceSerializer, self).to_representation(instance)
            MultipleChoiceService.cache_representation(instance.id, representation)
        return representation
