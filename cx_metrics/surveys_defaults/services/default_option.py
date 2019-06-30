#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import DefaultOption


class DefaultOptionService(object):

    @staticmethod
    def get_default_options_by_industry_and_survey_type(industry, survey_type, ordering=None):
        default_options = DefaultOption.active_objects.filter(
            industry=industry, survey_type=survey_type
        )
        if ordering is not None:
            default_options = default_options.order_by(*ordering)
        return default_options
