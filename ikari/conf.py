import logging
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core import exceptions

from appconf import AppConf
from .loader import load_class, get_model


MESSAGES = {
    "MissingSettings" : "django-ikari: critial settings attribute missing : IKARI_{}",
    "FailedImportTest": "Could not test import of {}",
}


class IkariAppConf(AppConf):
    ACCOUNT_URLCONF = 'ikari.urls.private'
    SITE_URLCONF = 'ikari.urls.sites'

    # This needs to point at the domain
    # of your main project, typically
    # the place where you'd have forms that
    # process payments, login users, process
    # beta invites etc.
    MASTER_DOMAIN = None

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

    # See ikari.backends.domain_verification for a list of
    # existing backends
    DOMAIN_VERIFICATION_BACKEND = 'ikari.backends.domain_verification.FQDNVerificationBackend'
    USE_SSO = False

    CACHE_KEY_PREFIX = u'ikari:'
    CACHE_KEY_ALL = u'domain:all'
    CACHE_KEY_ITEM = u'domain:{}'

    # you can customise how this relates to your
    # project by subclassing from ikari.models.BaseSite
    # and pointing this at your new Site model.
    SITE_MODEL = 'ikari.Site'

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

    def configure_use_sso(self, value):
        try:
            import sso
            return True

        except Exception as error:
            return False

    def configure_site_model(self, value):
        if not value:
            raise exceptions.ImproperlyConfigured(
                MESSAGES.get('MissingSettings').format("SITE_MODEL"))
        try:
            app_name, model_name = value.split(".")
            klass = get_model(app_name, model_name)
        except Exception as error:
            raise exceptions.ImproperlyConfigured(
                MESSAGES.get("FailedImportTest").format(value))
        return value

    def configure_port_suffix(self, value):
        if not value and hasattr(settings, 'IKARI_PORT'):
            return u':{}'.format(settings.IKARI_PORT)
        return value

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


#
# Old Configuration
#
# PORT_SUFFIX = ''
# PORT = getattr(settings, 'IKARI_PORT', None)
# if PORT:
#     PORT_SUFFIX = ':{}'.format(PORT)

# ACCOUNT_URLCONF = getattr(settings, 'IKARI_ACCOUNT_URLCONF', None)
# USERSITE_URLCONF = getattr(settings, 'IKARI_USERSITE_URLCONF', None)
# DEFAULT_DOMAIN = getattr(settings, 'IKARI_DEFAULT_DOMAIN', None)
# DEFAULT_URL = getattr(settings, 'IKARI_DEFAULT_URL',
#                       'http://{domain}{port}/'.format(
#                           domain=DEFAULT_DOMAIN,
#                           port=PORT_SUFFIX))

# CANONICAL_DOMAINS = getattr(settings, 'IKARI_CANONICAL_DOMAINS', True)

# SUBDOMAIN_ROOT = getattr(settings, 'IKARI_ROOT_DOMAIN', None)
# assert SUBDOMAIN_ROOT is not None, _("You must create IKARI_ROOT_DOMAIN in your settings")
# if not SUBDOMAIN_ROOT.startswith('.'):
#     SUBDOMAIN_ROOT = '.' + SUBDOMAIN_ROOT
# SUBDOMAIN_STOPWORDS = getattr(settings, 'IKARI_SUBDOMAIN_STOPWORDS',
# ('www',))

# try:
#     import sso
# except ImportError:
#     USE_SSO = False
# else:
#     USE_SSO = getattr(settings, 'IKARI_USE_SSO', True)

# ANCHORED_MODEL = getattr(settings, 'IKARI_ANCHORED_OBJECT', u'auth.User')
# if ANCHORED_MODEL is not an instance of "auth.User" then you need to supply the attr of
# ANCHORED_MODEL that points us to an instance of 'auth.User'. it can be a callable.
# ANCHORED_MODEL_OWNER_ATTR = getattr(settings, 'IKARI_ANCHORED_OBJECT_OWNER_ATTR', u'owner')
# ANCHORED_MODEL_MEMBER_ATTR = getattr(settings,
# 'IKARI_ANCHORED_OBJECT_MEMBER_ATTR', u'members')

# CACHE_KEY_PREFIX = getattr(settings, 'IKARI_CACHE_PREFIX', u'ikari:')
# CACHE_KEY_ALL = getattr(settings, 'IKARI_CACHE_KEY_ALL', u'domain:all')
# CACHE_KEY_ITEM = getattr(settings, 'IKARI_CACHE_KEY_ITEM', u'domain:{}')

# ERRORMSG_UNAVAILABLE = getattr(settings,  "IKARI_ERRORMSG_UNAVAILABLE",   _('This hostname is unavailable.'))
# ERRORMSG_INVALIDCHARS = getattr(settings, "IKARI_ERRORMSG_INVALIDCHARS",  _('Invalid characters in hostname.  You may only use a-z, 0-9, and "-".'))
# ERRORMSG_PROTECTEDTLD = getattr(settings, "IKARI_ERRORMSG_PROTECTEDTLD",  _('Hostnames cannot be a subdomain of {}.'.format(SUBDOMAIN_ROOT)))
# ERRORMSG_NOPERMISSION = getattr(settings, "IKARI_ERRORMSG_NOPERMISSION",
# _('Insufficient permissions.'))

# ERRORCONTEXT_INACTIVE = {'title': _("Domain Inactive"), 'message': _("Looks like you're trying to access a domain that's inactive")}
# ERRORCONTEXT_INVALID = {'title': _("Domain Invalid"), 'message': _("No such domain registered here")}
# ERRORCONTEXT_PRIVATE = {'title': _("Domain Private"), 'message': _("This
# domain is private. The owner hasn't made it public yet.")}


class NullHandler(logging.Handler):

    def emit(self, record):
        pass

null_handler = NullHandler()
