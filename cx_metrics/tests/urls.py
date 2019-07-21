#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('auth/', include('upkook_core.auth.urls', 'auth')),
    path('surveys/defaults/', include('cx_metrics.surveys_defaults.urls.api', 'survey-defaults')),
    path('cx/surveys/', include('cx_metrics.surveys.urls.api', 'cx-surveys')),
    path('cx/surveys/nps/', include('cx_metrics.nps.urls.api', 'cx-nps')),
    path('cx/surveys/csat/', include('cx_metrics.csat.urls.api', 'cx-csat')),
    path('', admin.site.urls),
]
