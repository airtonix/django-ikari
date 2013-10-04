import logging

from django.db.models import get_model
from django.utils.encoding import iri_to_uri
from django.core.urlresolvers import reverse
from django.core.handlers.base import BaseHandler
from django.db import connection

from model_mommy import mommy as mummy

from ikari import models
from ikari.conf import settings
from ikari.utils import null_handler
from ikari.views import SiteHomeView, SiteUpdateView

from .utils import LazyTestCase, UserLogin, TestCase, override_settings


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

User = get_model('auth', 'User')


class IkariTestBase(object):
    urls = settings.ROOT_URLCONF
    base_url = "http://" + settings.IKARI_MASTER_DOMAIN

    @property
    def doesntexist_url(self):
        return "".join([self.base_url, reverse(settings.IKARI_URL_ERROR_DOESNTEXIST)])

    @property
    def private_url(self):
        return "".join([self.base_url, reverse(settings.IKARI_URL_ERROR_PRIVATE)])

    @property
    def inactive_url(self):
        return "".join([self.base_url, reverse(settings.IKARI_URL_ERROR_INACTIVE)])

    @property
    def unknown_url(self):
        return "".join([self.base_url, reverse(settings.IKARI_URL_ERROR_UNKNOWN)])

    def get_headers(self, fqdn):
        return {
            "HTTP_HOST": fqdn,
            "SERVER_NAME": fqdn,
            "SERVER_PORT": "80"
        }

    def tearDown(self):
        self.site_model.objects.all().delete()

    def setUp(self):
        self.site_model = models.Site

        self.user_owner = self.make_user(
            'owner', 'owner', is_superuser=False, is_active=True, is_staff=False)

        self.user_admin = self.make_user(
            'admin', 'admin', is_superuser=True, is_active=True, is_staff=True)
        self.site_name = "Something something something, darkside"
        self.site_fqdn = "darksi.de"

    def make_user(self, username, password, **kwargs):
        email = "{username}@{domain}".format(username=username,
                                             domain=settings.IKARI_MASTER_DOMAIN)
        user = mummy.make(
            'auth.User', username=username, email=email, **kwargs)
        user._unecrypted_password = password
        user.set_password(password)
        user.save()
        return user

    def assertRedirectsTo(self, response, url):
        """
        Assert that a response redirects to a specific url without trying to
        load the other page.
        """
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], url)


class IkariSiteTestBase(object):

    def test_master_site(self):
        # master site should be accesible.
        response = self.client.get(
            "/", **self.get_headers(settings.IKARI_MASTER_DOMAIN))
        self.assertEqual(response.status_code, 200)

    def test_site_with_port(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)
        response = self.client.get(
            "/", **self.get_headers(settings.IKARI_MASTER_DOMAIN + ":80"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("request").META.get(
            "HTTP_HOST"), settings.IKARI_MASTER_DOMAIN + ":80")

        response = self.client.get(
            "/", **self.get_headers(site.fqdn + ":8000"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('Site').name, site.name)
        self.assertEqual(response.context.get(
            "request").META.get("HTTP_HOST"), site.fqdn + ":8000")

    def test_threading_conflicts(self):
        # master site should be accesible.
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)
        response = self.client.get(
            "/", **self.get_headers(settings.IKARI_MASTER_DOMAIN))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("request").META.get(
            "HTTP_HOST"), settings.IKARI_MASTER_DOMAIN)

        response = self.client.get(
            "/", **self.get_headers(site.fqdn))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('Site').name, site.name)

        response = self.client.get(
            "/", **self.get_headers(settings.IKARI_MASTER_DOMAIN))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("request").META.get(
            "HTTP_HOST"), settings.IKARI_MASTER_DOMAIN)

    def test_site_inactive(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=False,
                          is_public=False,
                          owner=self.user_owner)
        self.assertEquals(site.is_active, False)
        self.assertEquals(site.is_public, False)

    def test_site_private(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=False,
                          owner=self.user_owner)
        self.assertEquals(site.is_active, True)
        self.assertEquals(site.is_public, False)

    def test_site_public(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)
        self.assertEquals(site.is_active, True)
        self.assertEquals(site.is_public, True)

    def test_inactive_site_guest(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=False,
                          is_public=False,
                          owner=self.user_owner)

        # test guest can't access inactive site
        response = self.client.get(
            '/', **self.get_headers(site.fqdn))
        # it should redirect to the inactive urlname
        self.assertLocationEquals(response, self.inactive_url)

    def test_inactive_site_admin(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=False,
                          is_public=False,
                          owner=self.user_owner)

        # test admin can access inactive site
        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_inactive_site_owner(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=False,
                          is_public=False,
                          owner=self.user_owner)

        # test owner cant access inactive site
        with self.login(self.user_owner.username, self.user_owner._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            # it should redirect to the inactive urlname
            self.assertLocationEquals(response, self.inactive_url)

    def test_private_site_guest(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=False,
                          owner=self.user_owner)

        # test guest can't access private site
        response = self.client.get(
            '/', **self.get_headers(site.fqdn))
        # it should redirect to the private urlname
        self.assertLocationEquals(response, self.private_url)

    def test_private_site_admin(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=False,
                          owner=self.user_owner)

        # test owner can access private site
        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            self.assertEquals(response.status_code, 200)
            self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_private_site_owner(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=False,
                          owner=self.user_owner)

        # test owner can access private site
        with self.login(self.user_owner.username, self.user_owner._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_public_site_guest(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)

        response = self.client.get(
            '/', **self.get_headers(site.fqdn))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_public_site_admin(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)

        # test admin can access inactive site
        with self.login(self.user_owner.username, self.user_owner._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')

    def test_public_site_owner(self):
        site = mummy.make(self.site_model,
                          name=self.site_name,
                          is_active=True,
                          is_public=True,
                          owner=self.user_owner)

        # test admin can access inactive site
        with self.login(self.user_admin.username, self.user_admin._unecrypted_password):
            response = self.client.get(
                '/', **self.get_headers(site.fqdn))
            # it should allow access
            self.assertEquals(response.status_code, 200)
            # it should render the base usersite template
            self.assertEquals(response.template_name[0], 'ikari/site.html')


class BasicIkariTest(IkariTestBase, IkariSiteTestBase, LazyTestCase):
    """
      Normal tests
    """

# CustomSiteSettings = {
#     "IKARI_SITE_MODEL": 'tests.site.SomeCustomisedSite',
#     "DATABASES": {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': 'customised_sitet',
#         }
#     }
# }


# @override_settings(**CustomSiteSettings)
# class IkariCustomSiteTest(IkariSiteTestBase, IkariTestBase, LazyTestCase):

#     """
#         This test case covers the scenario where a project integrator
#         will specify their own IKARI_SITE_MODEL.
#     """
