from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse, reverse_lazy

from . import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.DomainListView.as_view(),
                           name='domains-list'),
                       url(r'^create/$',
                           views.DomainCreateView.as_view(),
                           name='domains-create'),
                       url(r'^(?P<pk>\d)/$',
                           views.DomainUpdateView.as_view(),
                           name='domains-detail'),
                       url(r'^(?P<pk>\d)/remove/$',
                           views.DomainRemoveView.as_view(),
                           name='domains-remove'),
                       )
