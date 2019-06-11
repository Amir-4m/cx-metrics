#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class NPSAppConfig(AppConfig):
    label = 'nps'
    name = 'cx_metrics.nps'
    verbose_name = _('NPS')

    def ready(self):
        # Do not connect signals when running tests
        if not settings.TEST:  # pragma: no cover
            from cx_metrics.surveys.signals import manage_signal_receivers  # NOQA
            from .models import NPSSurvey
            manage_signal_receivers(NPSSurvey, connect=True)
