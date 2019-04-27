#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from mock import patch
from django.test import TestCase

from upkook_core.businesses.services import BusinessService
from ..models import Survey
from ..factory import SurveyFactory
from ..decorators import register_survey
from .models import TestSurvey


class SurveyTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses']

    def setUp(self):
        self.business = BusinessService.get_business_by_id(1)

    def test_str(self):
        survey = Survey(name=self.id())
        self.assertEqual(str(survey), self.id())

    @patch.object(SurveyFactory, 'register')
    def test_register_survey(self, mock_register):
        wrapper = register_survey(self.id())
        wrapper(TestSurvey)
        mock_register.assert_called_with(self.id(), TestSurvey)

    def test_register_survey_value_error(self):
        wrapper = register_survey(self.id())
        self.assertRaisesMessage(
            ValueError,
            'Wrapped model must be subclass of SurveyModel',
            wrapper,
            SurveyTestCase,
        )

    def test_save_new(self):
        ts = TestSurvey.objects.create(name='test_save_new', business=self.business, enabled=False)
        self.assertFalse(ts.enabled)
        self.assertIsInstance(ts.survey, Survey)
        self.assertEqual(ts.survey.type, ts.type)
        self.assertEqual(ts.name, 'test_save_new')
        self.assertEqual(ts.name, ts.survey.name)
        self.assertEqual(ts.business.pk, self.business.pk)
        self.assertEqual(ts.business.pk, ts.survey.business.pk)

    def test_save_changes(self):
        ts = TestSurvey.objects.create(name='test_save_changes', business=self.business)
        ts.name = 'Hello'
        ts.save()
        self.assertEqual(ts.name, 'Hello')
        self.assertEqual(ts.name, ts.survey.name)

    def test_delete(self):
        ts = TestSurvey.objects.create(name='test_delete', business=self.business)
        ts.delete()
        self.assertFalse(TestSurvey.objects.filter(name='test_delete').exists())
        self.assertFalse(Survey.objects.filter(name='test_delete').exists())

    def test_queryset_delete(self):
        ts = TestSurvey.objects.create(name='test_queryset_delete', business=self.business)
        TestSurvey.objects.filter(id=ts.pk).delete()
        self.assertFalse(TestSurvey.objects.filter(name='test_queryset_delete').exists())
        self.assertFalse(Survey.objects.filter(name='test_queryset_delete').exists())

    def test_queryset_update(self):
        ts = TestSurvey.objects.create(name='test_queryset_update', business=self.business)
        TestSurvey.objects.filter(id=ts.pk).update(name='Hello World!')
        ts.refresh_from_db()
        self.assertEqual(ts.name, 'Hello World!')
        self.assertEqual(ts.name, ts.survey.name)

    def test_queryset_update_enabled(self):
        ts = TestSurvey.objects.create(name='test_queryset_update_enabled', business=self.business)
        TestSurvey.objects.filter(id=ts.pk).update(enabled=False)
        ts.refresh_from_db()
        self.assertFalse(ts.enabled)
        self.assertEqual(ts.name, 'test_queryset_update_enabled')
        self.assertEqual(ts.name, ts.survey.name)
