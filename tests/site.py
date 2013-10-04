from django.db import models
from django.utils.translation import ugettext_lazy as _

from ikari.models.bases import BaseSite


class SomeCustomisedSite(BaseSite):

    """
        custom site model test case scenario
    """
    by_line = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_(u'By Line'))
    owner = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name="sites")

    class Meta:
        abstract = False

    def get_owner(self):
        return self.owner

    def get_moderators(self):
        return []

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
