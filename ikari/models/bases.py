from uuid import uuid4
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from uuidfield import UUIDField
from ..conf import settings
from ..utils import null_handler
from ..loader import load_class, get_model_string


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)
VerficationBackend = load_class(settings.IKARI_DOMAIN_VERIFICATION_BACKEND)

USER_MODEL_STRING = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
SITE_MODEL_STRING = get_model_string("Site")


class BaseSite(models.Model):

    uuid = UUIDField()
    name = models.CharField(verbose_name=_("Site Name"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))

    fqdn = models.CharField(verbose_name=_('Domain Name'),
                            help_text=_("Either a) Fully qualified domain name <a href='http://en.wikipedia.org/wiki/Fully_qualified_domain_name'>help</a>, or b) a slugified word as a subdomain of {master_domain}, or c) blank which will use the slugified name.".format(
                                master_domain=settings.IKARI_MASTER_DOMAIN)),
                            blank=True, null=True, max_length=255, unique=True)

    is_public = models.BooleanField(verbose_name=_('Is public'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=False)
    is_primary = models.BooleanField(
        verbose_name=_('Is primary'), default=True)

    class Meta:
        abstract = True
        permissions = (
            ('set_custom', _('Can set custom domain')),
            ('set_public', _('Can set public status')),
            ('set_active', _('Can set active status')),
        )

    def __init__(self, *args, **kwargs):
        super(BaseSite, self).__init__(*args, **kwargs)
        self.verification_backend = VerficationBackend(self)

    def __unicode__(self):
        return self.name

    def save(self):
        if self.fqdn is "" or self.fqdn is None:
            self.fqdn = self.slug

        if not "." in self.fqdn:
            # if fqdn is a valid host name, otherwise we'll try
            # joining it with SUBDOMAIN_ROOT then test again.
            separator = "."
            if settings.IKARI_SUBDOMAIN_ROOT.startswith("."):
                separator = ""
            self.fqdn = separator.join(
                [self.fqdn, settings.IKARI_SUBDOMAIN_ROOT])

        # should raise an exception if it's not valid.
        self.verification_backend.is_valid()

        return super(BaseSite, self).save()

    @property
    def slug(self):
        return slugify(self.name)

    def user_can_access(self, user):
        # super this method to perform more rigid checks.
        is_valid_user = user and user.is_authenticated and user.is_active
        is_admin = user and is_valid_user and (user.is_superuser or user.is_staff)

        # if the site is disabled
        # or the site isn't in a public state yet
        # and the user is not admin
        # otherwise the site is public, so show the site
        return not self.is_active or not self.is_public and not is_admin

    def get_owner(self):
        raise NotImplementedError(_("You need to provide this method on your class, it needs to return an instance of auth.User"))

    def get_moderators(self):
        raise NotImplementedError(_("You need to provide this method on your class, it needs to return a queryset of auth.User"))
