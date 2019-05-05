#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import Survey


class SurveyService(object):
    @staticmethod
    def get_surveys_by_business(business, ordering=None):
        surveys = Survey.objects.filter(business=business)
        if ordering is not None:
            surveys = surveys.order_by(*ordering)
        return surveys

    @staticmethod
    def survey_with_uuid_exists(survey_uuid):
        return Survey.objects.filter(uuid=survey_uuid).exists()

    @staticmethod
    def all():
        return Survey.objects.all()
