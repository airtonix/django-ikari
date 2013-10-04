Django Anchored Domains
==========================

django-ikari is an application for anchoring configurable
urlconfs to user configurable subdomains or domains to use
in software-as-a-service projects.

[![Build Status](https://travis-ci.org/airtonix/django-ikari.png?branch=master)](https://travis-ci.org/airtonix/django-ikari)

## Table of Contents

1. Installation
2. Settings
3. Models
  * Permissions
4. Middleware
5. Views
6. Caching
7. Signals
8. URLs
9. Templates
10. License


### 1 Installation

 `pip install django-ikari`

  In order to use application, add `ikari' to `INSTALLED_APPS` in
  Django project `settings.py' file,
  `ikari.middleware.DomainsMiddleware' to `MIDDLEWARE_CLASSES`
  after `AuthenticationMiddleware', and configure application settings
  described in the next section.

### 2 Settings


#### IKARI_MASTER_DOMAIN

This needs to point at the domain
of your main project, typically
the place where you'd have forms that
process payments, login users, process
beta invites etc.

#### IKARI_ACCOUNT_URLCONF

routes which define paths to views to
allow users to manage their site(s)

#### IKARI_SITE_URLCONF

routes that are anchored to the root
of users sites. this urlconf will replace
your ROOT_URLCONF setting when a requested
hostname matches an active ( and published
if the user is a site member) site.

#### IKARI_URL_ERROR_*

* IKARI_URL_ERROR_DOESNTEXIST
* IKARI_URL_ERROR_PRIVATE
* IKARI_URL_ERROR_INACTIVE
* IKARI_URL_ERROR_UNKNOWN

Url to redirect visitors to when they
land on a subdomain that isn't linked
to a ikari site.

#### IKARI_SUBDOMAIN_ROOT

if user defines a valid whole word then it is joined to
this. Defaults to something like "."+`IKARI_MASTER_DOMAIN`

#### IKARI_SITE_MODEL

a python import path to your customised IkariSite model.
you can subclass the abstract `ikari.models.bases.SiteBase`
model as a good start.


### Experimental Settings

#### IKARI_DOMAIN_VERIFICATION_BACKEND

a python import path to a verification backend that can
be used to ensure the domain provided by the user satisfies
your business logic.

#### IKARI_SITE_PERMISSION_GROUPS

Probably only relevant if you use the default provided `ikari.models.default.Site` class.
Simply provides some role based permissions, although it is recommended that you
use django-guardian and implement some action based permissions.


### 3 Models

Ikari ships with two default models, only one of which is required as defined
above in your settings as `IKARI_SITE_MODEL`.

For the purpose of this section, "site urls" refers to the setting 
attribute `IKARI_SITE_URLCONF`.

You site model should at least have the following fields and methods:

* `is_public`, boolean.  If True, then Anonymous users will
  be allowed to view the url routes in the "site urls".
  If False (default), DomainMiddleware will
  only allow the following instance of `auth.User':
  * `is_staff=True` or,
  * `is_superuser=True`, or
  * `user in site.get_members()`

* `is_active`, boolean.  If False (default), DomainMiddleware will
  only allow any `auth.User.is_staff or auth.User.is_superuser` to access the "site urls";
  if True, then site owners and other related users can also view the "site urls".


### 3.1 Permissions

* `can_set_custom_domain' enables setting a domain which is not suffixed
with the `IKARI_SUBDOMAIN_ROOT` value.
* `can_set_public_status' does the same for `is_public' field.
* `can_set_active_status' does the same for `is_active' field.


### 4 Middleware
`ikari.middleware.DomainsMiddleware' looks at
`request.get_host()` and, if it matches any `ikari.Site` model
instance:
* sets `request.ikari_site' to that instance (it can be later used by
  views and, with `request` context processor, in templates);
* unless `request.ikari_site.is_public' is true, it immediately logs
  out (and redirects to reverse URL lookup of
  `settings.IKARI_URL_ERROR_PRIVATE`) any `auth.User` that does not
  satisfy this sites get_moderators() method;
- if `IKARI_SITE_URLCONF' setting is set, sets
  `request.urlconf' to its value, allowing single project to display
  different URL hierarchies for main site and account sites;
  *WARNING*: setting `request.urlconf' doesn't fit well with reverse
  URL lookups (those will still be made against root urlconf),
  django-debug-toolbar, and probably other things as well. For
  maximum reliability, consider running two separate projects on
  single database: one for "main" site, other for account domains,
  or use single urlconf for both;
- send signal `ikari.signals.site_request' and if any
  receiver returns an instance of `HttpResponse`, returns this
  response instead of actual page.  This can be used for
  e.g. displaying error message and not allowing to log into expired
  accounts.

If current domain doesn't match any of existing `ikari.Site` instances
and is not `IKARI_MASTER_DOMAIN', middleware redirects user to
`IKARI_MASTER_DOMAIN'.


### 5 Views

* `ikari.views.DomainErrorView` : View used to render the templates for each of 
  * IKARI_URL_ERROR_DOESNTEXIST
  * IKARI_URL_ERROR_PRIVATE
  * IKARI_URL_ERROR_INACTIVE
  * IKARI_URL_ERROR_UNKNOWN
* `ikari.views.SiteHomeView` : Main view to render an `ikari.Site`
* `ikari.views.SiteUpdateView` : Allows authorised users to update their site details.
* `ikari.views.SiteCreateView` : Allows authorised users to create their site.


### 6 Caching

I susgest you install and use `django-johnny-cache` with `django-redis-cache`


### 7 Signals

* `ikari.signals.site_request`: fired after default access rules satisfied but before delivery
of site homepage
* `ikari.signals.site_created`: fired after a new `ikari.Site` is created.
* `ikari.signals.site_updated`: fired after an `ikari.Site` is updated.
* `ikari.signals.site_deleted`: fired after an `ikari.Site` is deleted.


### 8 URLs

##### `ikari.urls.errors`

Include this somewhere in your main site urlconf. example:
```
...
url(r'^sites/error/', include('ikari.urls.errors')),
...
```

##### `ikari.urls.private`

Include this somewhere in your main site urlconf. example:
```
...
url(r'^users/sites/', include('ikari.urls.private')),
...
```

##### `ikari.urls.sites`

The default urlconf which provides the `ikari.views.SiteHomeView`.


### 9 Templates
Ikari:
- `ikari/site-update.html` called by `ikari.views.SiteUpdateView` view.
  Receives two arguments:
  - `Site` - `ikari.Site` instance, and
  - `form` - `forms.IkariSiteForm` instance to display.
- `ikari/site-create.html` called by `ikari.views.SiteCreateView` view.
  Receives one argument, `form`, holding an instance of
  `ikari.forms.IkariSiteForm`.


### 10 License
  This project is licensed on terms of GPL (GPL-LICENSE.txt) licenses.