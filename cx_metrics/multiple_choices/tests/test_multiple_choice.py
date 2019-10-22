#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from ..models import MultipleChoice, Option


class MultipleChoiceTestCase(TestCase):
    def test_str(self):
        mc = MultipleChoice(text=self.id())
        self.assertEqual(str(mc), self.id())

    def test_is_radio(self):
        mc = MultipleChoice(text=self.id(), type=MultipleChoice.TYPE_RADIO)
        self.assertTrue(mc.is_radio())

    def test_is_select(self):
        mc = MultipleChoice(text=self.id(), type=MultipleChoice.TYPE_SELECT)
        self.assertTrue(mc.is_select())

    def test_is_checkbox(self):
        mc = MultipleChoice(text=self.id(), type=MultipleChoice.TYPE_CHECKBOX)
        self.assertTrue(mc.is_checkbox())

    def test_is_multi_select(self):
        mc = MultipleChoice(text=self.id(), type=MultipleChoice.TYPE_MULTI_SELECT)
        self.assertTrue(mc.is_multi_select())


class OptionTestCase(TestCase):
    fixtures = ['multiple_choices']

    def test_str(self):
        option = Option(text=self.id())
        self.assertEqual(str(option), self.id())

    def test_delete_option(self):
        option = Option.objects.first()
        self.assertTrue(option.delete_option(True))

    def test_delete_option_false(self):
        option = Option.objects.first()
        self.assertFalse(option.delete_option(False))
