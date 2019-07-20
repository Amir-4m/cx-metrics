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

    @staticmethod
    def get_csat_survey(*args, **kwargs):
        try:
            return CSATSurvey.objects.get(*args, **kwargs)
        except CSATSurvey.DoesNotExist:
            return None

    @staticmethod
    def get_csat_survey_by_id(id_):
        return CSATService.get_csat_survey(id=id_)

    @staticmethod
    def get_csat_survey_by_uuid(uuid_):
        return CSATService.get_csat_survey(uuid=uuid_)

    @staticmethod
    def get_csat_surveys_by_business(business, ordering=None):
        csat_surveys = CSATSurvey.objects.filter(business=business)
        if ordering is not None:
            csat_surveys = csat_surveys.order_by(*ordering)
        return csat_surveys
