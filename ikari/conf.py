import logging
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core import exceptions

from appconf import AppConf
from .loader import get_model, load_class


MESSAGES = {
    "MissingSettings": "django-ikari: critial settings attribute missing : IKARI_{}",
    "FailedImportTest": "Could not test import of {}",
}


class IkariAppConf(AppConf):
    # This needs to point at the domain
    # of your main project, typically
    # the place where you'd have forms that
    # process payments, login users, process
    # beta invites etc.
    MASTER_DOMAIN = None

    # routes which define paths to views to
    # allow users to manag their site(s)
    ACCOUNT_URLCONF = 'ikari.urls.private'

    # routes that are anchored to the root
    # of users sites. this urlconf will replace
    # your ROOT_URLCONF setting when a requested
    # hostname matches an active ( and published
    # if the user is a site member) site.
    SITE_URLCONF = 'ikari.urls.sites'

    # Url to redirect visitors to when they
    # land on a subdomain that isn't linked
    # to a ikari site.
    URL_ERROR_DOESNTEXIST = "ikari-error-doesnotexist"
    URL_ERROR_PRIVATE = "ikari-error-private"
    URL_ERROR_INACTIVE = "ikari-error-inactive"
    URL_ERROR_UNKNOWN = "ikari-error-unknown"

    # Redirect users to errorpage when errors happen?
    REDIRECT_ONERROR = True

    SUBDOMAIN_ROOT = None
    SITE_PERMISSION_GROUPS = (
        ('admin', _("Site Administrator")),
        ('moderator', _("Site Moderator")),
        ('reviewer', _("Site Reviewer")),
    )

    # See ikari.backends.domain_verification for a list of
    # existing backends
    DOMAIN_VERIFICATION_BACKEND = 'ikari.backends.domain_verification.FQDNVerificationBackend'

    CACHE_KEY_PREFIX = u'ikari:'
    CACHE_KEY_ALL = u'domain:all'
    CACHE_KEY_ITEM = u'domain:{}'

    # you can customise how this relates to your
    # project by subclassing from ikari.models.BaseSite
    # and pointing this at your new Site model.
    SITE_MODEL = None

    #
    ERRORMSG_UNAVAILABLE = _('This hostname is unavailable.')
    ERRORMSG_INVALIDCHARS = _(
        'Invalid characters in hostname.  You may only use a-z, 0-9, and "-".')
    ERRORMSG_NOPERMISSION = _('Insufficient permissions.')

    # Context used for error templates
    # not used if you're redirecting users to the
    # DEFAULT_URL
    ERRORCONTEXT_INACTIVE = {'title': _("Domain Inactive"), 'message': _(
        "Looks like you're trying to access a domain that's inactive")}
    ERRORCONTEXT_INVALID = {
        'title': _("Domain Invalid"), 'message': _("No such domain registered here")}
    ERRORCONTEXT_PRIVATE = {'title': _("Domain Private"), 'message': _(
        "This domain is private. The owner hasn't made it public yet.")}
    ERRORCONTEXT_UNKNOWN = {
        'title': _("Oops"), 'message': _("Something weird happened.")}

    def configure_site_urlconf(self, value):
        if not value:
            raise exceptions.ImproperlyConfigured(
                MESSAGES.get('MissingSettings').format("SITE_URLCONF"))
        return value

    # def configure_site_model(self, value):
    #     if not value:
    #         raise exceptions.ImproperlyConfigured(
    #             MESSAGES.get('MissingSettings').format("SITE_MODEL"))
    #     try:
    #         klass = load_class(value)
    #     except ImportError:
    #         raise exceptions.ImproperlyConfigured(
    #             MESSAGES.get("FailedImportTest").format(value))
    #     return value

    def configure_master_domain(self, value):
        if not hasattr(settings, 'IKARI_MASTER_DOMAIN'):
            raise exceptions.ImproperlyConfigured(
                MESSAGES.get('MissingSettings').format("MASTER_DOMAIN"))
        return value

    def configure_subdomain_root(self, value):
        if not value and hasattr(settings, 'IKARI_MASTER_DOMAIN'):
            value = settings.IKARI_MASTER_DOMAIN

        if value and not value.startswith("."):
            value = "." + value

        return value
