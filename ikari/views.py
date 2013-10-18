import logging

from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from . import forms
from . import exceptions
from .conf import settings
from .utils import null_handler

logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class DomainErrorView(TemplateView):
    template_name = "ikari/error.html"


class SiteHomeView(TemplateView):
    template_name = "ikari/site.html"
    context_site_name = "Site"

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(SiteHomeView, self).dispatch(request, *args, **kwargs)
        except exceptions.SiteErrorDoesNotExist:
            return HttpResponseRedirect(reverse(settings.IKARI_URL_ERROR_DOESNTEXIST))

    def get_object(self, **kwargs):
        try:
            return self.request.ikari_site
        except AttributeError:
            raise exceptions.SiteErrorDoesNotExist

    def get_context_data(self, **kwargs):
        return {
            self.context_site_name: self.get_object()
        }


class SiteDeleteView(DeleteView):
    form_class = forms.IkariSiteForm
    template_name = "ikari/site-delete.html"


class SiteUpdateView(UpdateView):
    form_class = forms.IkariSiteForm
    template_name = "ikari/site-update.html"


class SiteCreateView(CreateView):
    form_class = forms.IkariSiteForm
    template_name = "ikari/site-create.html"
