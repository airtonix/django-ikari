from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..conf import settings
from ..utils import null_handler
from ..loader import get_model_string
from .bases import BaseSite


USER_MODEL_STRING = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
SITE_MODEL_STRING = get_model_string("Site")


class SiteMembership(models.Model):
    user = models.ForeignKey(USER_MODEL_STRING, blank=False, null=False)
    site = models.ForeignKey(SITE_MODEL_STRING, blank=False, null=False)
    access_level = models.CharField(verbose_name=_("Access Level"),
                                    max_length=32,
                                    choices=settings.IKARI_SITE_PERMISSION_GROUPS)

    class Meta:
        abstract = False


class Site(BaseSite):
    owner = models.ForeignKey(
        USER_MODEL_STRING, blank=True, null=True, related_name="sites")
    members = models.ManyToManyField(
        USER_MODEL_STRING, through=SiteMembership, blank=True, null=True)

    class Meta:
        abstract = False

    def get_owner(self):
        return self.owner

    def get_moderators(self):
        return self.members.all()

    def user_can_access(self, user):
        is_valid_user = user and user.is_authenticated and user.is_active
        is_admin = user and is_valid_user and (
            user.is_superuser or user.is_staff)
        is_manager = is_valid_user and user in (
            self.get_owner(), self.get_moderators())

        # if the site is disabled
        # and the user not is not admin
        if not self.is_active and not is_admin:
            return False
            # raise exceptions.SiteErrorInactive()

        # if the site isn't in a public state yet
        # and the user is not admin
        # or the user is not site manager
        elif not self.is_public:
            return (is_manager or is_admin)
            # raise exceptions.SiteErrorIsPrivate()
            # otherwise the site is public and the user is we don't care
            # or the site is private and the user is a manager

        # otherwise show the site
        return True
