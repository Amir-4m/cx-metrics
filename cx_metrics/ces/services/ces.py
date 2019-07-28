#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from ..models import CESSurvey


class CESService(object):
    @staticmethod
    def get_ces_survey(*args, **kwargs):
        try:
            return CESSurvey.objects.get(*args, **kwargs)
        except CESSurvey.DoesNotExist:
            return None

    @staticmethod
    def get_ces_survey_by_id(id_):
        return CESService.get_ces_survey(id=id_)
