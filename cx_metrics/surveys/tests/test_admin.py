#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from ..admin import SurveyAdmin
from ..models import Survey


class MockRequest(object):
    def __init__(self):
        pass


class SurveyAdminTestCase(TestCase):
    def setUp(self):
        self.survey_admin = SurveyAdmin(model=Survey, admin_site=AdminSite())
        self.request = MockRequest()

    def test_open_survey(self):
        survey = Survey(uuid=uuid4())
        value = self.survey_admin.open_survey(survey)
        expect_value = '<a href="%(url)s" target="_blank">Open Survey</a>' % {'url': survey.url}
        self.assertEqual(value, expect_value)

    def test_has_add_permission_false(self):
        self.assertFalse(self.survey_admin.has_add_permission(request=self.request))

    def test_has_change_permission_false(self):
        self.assertFalse(self.survey_admin.has_change_permission(request=self.request))

    def test_has_delete_permission_false(self):
        self.assertFalse(self.survey_admin.has_delete_permission(request=self.request))
