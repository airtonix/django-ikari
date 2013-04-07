import re

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView, RedirectView, FormView
from django.core.urlresolvers import reverse, reverse_lazy

from . import forms
from . import models
from . import mixins
from . import settings


class DomainErrorView(TemplateView):
    template_name = "domains/error.html"
    error = None

    def get_context(self, *args, **kwargs):
        return {
            'error': self.error
        }

class DomainUpdateView(mixins.DomainViewMixin, mixins.ProtectedView, UpdateView):
    form_class = forms.DomainUpdateForm
    template_name = 'domains/account_detail.html'
    success_url = reverse_lazy('domains-details')

    def get_object(self, *args, **kwargs):
        return self.request.user.domain

    def suggest_subdomain(self, user):
        dn = base = re.sub(r'[^a-z0-9-]+', '-', user.username.lower()).strip('-')
        taken_domains = set([domain.domain for domain in models.Domain.objects.filter(domain__contains=base).all()])
        i = 0
        while dn in taken_domains:
            i += 1
            dn = '%s-%d' % (base, i)
        return dn

    # def get_initial(self):
    #     # suggest a free subdomain name based on username.
    #     # Domainify username: lowercase, change non-alphanumeric to
    #     # dash, strip leading and trailing dashes
    #     kwargs = super(DomainUpdateView, self).get_initial()
    #     user = self.request.user
    #     return kwargs.update({
    #         'domain': self.suggest_subdomain(user),
    #         'subdomain': self.suggest_subdomain(user),
    #     })

        # if 'domain' in request.POST:
        #     form = DomainForm(request.POST, request.FILES, instance=account)
        #     if form.is_valid():
        #         form.save()
        #         return HttpResponseRedirect(return_to)
        # else:
        #     form = DomainForm(instance=account)

        # if 'user' in request.POST:
        #     uform = AddUserForm(request.POST, domainccount=account)
        #     if uform.is_valid():
        #         account.add_member(uform.cleaned_data['user'])
        #         return HttpResponseRedirect(return_to)
        # else:
        #     uform = AddUserForm()

