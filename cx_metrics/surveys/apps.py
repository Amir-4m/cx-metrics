#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from . import settings as app_settings


class SurveyAppConfig(AppConfig):
    label = 'surveys'
    name = 'cx_metrics.surveys'
    verbose_name = _('Surveys')

    def ready(self):
        for name in dir(app_settings):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(app_settings, name))
