#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from upkook_core.businesses.models import Business

from cx_metrics.multiple_choices.services import MultipleChoiceService
from cx_metrics.surveys.models import Survey
from ..services import NPSService
from ..admin import NPSSurveyAdmin, NPSResponseAdmin
from ..models import NPSSurvey, NPSResponse


class MockRequest(object):
    def __init__(self, user=None):
        self.user = user


class NPSForm(forms.ModelForm):
    class Meta:
        model = NPSSurvey
        fields = "__all__"


class NPSSurveyAdminTestCase(TestCase):
    fixtures = ['users', 'multiple_choices', 'nps']

    def setUp(self):
        self.survey = Survey.objects.first()
        User = get_user_model()
        user = User.objects.first()
        self.admin = NPSSurveyAdmin(model=NPSSurvey, admin_site=AdminSite())
        self.request = MockRequest(user)

    def test_contra_reason(self):
        contra = MultipleChoiceService.create(text=self.id())
        nps_survey = NPSSurvey(contra=contra)
        url = reverse('admin:%s_%s_change' % (contra._meta.app_label, contra._meta.model_name), args=(contra.pk,))
        expected = mark_safe('%(contra)s<br /><a href="%(url)s" target="_blank">%(link_text)s</a>' % {
            'contra': contra,
            'url': url,
            'link_text': _('More...'),
        })

        self.assertEqual(self.admin.contra_question(nps_survey), expected)

    def test_contra_question_contra_is_none(self):
        nps_survey = NPSSurvey(contra=None)
        value = self.admin.contra_question(nps_survey)
        self.assertIsNone(value)

    def test_save_model(self):
        nps = NPSService.create_nps_survey(
            name="name",
            business=Business.objects.first(),
            text="text",
            question="question",
            message="message"
        )
        data = {
            "name": "name",
            "business": Business.objects.first().id,
            "survey": nps.survey.id,
            "text": "text",
            "question": "question",
            "message": "message",
        }

        self.assertIsNone(nps.author)
        form = NPSForm(instance=nps, data=data)
        form.is_valid()
        self.admin.save_model(self.request, nps, form, False)

        self.assertIsNotNone(nps.author)
        self.assertEqual(nps.author.id, self.request.user.id)


class NPSResponseAdminTestCase(TestCase):
    def setUp(self):
        self.admin = NPSResponseAdmin(model=NPSResponse, admin_site=AdminSite())
        self.request = MockRequest()

    def test_has_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_has_change_permission(self):
        self.assertFalse(self.admin.has_change_permission(self.request))

    def test_has_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(self.request))
