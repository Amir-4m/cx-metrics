#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from rest_framework.serializers import Serializer
from .models import SurveyModel
from .factory import survey_factory, survey_serializer_factory


def register_survey(survey_type):
    def _survey_model_wrapper(survey_model):
        if not issubclass(survey_model, SurveyModel):
            raise ValueError('Wrapped model must be subclass of SurveyModel')

        survey_factory.register(survey_type, survey_model)

        return survey_model

    return _survey_model_wrapper


def register_survey_serializer(survey_type):
    def _survey_serializer_wrapper(serializer_class):
        if not issubclass(serializer_class, Serializer):
            raise ValueError('Wrapped serializer must be subclass of Serializer')

        survey_serializer_factory.register(survey_type, serializer_class)
        return serializer_class

    return _survey_serializer_wrapper
