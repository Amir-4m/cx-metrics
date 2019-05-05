#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from upkook_core.businesses.services import BusinessService
from ..factory import DefaultSurveyFactory, AlreadyRegistered, NotRegistered, DefaultSurveySerializerFactory
from ..serializers import SurveySerializer
from ..models import SurveyModel
from .models import TestSurvey


class SurveyFactoryTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses']

    def setUp(self):
        self.factory = DefaultSurveyFactory()
        self.business = BusinessService.get_business_by_id(1)

    def test_create(self):
        self.factory.register(self.id(), TestSurvey)

        survey = self.factory.create(self.id(), name=self.id(), business=self.business, enabled=False)

        self.assertIsInstance(survey, TestSurvey)
        self.assertEqual(survey.name, self.id())
        self.assertEqual(survey.business, self.business)
        self.assertFalse(survey.enabled)

    def test_register_abstract_model(self):
        self.assertRaisesMessage(
            ImproperlyConfigured,
            'The survey model SurveyModel is abstract, so it cannot be registered with survey factory.',
            self.factory.register, self.id(), SurveyModel,
        )

    def test_register_already_registered(self):
        self.factory.register(self.id(), TestSurvey)
        self.assertRaisesMessage(
            AlreadyRegistered,
            'The survey type %s is already registered' % self.id(),
            self.factory.register,
            self.id(),
            TestSurvey
        )

    def test_create_not_registered(self):
        self.assertRaisesMessage(
            NotRegistered,
            'The survey type %s is not registered' % self.id(),
            self.factory.create,
            self.id(),

        )


class SurveySerializerFactoryTestCase(TestCase):
    fixtures = ['users', 'industries', 'businesses']

    def setUp(self):
        self.factory = DefaultSurveySerializerFactory()
        self.business = BusinessService.get_business_by_id(1)

    def test_register_already_registered(self):
        self.factory.register(self.id(), SurveySerializer)
        self.assertRaisesMessage(
            AlreadyRegistered,
            'The survey type %s is already registered' % self.id(),
            self.factory.register,
            self.id(),
            SurveySerializer
        )

    def test_get_serializer_class(self):
        self.factory.register(self.id(), SurveySerializer)
        self.assertEqual(self.factory.get_serializer_class(self.id()), SurveySerializer)
