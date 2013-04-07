import re
import socket

from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import SafeUnicode
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse, reverse_lazy

from . import models
from . import settings
from . import fields
from . import cache

DOMAIN_RE = re.compile(r'^[a-z0-9][a-z0-9-]*\.[a-z0-9-.]+[a-z0-9]$')
SUBDOMAIN_RE = re.compile(r'^[a-z0-9][a-z0-9-]+[a-z0-9]$')


class DomainUpdateForm(forms.ModelForm):

    class Meta:
        model = models.Domain
        exclude = ('owner', 'members')

    def __init__(self, *args, **kwargs):
        super(DomainUpdateForm, self).__init__(*args, **kwargs)

        self.fields['subdomain'].widget = fields.SubdomainInput()
        owner = instance.get_owner()
        if owner:
            if not owner.has_perm('ikari.can_set_custom_domain'):
                self.fields['domain'].widget = forms.HiddenInput()

            if not owner.has_perm('ikari.can_set_public_status'):
                self.fields['is_public'].widget = forms.HiddenInput()

            if not owner.has_perm('ikari.can_set_active_status'):
                self.fields['is_active'].widget = forms.HiddenInput()

    def clean_subdomain(self):
        subdomain = self.cleaned_data['subdomain'].lower().strip()

        if not SUBDOMAIN_RE.match(subdomain):
            raise forms.ValidationError(settings.ERRORMSG_INVALIDCHARS)

        for pattern in settings.SUBDOMAIN_STOPWORDS:
            if re.search(pattern, subdomain, re.I):
                raise forms.ValidationError(settings.ERRORMSG_UNAVAILABLE)

        domain = cache.get_thing('item', subdomain+settings.SUBDOMAIN_ROOT)
        if domain and domain != self.instance:
            raise forms.ValidationError(settings.ERRORMSG_UNAVAILABLE)

        return domain

    def clean_domain(self):
        owner = instance.get_owner()
        if owner:
            if not owner.has_perm('ikari.can_set_custom_domain'):
                raise forms.ValidationError(settings.ERRORMSG_NOPERMISSION)

            domain_str = self.cleaned_data['domain'].strip().lower()

            if not DOMAIN_RE.match(domain_str):
                raise forms.ValidationError(settings.ERRORMSG_INVALIDCHARS)

            if domain_str.endswith(settings.SUBDOMAIN_ROOT):
                raise forms.ValidationError(settings.ERRORMSG_PROTECTEDTLD)

            try:
                ip = socket.gethostbyname(domain_str)
                if hasattr(settings, 'DOMAINS_IP'):
                    if callable(settings.DOMAINS_IP):
                        if not settings.DOMAINS_IP(ip):
                            self._errors['domain'] = forms.util.ErrorList([
                                _('Domain %s does not resolve to a correct IP number.') % domain_str])
                    else:
                        if ip != settings.DOMAINS_IP:
                            self._errors['domain'] = forms.util.ErrorList([
                                _('Domain %(domain)s does not resolve to %(ip)s.') % {'domain': domain_str, 'ip': settings.DOMAINS_IP}])

            except socket.error, msg:
                self._errors['domain'] = forms.util.ErrorList([
                    _('Cannot resolve domain %(domain)s: %(error_string)s') % {'domain': domain_str, 'error_string': msg}])

        return domain_str

    def clean_is_public(self):
        if self.instance.owner.has_perm('domains.can_set_public_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public

    def clean_is_active(self):
        if self.instance.owner.has_perm('domains.can_set_active_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public


class AddUserForm(forms.Form):
    user = forms.CharField(label='User',
                           help_text='Enter login name or e-mail address',
                           )

    def __init__(self, *args, **kwargs):
        try:
            self.domain = kwargs['domain']

        except KeyError:
            pass

        else:
            del kwargs['domain']

        super(AddUserForm, self).__init__(*args, **kwargs)

    def clean_user(self):
        un = self.cleaned_data['user']
        try:
            if '@' in un:
                u = User.objects.get(email=un)

            else:
                u = User.objects.get(username=un)

        except User.DoesNotExist:
            raise forms.ValidationError(_('User does not exist.'))

        if u == self.domain.owner:
            raise forms.ValidationError(_('You are already the plan owner.'))

        return u

    def clean(self):
        try:
            limit = self.domain.owner.quotas.domain_members

        except AttributeError:
            pass

        else:
            if limit <= len(self.domain.members.all()):
                raise forms.ValidationError(_("Member limit reached."))

        return self.cleaned_data
