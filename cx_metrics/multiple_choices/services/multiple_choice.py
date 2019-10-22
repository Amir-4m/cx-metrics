#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from ..models import MultipleChoice, Option, OptionText, OptionResponse


class MultipleChoiceService(object):
    @staticmethod
    def get(*args, **kwargs):
        try:
            return MultipleChoice.objects.get(*args, **kwargs)
        except MultipleChoice.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(id_):
        return MultipleChoiceService.get(id=id_)

    @staticmethod
    def create(
            text, enabled=True, required=True,
            type_=MultipleChoice.TYPE_RADIO,
            other_enabled=True,
    ):
        return MultipleChoice.objects.create(
            text=text,
            enabled=enabled,
            required=required,
            type=type_,
            other_enabled=other_enabled,
        )

    @staticmethod
    def cache_representation(mc_id, representation):
        key = MultipleChoiceService.representation_cache_key(mc_id)
        cache.set(key=key, value=representation, timeout=1 * 60 * 60)  # 1hour

    @staticmethod
    def representation_from_cache(mc_id):
        key = MultipleChoiceService.representation_cache_key(mc_id)
        return cache.get(key=key)

    @staticmethod
    def representation_cache_key(mc_id):
        key = "multiple-choice-%d" % mc_id
        return key

    @staticmethod
    def create_options(multiple_choice, options_kwargs):
        options = []
        for kwargs in options_kwargs:
            kwargs.update({'multiple_choice': multiple_choice})
            options.append(Option(**kwargs))

        try:
            return Option.objects.bulk_create(options)
        except IntegrityError:
            raise ValidationError(_('Failed to create options'))

    @staticmethod
    def get_option(*args, **kwargs):
        try:
            return Option.objects.get(*args, **kwargs)
        except Option.DoesNotExist:
            return None

    @staticmethod
    def get_option_by_id(id_):
        return MultipleChoiceService.get_option(id=id_)

    @staticmethod
    def option_exists(multiple_choice, id_):
        return multiple_choice.options.filter(id=id_).exists()

    @staticmethod
    def option_text_exists(multiple_choice, text, option_id=None):
        qs = multiple_choice.options.filter(text=text)
        if option_id:
            qs = qs.exclude(id=option_id)
        return qs.exists()

    @staticmethod
    def create_option(multiple_choice, text, order, enabled=True):
        return Option.objects.create(
            multiple_choice=multiple_choice,
            text=text,
            order=order,
            enabled=enabled,
        )

    @staticmethod
    def update_options(multiple_choice, options_kwargs):
        new_options = []
        for kwargs in options_kwargs:
            option_id = kwargs.pop('id', None)
            if option_id:
                multiple_choice.options.filter(id=option_id).update(**kwargs)
            else:
                new_options.append(kwargs)

        MultipleChoiceService.create_options(multiple_choice, new_options)

    @staticmethod
    def delete_option(multiple_choice, option_id):
        multiple_choice.options.filter(id=option_id).delete()


class OptionResponseService(object):

    @staticmethod
    def get_or_create_option_text(defaults=None, **kwargs):
        return OptionText.objects.get_or_create(defaults=defaults, **kwargs)

    @staticmethod
    def create_option_response(customer_uuid, contra_option):
        return OptionResponse.objects.create(
            customer_uuid=customer_uuid,
            option_text=contra_option
        )

    @staticmethod
    def store_option_response(multiple_choice, customer_uuid, option_ids):
        for option_id in option_ids:
            option = MultipleChoiceService.get_option_by_id(option_id)
            contra_option = OptionResponseService.get_or_create_option_text(
                multiple_choice=multiple_choice, text=option.text
            )[0]
            OptionResponseService.create_option_response(
                customer_uuid=customer_uuid,
                contra_option=contra_option
            )
            OptionResponseService.change_option_text_count(contra_option, 'count', 1)

    @staticmethod
    def change_option_text_count(survey_option, field_name, amount):
        kwargs = {field_name: F(field_name) + amount}
        return OptionText.objects.filter(id=survey_option.id).update(**kwargs)

    @staticmethod
    def get_option_text(*args, **kwargs):
        try:
            return OptionText.objects.get(*args, **kwargs)
        except OptionText.DoesNotExist:
            return None

    @staticmethod
    def get_option_text_by_text(text_):
        return OptionResponseService.get_option_text(text=text_)
