#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import MultipleChoice


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
