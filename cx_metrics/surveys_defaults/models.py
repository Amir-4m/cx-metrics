#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.translation import ugettext_lazy as _

from upkook_core.industries.models import Industry


class ActiveDefaultOptionManager(models.Manager):
    def get_queryset(self):
        return super(ActiveDefaultOptionManager, self).get_queryset().filter(is_active=True)


class DefaultOption(models.Model):
    SURVEY_TYPE_NPS = 'nps'
    SURVEY_TYPE_CHOICES = (
        (SURVEY_TYPE_NPS, _('NPS')),
    )

    QUESTION_TYPE_CONTRA = 'contra'
    QUESTION_TYPE_CHOICES = (
        (QUESTION_TYPE_CONTRA, _('Contra')),
    )

    industry = models.ForeignKey(
        Industry, verbose_name=_("Industry"),
        related_name="default_options", on_delete=models.CASCADE
    )
    survey_type = models.CharField(_('Survey Type'), choices=SURVEY_TYPE_CHOICES, max_length=20)
    question_type = models.CharField(_('Question Type'), choices=QUESTION_TYPE_CHOICES, max_length=20)
    text = models.CharField(_('Text'), max_length=256)
    order = models.PositiveSmallIntegerField(_('Order'), default=0, db_index=True)
    is_active = models.BooleanField(_('Is Active'), default=True)

    objects = models.Manager()
    active_objects = ActiveDefaultOptionManager()

    class Meta:
        verbose_name = _('Default Option')
        verbose_name_plural = _('Default Options')
        unique_together = ('survey_type', 'question_type', 'order')

    def __str__(self):
        return self.text
