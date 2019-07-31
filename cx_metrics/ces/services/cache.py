#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.cache import cache


class CESInsightCacheService:
    TIMEOUT = 4 * 60 * 60  # 4 hours

    @staticmethod
    def get(ces_survey_uuid):
        return cache.get("ces_insight-%s" % ces_survey_uuid)

    @staticmethod
    def set(ces_survey_uuid, data, timeout=TIMEOUT):
        cache.set("ces_insight-%s" % ces_survey_uuid, data, timeout)
