#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from cx_metrics.multiple_choices.models import MultipleChoice
from cx_metrics.surveys.models import SurveyModel, SurveyResponseBase
from cx_metrics.surveys.decorators import register_survey


@register_survey('NPS')
class NPSSurvey(SurveyModel):
    text = models.TextField(_('Intro Text'), max_length=1000)
    text_enabled = models.BooleanField(_('Is Intro Enabled'), default=True)
    question = models.TextField(_('Question'), max_length=256)
    message = models.TextField(_('Thank You Message'), max_length=256)
    promoters = models.BigIntegerField(_('Promoters'), default=0, validators=[MinValueValidator(0)])
    passives = models.BigIntegerField(_('Passives'), default=0, validators=[MinValueValidator(0)])
    detractors = models.BigIntegerField(_('Detractors'), default=0, validators=[MinValueValidator(0)])
    contra = models.OneToOneField(
        MultipleChoice, related_name='nps_survey', on_delete=models.PROTECT,
        verbose_name=_('Contra'), null=True, default=None,
    )

    class Meta:
        verbose_name = _('NPS Survey')
        verbose_name_plural = _('NPS Surveys')

    @cached_property
    def type(self):
        return 'NPS'


class NPSResponse(SurveyResponseBase):
    score = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        verbose_name = _('NPS Response')
        verbose_name_plural = _('NPS Responses')


class ContraOption(models.Model):
    nps_survey = models.ForeignKey(
        NPSSurvey, verbose_name=_('NPS Survey'),
        related_name='contra_options', on_delete=models.PROTECT
    )
    text = models.TextField(_('Text'), max_length=256)
    count = models.PositiveIntegerField(_('Count'), default=0)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Contra Option')
        verbose_name_plural = _('Contra Options')
        unique_together = ('nps_survey', 'text')

    def __str__(self):
        return self.text


class ContraResponse(models.Model):
    nps_response = models.ForeignKey(
        NPSResponse, verbose_name=_('NPS Response'),
        related_name=_('contra_responses'), on_delete=models.CASCADE
    )
    contra_option = models.ForeignKey(
        ContraOption, verbose_name=_('Contra Option'),
        related_name='contra_responses', on_delete=models.PROTECT
    )
    created = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Contra Response')
        verbose_name_plural = _('Contra Responses')

    def __str__(self):
        return str(self.contra_option)
