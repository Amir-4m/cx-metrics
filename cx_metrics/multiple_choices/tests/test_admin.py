#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory
from django.test import TestCase, override_settings

from ..admin import MultipleChoiceAdmin
from ..models import MultipleChoice, Option
from ..serializers import MultipleChoiceSerializer
from ..services import MultipleChoiceService


class MockRequest(object):
    def __init__(self, user=None):
        self.user = user


class MultipleChoiceForm(forms.ModelForm):
    class Meta:
        model = MultipleChoice
        fields = ("text",)


class OptionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoice
        fields = ("text",)


class MultipleChoiceAdminTestCase(TestCase):
    fixtures = ['users', 'multiple_choices']

    def setUp(self):
        User = get_user_model()
        user = User.objects.first()
        self.admin = MultipleChoiceAdmin(model=MultipleChoice, admin_site=AdminSite())
        self.request = MockRequest(user)

    def test_to_representation(self):
        mc = MultipleChoiceService.get_by_id(1)
        serializer = MultipleChoiceSerializer(mc)
        expected_representation = serializer.to_representation(mc)

        representation = self.admin.to_representation(mc)

        self.assertEqual(expected_representation, representation)

    def test_save_model(self):
        mc = MultipleChoiceService.get_by_id(1)
        form = MultipleChoiceForm(instance=mc, data={"text": mc.text})
        self.admin.save_model(self.request, mc, form, False)
        self.assertIsNotNone(self.admin.saved_obj)

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
    )
    def test_save_related(self):
        mc = MultipleChoiceService.get_by_id(1)
        serializer = MultipleChoiceSerializer(mc)
        expected_representation = serializer.to_representation(mc)

        form = MultipleChoiceForm(instance=mc, data={"text": mc.text})
        form.save(commit=False)

        formset = inlineformset_factory(
            MultipleChoice, Option, form=OptionForm, fields=['text']
        )

        self.admin.save_model(self.request, mc, formset, False)
        self.admin.save_related(self.request, form, (formset(),), False)

        representation = MultipleChoiceService.representation_from_cache(mc.id)

        self.assertEqual(expected_representation, representation)
