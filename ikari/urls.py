from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse, reverse_lazy

from . import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.DomainUpdateView.as_view(),
                           name='domains-details'),

                       url(r'^$',
                           views.DomainErrorView.as_view(error='not-available'),
                           name='domains-unavailable'),

                       url(r'^$',
                           views.DomainErrorView.as_view(error='not-public'),
                           name='domains-not-public'),
                       )
