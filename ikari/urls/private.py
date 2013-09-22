from django.conf.urls.defaults import *

from .. import views


urlpatterns = patterns('',
    url(r'^config/$', views.SiteUpdateView.as_view(), name="ikari-config"),
)