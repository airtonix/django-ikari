import logging

from django.contrib import admin
import whois

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model
from django.utils.datastructures import SortedDict

from . import models
from .loader import load_class
from .conf import settings
from .utils import null_handler
from .forms import IkariSiteAdminForm

site_model_string = settings.IKARI_SITE_MODEL
logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class IkariSiteAdmin(admin.ModelAdmin):

    form = IkariSiteAdminForm

    def verify_site(instance, request, queryset):
        results = []
        for site in queryset:
            logger.debug("attempting to verify site:", site)
            results.append(whois.query(site.fqdn))
        # TODO: redirect to report page, print whois results.

    verify_site.short_description = 'Query the site txt record for the uuid.'

    def enable_site(instance, request, queryset):
        queryset.update(is_active=True)
    enable_site.short_description = _('Enable the selected sites.')

    def disable_site(instance, request, queryset):
        queryset.update(is_active=False)
    disable_site.short_description = _('Enable the selected sites.')

    def publish_site(instance, request, queryset):
        queryset.update(is_public=True)
    publish_site.short_description = _('Make selected sites public.')

    def unpublish_site(instance, request, queryset):
        queryset.update(is_public=False)
    unpublish_site.short_description = _('Make selected sites private.')

    def set_site_as_primary(instance, request, queryset):
        queryset.update(is_primary=True)
    set_site_as_primary.short_description = 'Make the selected items the primary site for their anchored objects.'

    list_display = ('fqdn', 'is_public', 'is_active', 'is_primary', )
    actions = [verify_site,
               disable_site, enable_site,
               publish_site, unpublish_site,
               set_site_as_primary]


admin.site.register(models.Site, IkariSiteAdmin)
