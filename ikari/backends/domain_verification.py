import re
import whois
from datetime import datetime


class BaseVerificationBackend(object):
    site = None

    def __init__(self, site=None):
        self.site = site

    def is_valid(self):
        """
            performs all checks, this is the method you use
            in your code.
        """
        raise NotImplementedError("You need to implement this method.")


class FQDNVerificationBackend(BaseVerificationBackend):

    def is_valid(self):
        return self.is_valid_hostname()

    def is_valid_hostname(self):
        """
            Checks if the domain is valid
        """
        hostname = self.site.fqdn

        if len(hostname) > 255:
            return False

        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]

        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))


class WhoisVerficationBackend(FQDNVerificationBackend):

    def is_valid(self):
        if super(WhoisVerficationBackend, self).is_valid():
            return self.does_it_exist()

        return False

    def does_it_exist(self, domain=None):
        """
            Uses pywhois to lookup the domain.
            We could also check that the site owner email matches the records found.
        """
        result = whois.query(self.site.fqdn)

        if not result.expiration_date > now():
            return False

        print result.__dict__
        return True
