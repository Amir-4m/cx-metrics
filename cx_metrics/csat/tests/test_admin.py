#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from upkook_core.businesses.models import Business

from cx_metrics.csat.admin import CSATSurveyAdmin
from cx_metrics.csat.models import CSATSurvey
from cx_metrics.csat.services.csat import CSATService
from cx_metrics.multiple_choices.services import MultipleChoiceService
from cx_metrics.surveys.models import Survey


class MockRequest(object):
    def __init__(self, user=None):
        self.user = user


class CSATForm(forms.ModelForm):
    class Meta:
        model = CSATSurvey
        fields = "__all__"


class CSATSurveyAdminTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses', 'csat']

    def setUp(self):
        self.survey = Survey.objects.first()
        User = get_user_model()
        user = User.objects.first()
        self.admin = CSATSurveyAdmin(model=CSATSurvey, admin_site=AdminSite())
        self.request = MockRequest(user)

    def test_contra_reason(self):
        contra = MultipleChoiceService.create(text=self.id())
        csat_survey = CSATSurvey(contra=contra)
        url = reverse('admin:%s_%s_change' % (contra._meta.app_label, contra._meta.model_name), args=(contra.pk,))
        expected = mark_safe('%(contra)s<br /><a href="%(url)s" target="_blank">%(link_text)s</a>' % {
            'contra': contra,
            'url': url,
            'link_text': _('More...'),
        })

        self.assertEqual(self.admin.contra_question(csat_survey), expected)

    def test_contra_question_contra_is_none(self):
        csat_survey = CSATSurvey(contra=None)
        value = self.admin.contra_question(csat_survey)
        self.assertIsNone(value)

    def test_save_model(self):
        csat = CSATService.create_csat_survey(
            name="name",
            business=Business.objects.first(),
            text="text",
            question="question",
            message="message"
        )
        data = {
            "name": "name",
            "business": Business.objects.first().id,
            "survey": csat.survey.id,
            "text": "text",
            "question": "question",
            "message": "message",
        }

        self.assertIsNone(csat.author)
        form = CSATForm(instance=csat, data=data)
        form.is_valid()
        self.admin.save_model(self.request, csat, form, False)

        self.assertIsNotNone(csat.author)
        self.assertEqual(csat.author.id, self.request.user.id)
