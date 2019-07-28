#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import CESSurvey


class CESService(object):
    @staticmethod
    def create_ces_survey(name, business, text, question, message, text_enabled=True, scale_=CESSurvey.SCALE_1_TO_3):
        return CESSurvey.objects.create(
            name=name,
            business=business,
            text=text,
            question=question,
            message=message,
            text_enabled=text_enabled,
            scale=scale_
        )

    @staticmethod
    def get_ces_survey(*args, **kwargs):
        try:
            return CESSurvey.objects.get(*args, **kwargs)
        except CESSurvey.DoesNotExist:
            return None

    @staticmethod
    def get_ces_survey_by_id(id_):
        return CESService.get_ces_survey(id=id_)

    @staticmethod
    def get_ces_surveys_by_business(business, ordering=None):
        ces_surveys = CESSurvey.objects.filter(business=business)
        if ordering is not None:
            ces_surveys = ces_surveys.order_by(*ordering)
        return ces_surveys

    @staticmethod
    def get_ces_survey_by_uuid(uuid_):
        return CESService.get_ces_survey(uuid=uuid_)
