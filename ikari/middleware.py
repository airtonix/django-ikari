import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.cache import patch_vary_headers
from django.utils.encoding import iri_to_uri
from django.contrib.auth import logout
from django.db.models.query import Q

from .conf import settings, null_handler
from .loader import get_model
from . import models
from . import signals
from . import cache
from . import exceptions


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)
IkariSiteModel = get_model(*settings.IKARI_SITE_MODEL.split("."))


class DomainsMiddleware:

    def redirect_to_error(self, request, urlname):
        self.urlconf = settings.ROOT_URLCONF
        path = reverse(urlname)
        current_uri = '%s://%s%s' % ('https' if request.is_secure() else 'http',
                                     settings.IKARI_MASTER_DOMAIN, path)

        return HttpResponseRedirect(iri_to_uri(current_uri))

    def process_request(self, request):
        host = request.get_host()
        user = getattr(request, 'user', None)

        # strip port suffix if present
        if ":" in host:
            host = host[:host.index(":")]

        # if it's the MASTER_DOMAIN, or there isn't a host set then bail out now.
        if host is None or host is settings.IKARI_MASTER_DOMAIN:
            return

        try:
            site = cache.get_thing(facet='item', query=host,
                                   update=lambda: IkariSiteModel.objects.get(fqdn=host))
            site.user_can_access(user)

        except IkariSiteModel.DoesNotExist:
            return self.redirect_to_error(request, settings.IKARI_URL_ERROR_DOESNTEXIST)

        except exceptions.SiteErrorInactive:
            # if it's not active, then only allow staff through
            return self.redirect_to_error(request, settings.IKARI_URL_ERROR_INACTIVE)

        except exceptions.SiteErrorIsPrivate:
            # if it's not published, then only allow site owner and members
            # through
            return self.redirect_to_error(request, settings.IKARI_URL_ERROR_PRIVATE)

        else:
            # other wise, call the 'site_request' signal to allow project level integrated
            # checks to be performed. requires a HttpResponse type to
            # successfully continue.
            for receiver, return_value in signals.site_request.send(sender=DomainsMiddleware, request=request, site=site):
                if isinstance(return_value, HttpResponse):
                    return return_value
                else:
                    return self.redirect_to_error(request, settings.IKARI_URL_ERROR_UNKNOWN)

            request.site = site
            request.urlconf = settings.IKARI_SITE_URLCONF

    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
