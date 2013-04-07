import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView, RedirectView, FormView
from django.utils.decorators import method_decorator

from . import models
from . import settings


class DomainViewMixin(object):
    model = models.Domain

    # def get_object(self, *args, **kwargs):
    #     # We edit current user's domain
    #     return self.model.objects.get(owner=self.request.user)


class ProtectedView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)
