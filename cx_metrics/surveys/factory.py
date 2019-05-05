#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject

from .serializers import SurveySerializer


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class SurveyFactory:
    """
    A SurveyFactory object encapsulates dynamic instantiation of survey classes.
    Surveys are registered with SurveyFactory using the register() method
    """

    def __init__(self):
        self._registry = {}  # survey_model type -> survey_model class

    def register(self, survey_type, survey_model):
        """
        Register the given survey model class with given survey type

        Args:
            survey_type (str): A survey model type
            survey_model: A survey model class, not instances.

        Raises
            AlreadyRegistered: If a survey type is already registered
            ImproperlyConfigured: If a survey model is abstract
        """
        if survey_model._meta.abstract:
            raise ImproperlyConfigured(
                'The survey model %s is abstract, '
                'so it cannot be registered with survey factory.' % survey_model.__name__
            )

        if survey_type in self._registry:
            raise AlreadyRegistered('The survey type %s is already registered' % survey_type)

        self._registry[survey_type] = survey_model

    def create(self, survey_type, **kwargs):
        if survey_type not in self._registry:
            raise NotRegistered('The survey type %s is not registered' % survey_type)

        return self._registry[survey_type](**kwargs)


class DefaultSurveyFactory(LazyObject):
    def _setup(self):
        self._wrapped = SurveyFactory()


survey_factory = DefaultSurveyFactory()


class SurveySerializerFactory:
    """
    A Survey Serializer Factory object encapsulates dynamic instantiation of survey serializer.
    Survey serializers are registered with SurveySerializerFactory using the register() method.
    """

    def __init__(self):
        self._registry = {}  # survey_model type -> survey serializer class

    def register(self, survey_type, serializer_class):
        """
        Register the given survey serializer class with given survey type

        Args:
            survey_type (str): A survey model type
            serializer_class: A survey serializer class, not instances.
        """
        if survey_type in self._registry:
            raise AlreadyRegistered('The survey type %s is already registered' % survey_type)

        self._registry[survey_type] = serializer_class

    def get_serializer_class(self, survey_type):
        return self._registry.get(survey_type, SurveySerializer)


class DefaultSurveySerializerFactory(LazyObject):
    def _setup(self):
        self._wrapped = SurveySerializerFactory()


survey_serializer_factory = DefaultSurveySerializerFactory()
