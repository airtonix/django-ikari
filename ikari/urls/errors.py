from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse


from .. import views
from ..conf import settings


class TemplateErrorResponseNotFound(TemplateResponse):
    status_code = 404


class TemplateErrorResponseForbidden(TemplateResponse):
    status_code = 403


class TemplateErrorResponseBadRequest(TemplateResponse):
    status_code = 400


urlpatterns = patterns('',
                       url(r'^/$',
                           views.DomainErrorView.as_view(
                               response_class=TemplateErrorResponseBadRequest),
                           settings.IKARI_ERRORCONTEXT_UNKNOWN,
                           name=settings.IKARI_URL_ERROR_UNKNOWN),
                       url(r'^inactive/$',
                           views.DomainErrorView.as_view(
                               response_class=TemplateErrorResponseBadRequest),
                           settings.IKARI_ERRORCONTEXT_INACTIVE,
                           name=settings.IKARI_URL_ERROR_INACTIVE),
                       url(r'^missing/$',
                           views.DomainErrorView.as_view(
                               response_class=TemplateErrorResponseNotFound),
                           settings.IKARI_ERRORCONTEXT_INVALID,
                           name=settings.IKARI_URL_ERROR_DOESNTEXIST),
                       url(r'^private/$',
                           views.DomainErrorView.as_view(
                               response_class=TemplateErrorResponseForbidden),
                           settings.IKARI_ERRORCONTEXT_PRIVATE,
                           name=settings.IKARI_URL_ERROR_PRIVATE),
                       )
