#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from uuid import uuid4
from django.conf import settings
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from upkook_core.businesses.models import Business


class SurveyBase(models.Model):
    uuid = models.UUIDField(_('UUID'), unique=True, default=uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=256)
    business = models.ForeignKey(
        Business,
        related_name='%(class)ss',
        related_query_name='%(class)ss',
        on_delete=models.PROTECT,
        verbose_name=_('Business')
    )
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @cached_property
    def url(self):
        return '%s%s/' % (settings.SURVEY_PUBLIC_BASE_URL, self.uuid)


class Survey(SurveyBase):
    type = models.CharField(_('Type'), max_length=50)

    class Meta:
        abstract = False
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')


class SurveyModelQuerySet(QuerySet):
    def bulk_create(self, objs, batch_size=None):
        raise NotImplementedError

    @transaction.atomic
    def delete(self):
        sids = list(self.values_list('survey', flat=True))
        super(SurveyModelQuerySet, self).delete()
        Survey.objects.filter(id__in=sids).delete()

    @transaction.atomic
    def update(self, **kwargs):
        sids = list(self.values_list('survey', flat=True))
        rows = super(SurveyModelQuerySet, self).update(**kwargs)

        survey_kwargs = {}
        for field_name in ['name', 'business']:
            if field_name in kwargs:
                survey_kwargs.update({field_name: kwargs.get(field_name)})

        if survey_kwargs:
            Survey.objects.filter(id__in=sids).update(**survey_kwargs)

        return rows


class SurveyModel(SurveyBase):
    survey = models.OneToOneField(
        Survey, verbose_name=_('Survey'),
        related_name='%(class)s',
        related_query_name='%(class)s',
        on_delete=models.CASCADE,
    )

    objects = SurveyModelQuerySet.as_manager()

    class Meta:
        abstract = True

    @cached_property
    def type(self):
        raise NotImplementedError

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with transaction.atomic(using):
            try:
                self.survey.name = self.name
                self.survey.business = self.business
                self.survey.save(force_insert, force_update, using)

            except Survey.DoesNotExist:
                self.uuid = uuid4()
                survey = Survey(type=self.type, uuid=self.uuid, name=self.name, business=self.business)
                survey.save(force_insert, force_update, using)
                self.survey = survey

            super(SurveyModel, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        with transaction.atomic(using):
            super(SurveyModel, self).delete(using, keep_parents)
            self.survey.delete(using, keep_parents)


class SurveyResponseBase(models.Model):
    survey_uuid = models.UUIDField(_('Survey UUID'), editable=False)
    customer_uuid = models.UUIDField(_('Customer UUID'), editable=False)
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
