from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _

from .. import views


urlpatterns = patterns('',
    url(r'^inactive/$',
        views.DomainErrorView.as_view(message=_("This site is inactive.")),
        name="ikari-inactive"),

    url(r'^does-not-exist/$',
        views.DomainErrorView.as_view(message=_("No site matches this domain.")),
        name="ikari-does-not-exist"),

    url(r'^not-public/$',
        views.DomainErrorView.as_view(message=_("This site is private.")),
        name="ikari-not-public"),
)