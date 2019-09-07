#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import override_settings, TestCase
from django.core.cache import cache

from ..services.cache import SurveyCacheService


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class SurveyCacheServiceTestCase(TestCase):
    def test_set(self):
        data = {'name': self.id()}
        SurveyCacheService.set(self.id(), data)
        self.assertEqual(cache.get('survey-%s' % self.id()), data)

    def test_get(self):
        data = {'name': self.id()}
        SurveyCacheService.set(self.id(), data)
        self.assertEqual(SurveyCacheService.get(self.id()), data)

    def test_delete(self):
        data = {'name': self.id()}
        SurveyCacheService.set(self.id(), data)
        SurveyCacheService.delete(self.id())
        self.assertIsNone(SurveyCacheService.get(self.id()))
