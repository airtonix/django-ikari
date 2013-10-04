import logging

from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from django.utils.translation import ugettext_lazy as _

from . import forms
from .conf import settings
from .utils import null_handler


logger = logging.getLogger(__name__)
logger.addHandler(null_handler)


class DomainErrorView(TemplateView):
    template_name = "ikari/error.html"


class SiteHomeView(TemplateView):
    template_name = "ikari/site.html"

    def get_context_data(self, **kwargs):
        return {
            "Site": self.request.site
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
