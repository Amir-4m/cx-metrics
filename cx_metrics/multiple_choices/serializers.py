#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from copy import copy
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import MultipleChoice, Option, OptionText
from .services import MultipleChoiceService


class OptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Option
        fields = ('id', 'text', 'enabled', 'order')


class MultipleChoiceRespondSerializer(serializers.ListSerializer):

    def __init__(self, **kwargs):
        default_kwargs = {'child': serializers.IntegerField()}
        default_kwargs.update(**kwargs)
        contra_id = default_kwargs.pop("mc_id", None)
        self.contra = MultipleChoiceService.get_by_id(contra_id)
        super(MultipleChoiceRespondSerializer, self).__init__(**default_kwargs)

    def validate(self, value):

        if self.contra is None:
            raise ValidationError(_("Contra could not be none !"))

        elif not value and self.contra.required:
            raise ValidationError(_("At least 1 option should be chosen !"))

        elif value:
            if len(value) > 1 and self.contra.one_option_accept_type():
                raise ValidationError(_("Only 1 option can be chosen !"))

            for option_id in value:
                if not self.contra.options.filter(id=option_id).exists():
                    raise ValidationError(_("Contra option and Survey not related!"))

        return value


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

        orders = [option.get('order') for option in options]
        if len(orders) != len(set(orders)):
            raise ValidationError(_('You should not have duplicate option orders'))
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


class OptionTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionText
        fields = ('text', 'count')
