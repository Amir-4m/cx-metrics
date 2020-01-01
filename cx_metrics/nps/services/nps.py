#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import transaction
from django.db.models import F

from cx_metrics.multiple_choices.services.multiple_choice import OptionResponseService
from ..models import NPSSurvey, NPSResponse


class NPSService(object):
    PROMOTERS = 'promoters'
    PASSIVE = 'passives'
    DETRACTORS = 'detractors'

    @staticmethod
    def create_nps_survey(name, business, text, question, message, text_enabled=True):
        return NPSSurvey.objects.create(
            name=name,
            business=business,
            text=text,
            question=question,
            message=message,
            text_enabled=text_enabled,
        )

    @staticmethod
    def get_nps_survey(*args, **kwargs):
        try:
            return NPSSurvey.objects.get(*args, **kwargs)
        except NPSSurvey.DoesNotExist:
            return None

    @staticmethod
    def get_nps_survey_by_id(id_):
        return NPSService.get_nps_survey(id=id_)

    @staticmethod
    def get_nps_survey_by_uuid(uuid_):
        return NPSService.get_nps_survey(uuid=uuid_)

    @staticmethod
    def get_nps_surveys_by_business(business, ordering=None):
        nps_surveys = NPSSurvey.objects.filter(business=business)
        if ordering is not None:
            nps_surveys = nps_surveys.order_by(*ordering)
        return nps_surveys

    @staticmethod
    def change_overall_score(survey_uuid, field_name, amount):
        kwargs = {field_name: F(field_name) + amount}
        return NPSSurvey.objects.filter(uuid=survey_uuid).update(**kwargs)

    @staticmethod
    def respond(survey, customer_uuid, score, option_ids=None):
        field_name = NPSService.PROMOTERS
        if score <= 6:
            field_name = NPSService.DETRACTORS
        elif score <= 8:
            field_name = NPSService.PASSIVE

        with transaction.atomic():
            rows = NPSService.change_overall_score(survey.uuid, field_name, 1)
            if rows > 0:
                nps_response = NPSResponse.objects.create(
                    survey_uuid=survey.uuid,
                    customer_uuid=customer_uuid,
                    score=score
                )

                if option_ids:
                    OptionResponseService.store_option_response(survey.contra, customer_uuid, option_ids)
                return nps_response
            return None

    @staticmethod
    def get_last_response(customer):
        return NPSResponse.objects.filter(customer_uuid=customer.uuid).order_by('-created').first()
