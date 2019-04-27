#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import NPSSurvey


class NPSService(object):

    @staticmethod
    def create_nps_survey(name, business, text, question, message, text_enabled=True):
        return NPSSurvey.objects.create(
            name=name,
            business=business,
            text=text,
            question=question,
            message=message,
            text_enabled=text_enabled,
        )

    @staticmethod
    def get_nps_survey(*args, **kwargs):
        try:
            return NPSSurvey.objects.get(*args, **kwargs)
        except NPSSurvey.DoesNotExist:
            return None

    @staticmethod
    def get_nps_survey_by_id(id_):
        return NPSService.get_nps_survey(id=id_)

    @staticmethod
    def get_nps_survey_by_uuid(uuid_):
        return NPSService.get_nps_survey(uuid=uuid_)

    @staticmethod
    def get_nps_surveys_by_business(business, ordering=None):
        nps_surveys = NPSSurvey.objects.filter(business=business)
        if ordering is not None:
            nps_surveys = nps_surveys.order_by(*ordering)
        return nps_surveys
