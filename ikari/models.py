import warnings
import os
from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.defaultfilters import slugify

from . import signals
from . import fields
from . import settings
from . import cache


class Domain(models.Model):

    uuid = models.CharField(verbose_name=_('UUID'),
        blank=True, null=True, max_length=256, unique=True, default=lambda: uuid4() )

    domain = models.CharField(verbose_name=_('Domain'),
        blank=True, null=True, max_length=256, unique=True, )
    subdomain = models.CharField(verbose_name=_('Subdomain'),
        max_length=256, unique=True, null=True)

    is_public = models.BooleanField(verbose_name=_('Is public'), default=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=False)
    is_primary = models.BooleanField(verbose_name=_('Is primary'), default=False)

    anchored_on = models.OneToOneField(settings.ANCHORED_MODEL,
        verbose_name=_('Anchored To'), related_name='domain')

    class Meta:
        permissions = (
            ('set_custom', 'Can set custom domain'),
            ('set_public', 'Can set public status'),
            ('set_active', 'Can set active status'),
        )

    def save(self):
        if self.domain == "" or self.domain == None:
            self.domain = None
        return super(Domain, self).save()

    def __unicode__(self):
        return self.get_name()

    def get_slug(self):
        return slugify(self.get_name())

    def get_name(self):
        output = "domain-"+str(self.pk)
        if self.domain:
            output = self.domain

        if self.subdomain:
            output = self.subdomain + settings.SUBDOMAIN_ROOT

        return "{}".format(output)

    def user_can_access(self, user):

        if not user.is_active:
            print user, "not active"
            return False

        if user.is_staff:
            print user, "is staff"
            return True

        if user.is_superuser:
            print user, "is superuser"
            return True

        if self.anchored_on:
            print self, "is anchored to", self.anchored_on
            members = getattr(self.anchored_on, settings.ANCHORED_MODEL_MEMBER_ATTR)
            if user is self.get_owner() or user in members:
                return True
            print user, "is owner or member"

        return False

    def get_owner(self):
        # test if related object is the user model
        if isinstance(self.anchored_on, User):
            # return it
            owner = self.anchored_on
        else:
            owner = getattr(self.anchored_on, settings.ANCHORED_MODEL_OWNER_ATTR)
            if callable(owner):
                owner = owner()
        return owner

    def get_full_domain(self):
        if self.domain:
            return self.domain
        return self.subdomain+settings.SUBDOMAIN_ROOT

    def get_absolute_url(self, path='/', *args, **kwargs):
        port = ''
        if settings.PORT:
            port = ':{}'.format(settings.PORT)

        if not path.startswith('/'):
            if settings.USERSITE_URLCONF:
                path = reverse(path, args=args, kwargs=kwargs,
                               urlconf=settings.USERSITE_URLCONF)
            else:
                warnings.warn(
                    'Cannot resolve without settings.DOMAINS_USERSITE_URLCONF, using / path.')
                path = '/'
        output = '//{domain}{port}{path}'.format(domain=self.get_full_domain(), port=port, path=path)

        return output


post_save.connect(cache.cache_thing, sender=Domain, dispatch_uid='save_domain')
post_delete.connect(cache.uncache_thing, sender=Domain, dispatch_uid='delete_domain')
