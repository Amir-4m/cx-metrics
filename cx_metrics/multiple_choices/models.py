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

    def is_radio(self):
        return self.type == "R"

    def is_select(self):
        return self.type == "S"

    def is_checkbox(self):
        return self.type == "C"

    def is_multi_select(self):
        return self.type == "M"

    def one_option_accept_type(self):
        return self.type == "R" or self.type == "S"


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

    # FIXME: Implement a seperate API for deleting an option
    def delete_option(self, value):
        if value:
            return True
        return False


class OptionText(models.Model):
    multiple_choice = models.ForeignKey(
        MultipleChoice, verbose_name=_('Multiple Choice'),
        related_name='option_texts', on_delete=models.PROTECT,
    )
    text = models.CharField(_('Text'), max_length=256)
    count = models.PositiveIntegerField(_('Count'), default=0)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Option Text')
        verbose_name_plural = _('Option Texts')
        unique_together = ('multiple_choice', 'text')

    def __str__(self):
        return self.text


class OptionResponse(models.Model):
    option_text = models.ForeignKey(
        OptionText, verbose_name=_('Option Response'),
        related_name='option_response', on_delete=models.PROTECT
    )
    customer_uuid = models.UUIDField(_('Customer UUID'), editable=False)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Option Response')
        verbose_name_plural = _('Option Responses')

    def __str__(self):
        return str(self.option_text)
