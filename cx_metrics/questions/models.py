#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Question(models.Model):
    text = models.TextField(_('Text'), max_length=256)
    enabled = models.BooleanField(_('Is Enabled'), default=True)
    required = models.BooleanField(_('Is Required'), default=True)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return self.text
