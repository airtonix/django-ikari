import logging

from django.db.models import get_model
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse
from django.core.handlers.base import BaseHandler

from model_mommy import mommy as mummy

from ikari.conf import settings, null_handler
from ikari.views import SiteHomeView, SiteUpdateView
from .utils import LazyTestCase, UserLogin, TestCase


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

IkariSiteModel = get_model(*settings.IKARI_SITE_MODEL.split("."))
User = get_model('auth', 'User')


class IkariTest(TestCase):
    urls = settings.ROOT_URLCONF
    base_url = "http://" + settings.IKARI_MASTER_DOMAIN
    doesntexist_url = base_url + reverse(settings.IKARI_URL_ERROR_DOESNTEXIST)
    private_url = base_url + reverse(settings.IKARI_URL_ERROR_PRIVATE)
    inactive_url = base_url + reverse(settings.IKARI_URL_ERROR_INACTIVE)
    unknown_url = base_url + reverse(settings.IKARI_URL_ERROR_UNKNOWN)

    def get_headers(self, fqdn):
        return {
            "HTTP_HOST": fqdn,
            "SERVER_NAME": fqdn,
            "SERVER_PORT": "80"
        }

    def make_email(self, username):
        return "{username}@{domain}".format(username=username,
                                            domain=settings.IKARI_MASTER_DOMAIN)

    def assertRedirectsTo(self, response, url):
        """
        Assert that a response redirects to a specific url without trying to
        load the other page.
        """
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], url)

    def setUp(self):
        self.admin = mummy.make('auth.User', username="admin",
                                email=self.make_email('admin'),
                                is_superuser=True, is_active=True, is_staff=True)
        self.admin.set_password('admin')
        self.admin.save()
        self.john = mummy.make('auth.User', username="john",
                               email=self.make_email('john'),
                               is_superuser=False, is_active=True, is_staff=False,
                               password='john')
        self.john.set_password('john')
        self.john.save()

    def test_master_site(self):
        # master site should be accesible.
        response = self.client.get(
            "/", **self.get_headers(settings.IKARI_MASTER_DOMAIN))
        self.assertEqual(response.status_code, 200)

    def test_inactive_site(self):
        site = mummy.make(settings.IKARI_SITE_MODEL,
                          name='The house that John built',
                          is_active=False,
                          is_public=False,
                          owner=self.john)

        # test guest can't access inactive site
        response = self.client.get('/', **self.get_headers(site.fqdn))
        # it should redirect
        # it should redirect to the inactive urlname
        self.assertRedirectsTo(response, self.inactive_url)

        # test owner cant access inactive site
        with UserLogin(username=self.john.username, password='john'):
            response = self.client.get('/', **self.get_headers(site.fqdn))
            # it should redirect to the inactive urlname
            self.assertRedirectsTo(response, self.inactive_url)

        # test admin can access inactive site
        with UserLogin(username=self.admin.username, password='admin'):
            response = self.client.get('/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_active_site(self):
        site = mummy.make(settings.IKARI_SITE_MODEL,
                          name='The house that John built',
                          is_active=False,
                          is_public=False,
                          owner=self.john)

        # test guest can't access inactive site
        response = self.client.get('/', **self.get_headers(site.fqdn))
        # it should redirect to the inactive urlname
        self.assertRedirectsTo(response, self.private_url)
