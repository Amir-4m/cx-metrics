#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from ..models import MultipleChoice, Option


class MultipleChoiceTestCase(TestCase):
    def test_str(self):
        mc = MultipleChoice(text=self.id())
        self.assertEqual(str(mc), self.id())


class OptionTestCase(TestCase):
    def test_str(self):
        option = Option(text=self.id())
        self.assertEqual(str(option), self.id())
