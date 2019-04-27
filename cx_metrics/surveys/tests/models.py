#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.functional import cached_property

from ..models import SurveyModel


class TestSurvey(SurveyModel):
    enabled = models.BooleanField(default=True)

    @cached_property
    def type(self):
        return 'TEST'
