#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4
from django.test import TestCase
from ..models import NPSSurvey


class NPSSurveyTestCase(TestCase):
    def test_type(self):
        self.assertEqual(NPSSurvey().type, 'NPS')

    def testURL(self):
        uuid_ = uuid4()
        expected_url = 'https://www.upkook.com/bizz/s/%s/' % uuid_
        self.assertEqual(NPSSurvey(uuid=uuid_).url, expected_url)
