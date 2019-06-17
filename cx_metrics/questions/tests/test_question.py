#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from ..models import Question


class QuestionTestCase(TestCase):
    def test_str(self):
        question = Question(text=self.id())
        self.assertEqual(str(question), self.id())
