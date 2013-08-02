import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.cache import patch_vary_headers
from django.contrib.auth import logout

from . import models
from . import signals
from . import settings
from . import cache


logger = logging.getLogger(__name__)
logger.addHandler(settings.null_handler)


def get_domain_list(facet='domain'):
    return models.Domain.objects.values_list(facet, flat=True)


def get_domain(query_dict=None):
    return models.Domain.objects.get(**query_dict)


class DomainsMiddleware:

    def process_request(self, request):
        host = request.META.get('HTTP_HOST', None)
        if host is None:
            return

        # strip port suffix if present
        if settings.PORT_SUFFIX and host.endswith(settings.PORT_SUFFIX):
            host = host[:-len(settings.PORT_SUFFIX)]

        try:
            if host.endswith(settings.SUBDOMAIN_ROOT):
                query_dict = {"subdomain": host[:-len(settings.SUBDOMAIN_ROOT)]}
            else:
                query_dict = {"domain": host}

            domain = cache.get_thing(facet='item', query=host, update=lambda: get_domain(query_dict))

            if settings.CANONICAL_DOMAINS and domain.domain:
                if str(host) != (domain.domain):
                    return HttpResponseRedirect(domain.get_absolute_url())

        except models.Domain.DoesNotExist:
            if host != settings.DEFAULT_DOMAIN:
                return HttpResponseRedirect(settings.DEFAULT_URL)

        else:
            request.domain = domain
            # set up request parameters

            if settings.ACCOUNT_URLCONF:
                request.urlconf = settings.ACCOUNT_URLCONF

            # force logout of non-member and non-owner from non-public site
            if hasattr(request.user, 'pk') > 0 and request.user.is_authenticated:
                # logger.debug(request.user, "is authenticated")
                can_access = domain.user_can_access(request.user)
                # logger.debug(request.user, "can_access", can_access)
                if not can_access:
                    url = settings.DEFAULT_URL.rstrip("/")
                    if not domain.is_public:
                        url = url + reverse('domains-inactive')
                    logout(request)
                    return HttpResponseRedirect(url)

            # call request hookanchored_domains
            for receiver, retval in signals.domain_request.send(sender=request, request=request, domain=domain):
                if isinstance(retval, HttpResponse):
                    return retval

    def process_response(self, request, response):

        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))

        return response
