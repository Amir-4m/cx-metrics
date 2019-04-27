#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from .models import SurveyModel
from .factory import survey_factory


def register_survey(survey_type):
    def _survey_model_wrapper(survey_model):
        if not issubclass(survey_model, SurveyModel):
            raise ValueError('Wrapped model must be subclass of SurveyModel')

        survey_factory.register(survey_type, survey_model)

        return survey_model

    return _survey_model_wrapper
