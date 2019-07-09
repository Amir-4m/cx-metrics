#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db.models import F

from cx_metrics.multiple_choices.services import MultipleChoiceService
from cx_metrics.nps.models import ContraResponse, ContraOption


class ContraService(object):

    @staticmethod
    def get_or_create_contra_option(defaults=None, **kwargs):
        return ContraOption.objects.get_or_create(defaults=defaults, **kwargs)

    @staticmethod
    def create_contra_response(nps_response, contra_option):
        return ContraResponse.objects.create(
            nps_response=nps_response,
            contra_option=contra_option
        )

    @staticmethod
    def store_contra_response(survey, nps_response, option_ids):
        for option_id in option_ids:
            option = MultipleChoiceService.get_option_by_id(option_id)
            contra_option = ContraService.get_or_create_contra_option(
                nps_survey=survey, text=option.text
            )[0]
            ContraService.create_contra_response(
                nps_response=nps_response,
                contra_option=contra_option
            )
            ContraService.change_contra_option_count(contra_option, 'count', 1)

    @staticmethod
    def change_contra_option_count(contra_option, field_name, amount):
        kwargs = {field_name: F(field_name) + amount}
        return ContraOption.objects.filter(id=contra_option.id).update(**kwargs)
