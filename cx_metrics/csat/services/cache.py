#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.cache import cache


class CSATInsightCacheService:
    TIMEOUT = 4 * 60 * 60  # 4 hours

    @staticmethod
    def get(csat_survey_uuid):
        return cache.get("csat_insight-%s" % csat_survey_uuid)

    @staticmethod
    def set(csat_survey_uuid, data, timeout=TIMEOUT):
        cache.set("csat_insight-%s" % csat_survey_uuid, data, timeout)
