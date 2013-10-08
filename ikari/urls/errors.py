from django.conf.urls.defaults import *

from .. import response
from .. import views
from ..conf import settings


urlpatterns = patterns('',
                       url(r'^/$',
                           views.DomainErrorView.as_view(
                               response_class=response.TemplateErrorResponseBadRequest,
                               template_name=settings.IKARI_ERROR_TEMPLATENAME),
                           settings.IKARI_ERRORCONTEXT_UNKNOWN,
                           name=settings.IKARI_URL_ERROR_UNKNOWN),
                       url(r'^inactive/$',
                           views.DomainErrorView.as_view(
                               response_class=response.TemplateErrorResponseBadRequest,
                               template_name=settings.IKARI_ERROR_TEMPLATENAME),
                           settings.IKARI_ERRORCONTEXT_INACTIVE,
                           name=settings.IKARI_URL_ERROR_INACTIVE),
                       url(r'^missing/$',
                           views.DomainErrorView.as_view(
                               response_class=response.TemplateErrorResponseNotFound,
                               template_name=settings.IKARI_ERROR_TEMPLATENAME),
                           settings.IKARI_ERRORCONTEXT_INVALID,
                           name=settings.IKARI_URL_ERROR_DOESNTEXIST),
                       url(r'^private/$',
                           views.DomainErrorView.as_view(
                               response_class=response.TemplateErrorResponseForbidden,
                               template_name=settings.IKARI_ERROR_TEMPLATENAME),
                           settings.IKARI_ERRORCONTEXT_PRIVATE,
                           name=settings.IKARI_URL_ERROR_PRIVATE),
                       )
