#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db.models.signals import post_save, post_delete
from .models import SurveyModel
from .services import SurveyCacheService


def clear_cache_on_change(sender, instance, created=False, raw=False, **kwargs):
    if not raw and issubclass(sender, SurveyModel) and not created:
        SurveyCacheService.delete(instance.uuid)


def manage_signal_receivers(sender, connect=True):
    for name, signal in {'post_save': post_save, 'post_delete': post_delete}.items():
        dispatch_uid = 'surveys_%s_%s_clear_cache_on_change' % (
            sender.__name__.lower(), name
        )
        if connect:
            signal.connect(clear_cache_on_change, sender, dispatch_uid=dispatch_uid)
        else:
            signal.disconnect(clear_cache_on_change, sender, dispatch_uid=dispatch_uid)
