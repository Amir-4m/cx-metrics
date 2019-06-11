#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.cache import cache


class SurveyCacheService:
    TIMEOUT = 4 * 60 * 60  # 4 hours

    @staticmethod
    def get(survey_uuid):
        return cache.get("survey-%s" % survey_uuid)

    @staticmethod
    def set(survey_uuid, data, timeout=TIMEOUT):
        cache.set("survey-%s" % survey_uuid, data, timeout)

    @staticmethod
    def delete(survey_uuid):
        cache.delete("survey-%s" % survey_uuid)
