import logging

from django.test import TestCase
from django.db.models import get_model
from django.core.urlresolvers import reverse

from model_mommy import mommy as mummy

from .conf import settings, null_handler


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class SubdomainTest(TestCase):

    def setUp(self):
        self.admin = mummy.make('auth.User', username="admin", is_superuser=True, is_active=True)
        self.john = mummy.make('auth.User', username="john", is_superuser=False, is_active=True)
        self.johns_site = mummy.make(settings.IKARI_SITE_MODEL, name='Johns New Site')
        self.johns_site.set_owner(self.john)

    def test_master_site(self):
        self.urls = settings.ROOT_URLCONF
        url = reverse("home")
        print url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)