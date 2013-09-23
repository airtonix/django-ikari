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


class IkariTestBase:
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
        self.master_meta = self.get_headers(settings.IKARI_MASTER_DOMAIN)

    def tearDown(self):
        self.admin.delete()
        self.john.delete()


class IkariSiteTest(IkariTestBase, TestCase):

    def test_master_site(self):
        # master site should be accesible.
        response = self.client.get("/", **self.master_meta)
        self.assertEqual(response.status_code, 200)

    def test_site_is_inactive(self):
        site = mummy.make(settings.IKARI_SITE_MODEL,
                          name='Johns New Inactive Site',
                          is_active=False,
                          is_public=False,
                          owner=self.john)

        # test guest can't access inactive site
        response = self.client.get('/', **self.get_headers(site.fqdn))
        # it should redirect
        self.assertEquals(response.status_code, 302)
        # it should redirect to the inactive urlname
        # self.assertRedirectsTo(response, self.inactive_url)

        # test admin can access inactive site
        with UserLogin(self, self.admin.username, 'admin'):
            response = self.client.get('/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')

        # test owner cant access inactive site
        with UserLogin(self, self.john.username, 'john'):
            response = self.client.get('/', **self.get_headers(site.fqdn))
            # it should redirect
            self.assertEquals(response.status_code, 302)
            # it should redirect to the inactive urlname
            # self.assertRedirectsTo(response, self.inactive_url)

    def test_site_is_active(self):
        site = mummy.make(settings.IKARI_SITE_MODEL,
                          name='Johns New Inactive Site',
                          is_active=True,
                          is_public=False,
                          owner=self.john)

        # test guest can't access inactive site
        response = self.client.get('/', **self.get_headers(site.fqdn))
        # it should redirect
        # self.assertEquals(response.status_code, 302)
        # it should redirect to the inactive urlname
        # self.assertRedirectsTo(response, self.inactive_url)

    # test admin can access inactive site
    #         with self.login(self.admin.username, 'admin'):
    #             response = self.client.get(
    #                 '/', **self.get_headers(site=site))
    # it should allow access
    #             self.assertEquals(response.status_code, 200)
    # it should render the base usersite template
    #             self.assertEquals(response.template_name[0], 'ikari/site.html')

    # test owner cant access inactive site
    #         with self.login(self.john.username, 'john'):
    #             response = self.client.get(
    #                 '/', **self.get_headers(site=site))
    # it should redirect
    #             self.assertEquals(response.status_code, 200)
    # it should redirect to the inactive urlname
    #             self.assertEquals(response.template_name[0], 'ikari/site.html')


# class IkariWhoisMiddlewareTest(TestCase):

#     def setUp(self):
#         self.admin = mummy.make(
#             'auth.User', username="admin", is_superuser=True, is_active=True)
#         self.john = mummy.make(
#             'auth.User', username="john", is_superuser=False, is_active=True)
#         self.johns_site = mummy.make(settings.IKARI_SITE_MODEL,
#                                      name='Johns New Site')
#         self.johns_site.set_owner(self.john)

#     def test_whois_middleware(self):
#         """
#         Here we
#         """

