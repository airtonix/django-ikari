import warnings
from uuid import uuid4
import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from .conf import settings, null_handler
from .loader import load_class
from . import cache


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)
VerficationBackend = load_class(settings.IKARI_DOMAIN_VERIFICATION_BACKEND)


class BaseSiteMembership(models.Model):
    user = models.ForeignKey('auth.User', blank=False, null=False)
    site = models.ForeignKey('ikari.Site', blank=False, null=False)
    access_level = models.CharField(verbose_name=_("Access Level"),
                                    max_length=32,
                                    choices=(
                                        ('admin', "Site Administrator"),
                                        ('moderator', "Site Moderator"),
                                        ('reviewer', "Site Reviewer"),
                                    ))

    class Meta:
        abstract = True


class BaseSite(models.Model):

    uuid = models.CharField(verbose_name=_('UUID'),
                            blank=True, null=True, max_length=255,
                            unique=True, default=lambda: uuid4())
    name = models.CharField(verbose_name=_("Site Name"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))

    fqdn = models.CharField(verbose_name=_('Domain Name'),
                            help_text=_("Either a) Fully qualified domain name <a href='http://en.wikipedia.org/wiki/Fully_qualified_domain_name'>help</a>, or b) a slugified word as a subdomain of {}, or c) blank which will use the slugified name.".format(
                                settings.IKARI_MASTER_DOMAIN)),
                            blank=True, null=True, max_length=255, unique=True)

    owner = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name="owns_site")
    members = models.ManyToManyField(
        'auth.User', through='ikari.SiteMembership', blank=True, null=True)

    is_public = models.BooleanField(verbose_name=_('Is public'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=False)
    is_primary = models.BooleanField(
        verbose_name=_('Is primary'), default=True)

    class Meta:
        abstract = True
        permissions = (
            ('set_custom', 'Can set custom domain'),
            ('set_public', 'Can set public status'),
            ('set_active', 'Can set active status'),
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
        is_valid_user = user and user.is_authenticated and user.is_active
        # staff and superuser can always access the site
        if is_valid_user and (user.is_superuser or user.is_staff):
            return True

        # if the site is disabled (only site staff can toggle this)
        if not self.is_active:
            return False

        # if the site isn't in a public state yet
        if not self.is_public and is_valid_user:
            # if the user is allowed to manage the site
            if user in (self.get_owner(), self.get_moderators()):
                return True

            # only site owners and moderators can access active yet unpublished
            # sites.
            return False

        # site is active and published
        return True

    def get_owner(self):
        return self.owner

    def set_owner(self, user):
        self.owner = user
        self.save()

    def get_moderators(self):
        raise NotImplementedError(
            "You need to implemenet this in your own subclass")


class Site(BaseSite):

    class Meta:
        abstract = False


class SiteMembership(BaseSiteMembership):

    class Meta:
        abstract = False


post_save.connect(cache.cache_thing, sender=Site, dispatch_uid='save_domain')
post_delete.connect(cache.uncache_thing,
                    sender=Site, dispatch_uid='delete_domain')
