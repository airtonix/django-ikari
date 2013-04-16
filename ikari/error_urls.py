from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse, reverse_lazy

from . import views
from . import settings

urlpatterns = patterns('',
                       url(r'^error/domain/inactive/$',
                           views.DomainErrorView.as_view(), settings.ERRORCONTEXT_INACTIVE,
                           name='domains-inactive'),

                       url(r'^error/domain/invalid/$',
                           views.DomainErrorView.as_view(), settings.ERRORCONTEXT_INVALID,
                           name='domains-unavailable'),

                       url(r'^error/domain/private/$',
                           views.DomainErrorView.as_view(), settings.ERRORCONTEXT_PRIVATE,
                           name='domains-not-public'),
)
