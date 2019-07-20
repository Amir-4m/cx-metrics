#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from ..models import CSATSurvey


class CSATService(object):

    @staticmethod
    def create_csat_survey(name, business, text, question, message, text_enabled=True, scale_=CSATSurvey.SCALE_1_TO_3):
        return CSATSurvey.objects.create(
            name=name,
            business=business,
            text=text,
            question=question,
            message=message,
            text_enabled=text_enabled,
            scale=scale_
        )
