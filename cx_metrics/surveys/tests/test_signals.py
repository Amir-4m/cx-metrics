#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from mock import patch
from django.test import TestCase
from django.db.models.signals import post_save

from upkook_core.businesses.services import BusinessService
from upkook_core.industries.services import IndustryService

from ..signals import manage_signal_receivers
from ..services import SurveyCacheService
from .models import TestSurvey


class SignalsTestCase(TestCase):
    def setUp(self):
        super(SignalsTestCase, self).setUp()
        industry = IndustryService.create_industry(name='Industry', icon='')
        business = BusinessService.create_business(
            size=5,
            name='Business',
            domain='www.business.com',
            industry=industry,
        )
        self.instance = TestSurvey.objects.create(name='test', business=business)
        manage_signal_receivers(TestSurvey, connect=True)

    def tearDown(self):
        super(SignalsTestCase, self).tearDown()
        manage_signal_receivers(TestSurvey, connect=False)

    def test_clear_cache_on_change_not_raw(self):
        kwargs = dict(
            instance=self.instance,
            created=True, raw=True,
            update_fields=[], using=None
        )
        post_save.send(TestSurvey, **kwargs)

    @patch.object(SurveyCacheService, 'delete')
    def test_clear_cache_on_change(self, mock_cache_delete):
        kwargs = dict(
            instance=self.instance,
            created=False, raw=False,
            update_fields=[], using=None
        )
        post_save.send(TestSurvey, **kwargs)
        mock_cache_delete.assert_called_once_with(self.instance.uuid)
