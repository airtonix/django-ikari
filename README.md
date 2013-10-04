Django Anchored Domains
==========================

django-ikari is an application for anchoring configurable
urlconfs to user configurable subdomains or domains to use
in software-as-a-service projects.

[![Build Status](https://travis-ci.org/airtonix/django-ikari.png?branch=develop)](https://travis-ci.org/airtonix/django-ikari)

Table of Contents
=================
1 Installation
2 Settings
3 Models
    3.1 Permissions
4 Middleware
5 Views
6 URLs
7 Templates
8 License


1 Installation
~~~~~~~~~~~~~~

 `pip install django-ikari`

  In order to use application, add `ikari' to INSTALLED_APPS in
  Django project `settings.py' file,
  `ikari.middleware.DomainsMiddleware' to MIDDLEWARE_CLASSES
  after `AuthenticationMiddleware', and configure application settings
  described in the next section.

2 Settings
~~~~~~~~~~
  Following Django settings are read by the application:
  - `DOMAINS_ACCOUNT_URLCONF' - if set, `request.urlconf' is set to
    this value when Domain's domain is accessed.  This breaks
    django-debug-toolbar and misleads reverse URL resolver (main
    urlconf is always used for reverse URL resolving).
  - `DOMAINS_DEFAULT_DOMAIN' - Default domain name, on which "main"
    (non-user) site is hosted.  Used to prevent redirection to
    `DOMAINS_DEFAULT_URL' when `DomainsMiddleware' is used both
    on accounts' sites and main site.  Also used to construct default
    value of `DOMAINS_DEFAULT_URL' when it is not set.
  - `DOMAINS_DEFAULT_URL' - URL to redirect to when user agent
    refers to site with an unknown domain (not registered in any of
    accounts).  When not set, a URL is constructed from
    `DOMAINS_DEFAULT_DOMAIN' or current Site object's domain and
    `DOMAINS_PORT'.
  - `DOMAINS_IP' - if set, value is used to verify custom domains
    in `DomainForm'.  It can be set to a string (literal
    'aa.bb.cc.dd' value that is compared to `sockets.gethostbyname()'
    result), or, for more complex deployments, it can be a function
    that will receive IP as returned by `sockets.gethostbyname()'
  - `DOMAINS_PORT' - can be set to custom port that will be used in
    Domain site URLs.  This way, developer can successfully use
    Domains on e.g. 127.0.0.1:8000.
  - `DOMAINS_ROOT_DOMAIN' - root domain for subdomains (with or
    without leading dot).  Must be set.
  - `DOMAINS_SUBDOMAIN_STOPWORDS' - tuple of regular expressions
    ([http://docs.python.org/library/re.html]) that cannot be used as
    subdomain names.  Default is `("^www$",)'.  Use this to stop users
    from e.g. using reserved domain names or using profanities as
    their domain name.  Expressions are tested using `re.search', not
    `re.match', so without using `^' anchor they can match anywhere in
    the domain name.
  - `DOMAINS_THEMES' - a sequence of (codename, name) pairs
    indicating available themes for user sites.
  - `DOMAINS_USE_SSO' - use django-sso when redirecting user to
    newly created site.  Default is True if django-sso is available,
    False otherwise.
  - `DOMAINS_USERSITE_URLCONF' - name of URLconf module for user
    sites.  This is used by Domain instances' get_absolute_url()
    method.

3 Models
~~~~~~~~
  Application defines one model, `Domain'.  Model has three fields:
  - `owner', OneToOneField reference to
    `django.contrib.auth.models.User' model, which holds user owning
    the account;
  - `members', ManyToManyField reference to
    `django.contrib.auth.models.User' model, which holds account
    members;
  - `domain', name of custom full domain for the site, changeable by
    user;
  - `subdomain', a sub-domain of `DOMAINS_ROOT_DOMAIN', not
    editable by user;
  - `is_public', boolean.  If True (default), DomainMiddleware will
    allow any `auth.User' to log in to Domain's account; if False,
    only users that are Domain members will be allowed;
  Class has one class attribute, `subdomain_root', which contains root
  for subdomains as in `DOMAINS_ROOT_DOMAIN' setting description,
  always with leading dot.  This attribute should not be written.

  Model defines `get_absolute_url(path = '/', args = (), kwargs = {})'
  method, which returns link to configured domain
  ([http://subdomain.root_domain/path] if `domain' is None,
  [http://domain/path] otherwise).  Optional path can be either an
  absolute path or, if `settings.DOMAINS_USERSITE_URLCONF' is set,
  a name, args and kwargs for reverse URL lookup.

  Two methods are defined, `add_member(user)' and
  `remove_member(user)' to respectively add or remove `user' from
  `members' and send out `domains.signals.add_member' or
  `domains.signals.remove_member' with additional `user'
  parameter.

3.1 Permissions
===============
   - `can_set_custom_domain' enables setting `is_subdomain' to `True'
     by the account owner.  If Domain owner does not have such
     permission, `account_detaul' view hides checkbox for
     `is_subdomain', and on form validation `is_subdomain' field is
     unconditionally set to `True';
   - `can_set_public_status' does the same for `is_public' field.

4 Middleware
~~~~~~~~~~~~
  `domains.middleware.DomainsMiddleware' looks at
  `request.META['HTTP_HOST']' and, if it matches any `Domain' model
  instance:
  - sets `request.domain' to that instance (it can be later used by
    views and, with `request' context processor, in templates);
  - immediately logs out (and redirects to reverse URL lookup of
    `domains_not_a_member') any `auth.models.User' that is not this
    account's owner or memeber, unless `request.domain.is_public'
    is true;
  - if `DOMAINS_ACCOUNT_URLCONF' setting is set, sets
    `request.urlconf' to its value, allowing single project to display
    different URL hierarchies for main site and account sites;

    *WARNING*: setting `request.urlconf' doesn't fit well with reverse
    URL lookups (those will still be made against root urlconf),
    django-debug-toolbar, and probably other things as well. For
    maximum reliability, consider running two separate projects on
    single database: one for "main" site, other for account domains,
    or use single urlconf for both;
  - send signal `domains.signals.domain_request' and if any
    receiver returns an instance of `HttpResponse', returns this
    response instead of actual page.  This can be used for
    e.g. displaying error message and not allowing to log into expired
    accounts.

  If current domain doesn't match any of existing Domain instances
  and is not `DOMAINS_DEFAULT_DOMAIN', middleware redirects user to
  `DOMAINS_DEFAULT_DOMAIN'.

5 Views
~~~~~~~
  - `domains.views.create_account' - if logged in user does not
    have a Domain, displays a form to create a new one or accepts
    results of this form.  After accepting form and creating new
    account, redirects user to that account, using django-sso if
    available.  It is not configured in default `urls.py' and should
    be added directly in main site's urlconf.
  - `domains.views.account_detail' - displays using
    `domains/account_detail.html' template and validates
    `domains.forms.DomainForm' form, which enables user to
    configure account's domain.  In supplied `urls.py' this view is
    named `domains_account_detail'.
  - `domains.views.claim_account' - if `domain.owner' is NULL,
    logged in user can "claim" the account, i.e. click a button
    directing to this view, which will send an e-mail to
    `settings.MANAGERS'.  This view should be called with a POST
    request.  In default `urls.py' this view is named
    `domains_claim_account'.
  - `domains.views.remove_member' - for Domain_owner, with
    `user_id' parameter set, this post will remove user with supplied
    ID from the member list.  This view should be called with a POST
    request.  In default `urls.py' this view is called
    `domains.views.remove_member'.

6 URLs
~~~~~~
  In supplied urlconf, `domains.urls', one external URL is
  configured: root for `account_detail' view.  More URLs are
  configured for various POST actions.  This is intended to be
  included in the subdomain sites' urlconf.

  In main site a link to create account form should be used.  Account
  is created by view `domains.views.create_account'.  Sample
  urlconf line is:
   (r'^accounts/create-site/$', 'domains.views.create_account'),

7 Templates
~~~~~~~~~~~
  Application in default setup needs two templates:
  - `domains/account_detail.html' called by `account_detail' view.
    Receives two arguments:
    - `object' - edited Domain instance, and
    - `form' - DomainForm instance to display.
  - `domains/create_account.html' called by `create_account' view.
    Receives one argument, `form', holding an instance of
    DomainCreateForm.
  - `domains/claim_account_subject.txt' and
    `domains/claim_account_email.txt' - these templates are used by
    `claim_account' view to create an e-mail to MANAGERS.  This
    templates receive three arguments:
    - `user' - user that is sending the claim,
    - `domain' - an account that is claimed,
    - `site' - `sites.Site' object for current site.


8 License
~~~~~~~~~~
  This project is licensed on terms of GPL (GPL-LICENSE.txt) licenses. 
