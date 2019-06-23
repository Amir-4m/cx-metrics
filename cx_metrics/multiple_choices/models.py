#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cx_metrics.questions.models import Question


class MultipleChoice(Question):
    TYPE_RADIO = 'R'
    TYPE_SELECT = 'S'
    TYPE_CHECKBOX = 'C'
    TYPE_MULTI_SELECT = 'M'

    TYPE_CHOICES = (
        (TYPE_RADIO, _('Radio')),
        (TYPE_SELECT, _('Dropdown')),
        (TYPE_CHECKBOX, _('Checkboxes')),
        (TYPE_MULTI_SELECT, _('Multi Dropdown')),
    )

    type = models.CharField(_('Type'), max_length=1, choices=TYPE_CHOICES, default=TYPE_RADIO)
    other_enabled = models.BooleanField(_('Is Other Option Enabled'), default=False)

    class Meta:
        abstract = False
        verbose_name = _('Multiple Choice Question')
        verbose_name_plural = _('Multiple Choice Questions')


class Option(models.Model):
    multiple_choice = models.ForeignKey(
        MultipleChoice, verbose_name=_('Multiple Choice'),
        related_name='options', on_delete=models.PROTECT,
    )
    text = models.CharField(_('Text'), max_length=256)
    enabled = models.BooleanField(_('Is Enabled'), default=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=0, db_index=True)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Option')
        verbose_name_plural = _('Options')
        unique_together = (
            ('multiple_choice', 'text'),
        )
        ordering = ('order',)

    def __str__(self):
        return self.text
