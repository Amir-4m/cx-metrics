#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.contrib.admin import AdminSite
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cx_metrics.multiple_choices.services import MultipleChoiceService
from ..admin import CESSurveyAdmin
from ..models import CESSurvey


class CESSurveyAdminTestCase(TestCase):

    def setUp(self):
        self.admin = CESSurveyAdmin(model=CESSurvey, admin_site=AdminSite())

    def test_contra_reason(self):
        contra = MultipleChoiceService.create(text=self.id())
        ces_survey = CESSurvey(contra=contra)
        url = reverse('admin:%s_%s_change' % (contra._meta.app_label, contra._meta.model_name), args=(contra.pk,))
        expected = mark_safe('%(contra)s<br /><a href="%(url)s" target="_blank">%(link_text)s</a>' % {
            'contra': contra,
            'url': url,
            'link_text': _('More...'),
        })

        self.assertEqual(self.admin.contra_question(ces_survey), expected)

    def test_contra_question_contra_is_none(self):
        ces_survey = CESSurvey(contra=None)
        value = self.admin.contra_question(ces_survey)
        self.assertIsNone(value)
