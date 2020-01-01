#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf import settings
from django.utils import timezone
from datetime import datetime

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
    def get_survey(*args, **kwargs):
        try:
            return Survey.objects.get(*args, **kwargs)
        except Survey.DoesNotExist:
            return None

    @staticmethod
    def get_survey_by_uuid(uuid_):
        return SurveyService.get_survey(uuid=uuid_)

    @staticmethod
    def all():
        return Survey.objects.all()

    @staticmethod
    def is_duplicate_response(last_response):
        if last_response:
            ts = datetime.timestamp(last_response.created)
            if datetime.timestamp(timezone.now()) - ts < int(settings.RESPONSE_DUPLICATE_BLOCK_TIME):
                return True
        return False
