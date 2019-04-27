#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from cx_metrics.surveys.models import SurveyModel
from cx_metrics.surveys.decorators import register_survey


@register_survey('NPS')
class NPSSurvey(SurveyModel):
    text = models.TextField(_('Intro Text'), max_length=1000)
    text_enabled = models.BooleanField(_('Is Intro Enabled'), default=True)
    question = models.TextField(_('Question'), max_length=256)
    message = models.TextField(_('Thank You Message'), max_length=256)

    class Meta:
        verbose_name = _('NPS Survey')
        verbose_name_plural = _('NPS Surveys')

    @cached_property
    def type(self):
        return 'NPS'
