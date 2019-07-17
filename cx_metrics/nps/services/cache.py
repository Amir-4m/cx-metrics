#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.cache import cache


class NPSInsightCacheService:
    TIMEOUT = 4 * 60 * 60  # 4 hours

    @staticmethod
    def get(nps_survey_uuid):
        return cache.get("nps_insight-%s" % nps_survey_uuid)

    @staticmethod
    def set(nps_survey_uuid, data, timeout=TIMEOUT):
        cache.set("nps_insight-%s" % nps_survey_uuid, data, timeout)

    @staticmethod
    def delete(nps_survey_uuid):
        cache.delete("nps_insight-%s" % nps_survey_uuid)
