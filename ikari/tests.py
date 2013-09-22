import logging

from django.test import TestCase
from django.db.models import get_model
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri

from model_mommy import mommy as mummy

from .conf import settings, null_handler


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

IkariSiteModel = get_model(*settings.IKARI_SITE_MODEL.split("."))


class IkariTest(TestCase):

    urls = settings.ROOT_URLCONF
    base_url = "http://"+settings.IKARI_MASTER_DOMAIN
    doesntexist_url = base_url+reverse(settings.IKARI_URL_ERROR_DOESNTEXIST)
    private_url = base_url+reverse(settings.IKARI_URL_ERROR_PRIVATE)
    inactive_url = base_url+reverse(settings.IKARI_URL_ERROR_INACTIVE)
    unknown_url = base_url+reverse(settings.IKARI_URL_ERROR_UNKNOWN)

    def setUp(self):
        self.admin = mummy.make('auth.User', username="admin", is_superuser=True, is_active=True)
        self.john = mummy.make('auth.User', username="john", is_superuser=False, is_active=True)
        self.johns_site = mummy.make(settings.IKARI_SITE_MODEL, 
            name='Johns New Site')
        self.johns_site.set_owner(self.john)
        self.site_meta = {"HTTP_HOST": self.johns_site.fqdn,
                "SERVER_NAME": self.johns_site.fqdn,
                "SERVER_PORT": "80"
                }
        self.master_meta = {
            "HTTP_HOST": settings.IKARI_MASTER_DOMAIN,
            "SERVER_NAME": settings.IKARI_MASTER_DOMAIN,
            "SERVER_PORT": "80"
        }

    def test_master_site(self):
        # master site should be accesible.
        response = self.client.get("/", **self.master_meta)
        self.assertEqual(response.status_code, 200)


    def test_inactive_site(self):
        self.johns_site.is_active = False
        self.johns_site.is_public = False
        self.johns_site.save()

        #test guest can't access inactive site
        response = self.client.get("/", **self.site_meta)
        print response
        self.assertEquals(response.status_code, 302)

        #test admin can access inactive site
        #test owner cant access inactive site

        # change fqdn between subdomain of MASTER_DOMAIN and self supported domain
            # perform above three tests again


    def test_active_site(self):
        # site is active, but not published
        self.johns_site.is_active = True
        self.johns_site.is_public = False
        self.johns_site.save()

        # test guest can't access unpublished site
        response = self.client.get("/", **self.site_meta)
        print response
        self.assertEquals(response.status_code, 302)

        # test admin can access unpublished site
        # test owner can access unpublished site

        # change fqdn between subdomain of MASTER_DOMAIN and self supported domain
            # perform above three tests again

    def test_public_site(self):
        # site is active and published
        self.johns_site.is_active = True
        self.johns_site.is_public = True
        self.johns_site.save()

        # test guest can access
        response = self.client.get("/", **self.site_meta)
        print response
        self.assertEqual(response.status_code, 200)
        # test admin can access
        # test owner can access

        # change fqdn between subdomain of MASTER_DOMAIN and self supported domain
            # perform above three tests again


class IkariWhoisMiddlewareTest(TestCase):

    def setUp(self):
        self.admin = mummy.make('auth.User', username="admin", is_superuser=True, is_active=True)
        self.john = mummy.make('auth.User', username="john", is_superuser=False, is_active=True)
        self.johns_site = mummy.make(settings.IKARI_SITE_MODEL, 
            name='Johns New Site')
        self.johns_site.set_owner(self.john)


    def test_whois_middleware(self):
        """
        Here we 
        """