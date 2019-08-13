#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from upkook_core.customers.services import CustomerService

from cx_metrics.multiple_choices.models import MultipleChoice
from cx_metrics.surveys.decorators import register_survey
from cx_metrics.surveys.models import SurveyModel, SurveyResponseBase


@register_survey('CES')
class CESSurvey(SurveyModel):
    SCALE_1_TO_3 = '3'
    SCALE_1_TO_5 = '5'
    SCALE_1_TO_7 = '7'
    SCALE_CHOICES = (
        (SCALE_1_TO_3, _('3 Choices')),
        (SCALE_1_TO_5, _('5 Choices')),
        (SCALE_1_TO_7, _('7 Choices')),
    )
    text = models.TextField(_('Intro Text'), max_length=1000)
    text_enabled = models.BooleanField(_('Is Intro Enabled'), default=True)
    question = models.TextField(_('Question'), max_length=256)
    message = models.TextField(_('Thank You Message'), max_length=256)
    scale = models.CharField(_('Scale'), max_length=1, choices=SCALE_CHOICES, default=SCALE_1_TO_3)
    contra = models.OneToOneField(
        MultipleChoice, related_name='ces_survey', on_delete=models.PROTECT,
        verbose_name=_('Contra'), null=True, default=None
    )

    class Meta:
        verbose_name = _('CES Survey')
        verbose_name_plural = _('CES Survey')

    @cached_property
    def type(self):
        return 'CES'

    @property
    def contra_response_option_texts(self):
        if self.contra:
            return self.contra.option_texts.all()
        return []

    def has_contra(self):
        return self.contra and self.contra.enabled


class CESResponse(SurveyResponseBase):
    rate = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])

    class Meta:
        verbose_name = _('CES Response')
        verbose_name_plural = _('CES Responses')

    @cached_property
    def customer(self):
        return CustomerService.get_customer_by_uuid(self.customer_uuid)
