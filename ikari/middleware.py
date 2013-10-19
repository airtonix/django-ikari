import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.cache import patch_vary_headers
from django.utils.encoding import iri_to_uri

from .conf import settings
from .utils import null_handler
from . import signals
from . import models


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class DomainsMiddleware:

    def redirect_to_error(self, request, urlname):
        self.urlconf = settings.ROOT_URLCONF
        path = reverse(urlname)
        port_str = ''

        if not settings.IKARI_STRICT_DOMAINS:
            return

        if hasattr(request, 'port'):
            port_str = ":{port}".format(port=request.port)

        current_uri = '{protocol}://{domain}{port}{path}'.format(
            protocol='https' if request.is_secure() else 'http',
            domain=settings.IKARI_MASTER_DOMAIN,
            path=path,
            port=port_str)

        return HttpResponseRedirect(iri_to_uri(current_uri))

    def process_request(self, request):
        host = request.get_host()
        user = getattr(request, 'user', None)
        # strip port suffix if present

        if ":" in host:
            host, port = host.split(":")
            request.port = port

        request.host = host

        # if it's the MASTER_DOMAIN, or there isn't a host set then bail out
        # now.

        if not host or host != settings.IKARI_MASTER_DOMAIN:
            request.urlconf = settings.IKARI_SITE_URLCONF

            try:
                site = models.Site.objects.get(fqdn__iexact=host)
                request.ikari_site = site

            except models.Site.DoesNotExist:
                return self.redirect_to_error(request, settings.IKARI_URL_ERROR_DOESNTEXIST)

            is_valid_user = user and user.is_authenticated and user.is_active
            is_admin = user and is_valid_user and (
                user.is_superuser or user.is_staff)
            is_manager = is_valid_user and user in (
                site.owner, site.get_moderators())

            if not site.is_active and not is_admin:
                # if it's not active, then only allow staff through
                return self.redirect_to_error(request, settings.IKARI_URL_ERROR_INACTIVE)

            elif not site.is_public and not (is_admin or is_manager):
                # if it's not published, then only allow site managers and
                # admin
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

    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
