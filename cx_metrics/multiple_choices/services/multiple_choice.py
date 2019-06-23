#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from ..models import MultipleChoice, Option


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
    def create_options(multiple_choice, options_kwargs):
        options = []
        for kwargs in options_kwargs:
            kwargs.update({'multiple_choice': multiple_choice})
            options.append(Option(**kwargs))

        try:
            return Option.objects.bulk_create(options)
        except IntegrityError:
            raise ValidationError(_('Failed to create options'))
