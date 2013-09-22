import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.cache import patch_vary_headers
from django.contrib.auth import logout
from django.db.models.query import Q

from .conf import settings, null_handler
from .loader import get_model
from . import models
from . import signals
from . import cache


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)
IkariSiteModel = get_model(*settings.IKARI_SITE_MODEL.split("."))


class DomainsMiddleware:

    def process_request(self, request):
        host = request.META.get('HTTP_HOST', None)
        if host is None:
            return

        # strip port suffix if present
        if ":" in host:
            host = host[:host.index(":")]

        try:
            site = cache.get_thing(facet='item', query=host,
                    update=lambda: IkariSiteModel.objects.get(fqdn=host))

        except IkariSiteModel.DoesNotExist:
            # if it's not the MASTER_DOMAIN
            if host != settings.IKARI_MASTER_DOMAIN:
                # redirect to error page
                return HttpResponseRedirect(settings.IKARI_URL_ERROR_DOESNTEXIST)

        else:
            # set up request parameters
            request.domain = domain
            request.urlconf = settings.IKARI_SITE_URLCONF

            user = request.user
            can_access = site.user_can_access(user)

            # if it's not active, then only allow staff through
            if not domain.is_active and not can_access:
                return HttpResponseRedirect(settings.IKARI_URL_ERROR_INACTIVE)

            # if it's not published, then only allow site owner and members through
            if not domain.is_public and not can_access:
                return HttpResponseRedirect(settings.IKARI_URL_ERROR_PRIVATE)

            # other wise, call the 'site_request' signal to allow project level integrated
            # checks to be performed. requires a HttpResponse type to successfully continue.
            for receiver, return_value in signals.site_request.send(sender=DomainsMiddleware, request=request, site=site):
                if isinstance(return_value, HttpResponse):
                    return return_value
                else:
                    return HttpResponseRedirect(settings.IKARI_URL_ERROR_UNKNOWN)


    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
