from django.conf import settings
_ = lambda x: x


PORT_SUFFIX = ''
PORT = getattr(settings, 'IKARI_PORT', None)
if PORT:
    PORT_SUFFIX = ':{}'.format(PORT)

ACCOUNT_URLCONF = getattr(settings, 'IKARI_ACCOUNT_URLCONF', None)
USERSITE_URLCONF = getattr(settings, 'IKARI_USERSITE_URLCONF', None)
DEFAULT_DOMAIN = getattr(settings, 'IKARI_DEFAULT_DOMAIN', None)
DEFAULT_URL = getattr(settings, 'IKARI_DEFAULT_URL',
                      'http://{domain}{port}/'.format(
                          domain=DEFAULT_DOMAIN,
                          port=PORT_SUFFIX))

CANONICAL_DOMAINS = getattr(settings, 'IKARI_CANONICAL_DOMAINS', True)

SUBDOMAIN_ROOT = getattr(settings, 'IKARI_ROOT_DOMAIN', None)
assert SUBDOMAIN_ROOT != None, _("You must create IKARI_ROOT_DOMAIN in your settings")
if not SUBDOMAIN_ROOT.startswith('.'):
    SUBDOMAIN_ROOT = '.' + SUBDOMAIN_ROOT
SUBDOMAIN_STOPWORDS = getattr(settings, 'IKARI_SUBDOMAIN_STOPWORDS', ('www',))

try:
    import sso
except ImportError:
    USE_SSO = False
else:
    USE_SSO = getattr(settings, 'IKARI_USE_SSO', True)

ANCHORED_MODEL = getattr(settings, 'IKARI_ANCHORED_OBJECT', u'auth.User')
#if ANCHORED_MODEL is not an instance of "auth.User" then you need to supply the attr of
# ANCHORED_MODEL that points us to an instance of 'auth.User'. it can be a callable.
ANCHORED_MODEL_OWNER_ATTR = getattr(settings, 'IKARI_ANCHORED_OBJECT_OWNER_ATTR', u'owner')

CACHE_KEY_PREFIX = getattr(settings, 'IKARI_CACHE_PREFIX', u'ikari:')
CACHE_KEY_ALL = getattr(settings,'IKARI_CACHE_KEY_ALL', u'domain:all')
CACHE_KEY_ITEM = getattr(settings, 'IKARI_CACHE_KEY_ITEM', u'domain:{}')

ERRORMSG_UNAVAILABLE = getattr(settings,  "IKARI_ERRORMSG_UNAVAILABLE",   _('This hostname is unavailable.'))
ERRORMSG_INVALIDCHARS = getattr(settings, "IKARI_ERRORMSG_INVALIDCHARS",  _('Invalid characters in hostname.  You may only use a-z, 0-9, and "-".'))
ERRORMSG_PROTECTEDTLD = getattr(settings, "IKARI_ERRORMSG_PROTECTEDTLD",  _('Hostnames cannot be a subdomain of {}.'.format(SUBDOMAIN_ROOT)))
ERRORMSG_NOPERMISSION = getattr(settings, "IKARI_ERRORMSG_NOPERMISSION",  _('Insufficient permissions.'))

ERRORCONTEXT_INACTIVE = {'title': _("Domain Inactive"), 'message': _("Looks like you're trying to access a domain that's inactive")}
ERRORCONTEXT_INVALID = {'title': _("Domain Invalid"), 'message': _("No such domain registered here")}
ERRORCONTEXT_PRIVATE = {'title': _("Domain Private"), 'message': _("This domain is private. The owner hasn't made it public yet.")}