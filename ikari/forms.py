import re
import socket
import logging

from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import SafeUnicode
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy

from .conf import settings
from .utils import null_handler
from . import models
from . import fields
from . import cache
from . import utils


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class IkariSiteAdminForm(forms.ModelForm):

    class Meta:
        model = models.Site

    def clean_fqdn(self):
        fqdn = self.cleaned_data.get('fqdn')
        if fqdn == '':
            fqdn = None
        return fqdn


class IkariSiteForm(forms.ModelForm):

    class Meta:
        model = models.Site
        exclude = ('owner', 'members')

    def __init__(self, *args, **kwargs):
        super(IkariSiteForm, self).__init__(*args, **kwargs)
        owner = kwargs.get("user", None)
        self.fields['subdomain'].widget = fields.SubdomainInput()
        if not owner and self.instance:
            owner = self.instance.get_owner()
            if owner:
                if not owner.has_perm('ikari.set_custom'):
                    self.fields['domain'].widget = forms.HiddenInput()

                if not owner.has_perm('ikari.set_public'):
                    self.fields['is_public'].widget = forms.HiddenInput()

                if not owner.has_perm('ikari.set_active'):
                    self.fields['is_active'].widget = forms.HiddenInput()

    def clean_fqdn(self):
        fqdn = self.cleaned_data.get('fqdn').lower().strip()
        owner = self.instance.get_owner()

        if owner and not owner.has_perm('ikari.can_set_custom_domain'):
            # this will cause the model save logic to append the SUBDOMAIN_ROOT
            return self.instance.get_slug()

        if not utils.is_valid_hostname(fqdn):
            raise forms.ValidationError(settings.ERRORMSG_INVALIDCHARS)

        for pattern in settings.SUBDOMAIN_STOPWORDS:
            if re.search(pattern, fqdn, re.I):
                raise forms.ValidationError(settings.ERRORMSG_UNAVAILABLE)

        site = cache.get_thing('item', fqdn + settings.SUBDOMAIN_ROOT)
        if site and site != self.instance:
            raise forms.ValidationError(settings.ERRORMSG_UNAVAILABLE)

        # if owner and :
        #     if not owner.has_perm('ikari.can_set_custom_domain', self.instance):
        #         raise forms.ValidationError(settings.ERRORMSG_NOPERMISSION)

            # try:
            #     ip = socket.gethostbyname(domain_str)
            #     if hasattr(settings, 'DOMAINS_IP'):
            #         if callable(settings.DOMAINS_IP):
            #             if not settings.DOMAINS_IP(ip):
            #                 self._errors['domain'] = forms.util.ErrorList([
            #                     _('Domain %s does not resolve to a correct IP number.') % domain_str])
            #         else:
            #             if ip != settings.DOMAINS_IP:
            #                 self._errors['domain'] = forms.util.ErrorList([
            #                     _('Domain %(domain)s does not resolve to %(ip)s.') % {'domain': domain_str, 'ip': settings.DOMAINS_IP}])

            # except socket.error as msg:
            #     self._errors['domain'] = forms.util.ErrorList([
            #         _('Cannot resolve domain %(domain)s: %(error_string)s') % {'domain': domain_str, 'error_string': msg}])

        return domain_str

    def clean_is_public(self):
        #TODO: guardian permissions
        if self.instance.owner.has_perm('domains.can_set_public_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public

    def clean_is_active(self):
        #TODO: guardian permissions
        if self.instance.owner.has_perm('domains.can_set_active_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public
