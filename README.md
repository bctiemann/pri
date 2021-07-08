# PRI Django

This is the Python/Django implementation of the Performance Rentals shopping/rental/ecommerce website.

## Installation

Development should be done in a local environment using a sqlite (default) or MySQL/PostgreSQL database instance.

Django provides a testing app runner via the `manage.py` command, i.e. `./manage.py runserver` (see below)

To set up your local environment, you will need to create a python virtualenv.

### Virtualenv Setup

- Ensure you have a recent version of Python installed locally. This project is built for Python 3.8.
- You will also need `pip` (normally installed as part of Python) and Virtualenv which can be installed from https://sourabhbajaj.com/mac-setup/Python/virtualenv.html
Virtualenv is a means of localizing a python environment and its installed packages to a specific project, so changes to
the OS-level Python do not affect your development environments, which are also segregated from one another.
- Once you have virtualenv, cd into the root directory of this project and enter: 
`virtualenv venv --python=<path/to/python>`
- Then activate the virtualenv (which sets the enviroment vars to use the localized python for this shell only):
`. venv/bin/activate` (other activate commands exist for non-bash shells). This is how you will need to activate the venv
to work with the project from now on (though PyCharm automates this; see below).
- You can deactivate the shell's environment at any time with `deactivate`. Or just close the shell, it is not persistent.
- You can now install the project's Python requirement libraries:
`pip install -r requirements.txt`
- Check the installed libraries using `pip freeze`
- Finally, set up your local database using `./manage.py migrate`. This will create the SQLite database using all existing migrations
and sync the tables with the models in code.
- You can now run the app using `./manage.py runserver [8000]` and connect to it locally at http://127.0.0.1:8000

### PyCharm Setup

If you are using PyCharm, you will need to configure it to look in your venv for the Python interpreter to use.

- Go to *Preferences > Project: pri_dj*
- In *Python Interpreter*, if the "Python Interpreter" selector does not point to the python executable in your project's venv,
you will need to click the gear icon and "Add", then select "Existing environment". Use the "..." button to navigate to the 
project's venv and the `venv/bin/python` binary.
- Open a new Terminal window (using PyCharm's built-in Terminal pane). If the prompt shows `(venv)`, it is using the venv 
correctly. You can run `./manage.py` to verify that it correctly executes within the environment (it will list available 
commands if working correctly).
- If using PyCharm Professional (which has built-in Django support), you may additionally want to set up a default runner
environment using the "Add Configuration" button in the top toolbar. Select "Django Server", then "Create configuration", 
and enter "PRI" for the configuration name. You will now be able to start up a regular or debug local app server environment
using the buttons to the right of the configuration.

### Django Structure

Functionality in a Django project is organized into "apps" (modules) within the project. There are apps for `fleet`, 
`sales`, `backoffice`, and other directories which serve both as logical groupings of data models (tables), and to
represent sub-sites within the main site (such as the non-authenticated site root, the secure customer portal,
and the backoffice admin area). 

More apps can be created if desired to keep  functionality segregated. Note that each app you add (via 
`./manage.py startapp <app>`) needs to be added to `INSTALLED_APPS` in the settings in order for it to be recognized 
by Django.

Within an app, models (code representations of database tables, and all object-oriented code surrounding them) reside 
in `models.py`. All tables from the database should be described in a `models.py` file and registered in an `admin.py`
to be accessed via the standard Django admin for basic CRUD management (the backoffice site replaces most of this, but
it's often important to be able to manage the DB objects directly and without business logic).

Views (code which responds to a request with data which may be derived from models and either rendered to an HTML template or 
returned in structured JSON) live in `views.py`.

- There are a few different ways to build views; the old-style, function-based views, map more or less logically to the code we have
in the old app, whereas class-based views (for example `TemplateView`) are a more flexible and semantic approach. Look up both
in the Django docs.

- In either case, the views are where database queries are done (using the Django ORM language) and the results passed to the 
template using the context dict. The template contains only minimal flow-control logic and presentation-layer formatting tags.

- Ideally, view logic should be sparse as well; any methods or logic which processes or transforms data from the database
should reside in the models, i.e. as properties or model methods, which can then be invoked on the model instances returned
by the ORM. See `rentals.models.Vehicle` for an example model class demonstrating these approaches. (This follows the
model-view-controller principle of separation of concerns)

`urls.py` in each app directory defines the URL patterns which map to specific views. Each app's `urls.py` is conventionally 
mapped to a central `urls.py` which exists in the main `pri` directory, which also houses the project's `settings.py` and 
core entry point modules.

### env.yaml (local environment overrides)

As standard, Django takes its central settings from the `settings.py` file in the main project directory (i.e. `pri`). However,
I have added an `env.template.yaml` which you should use as a basis to create an `env.yaml` file in your local environment 
and in any additional env where the app will be deployed.

The localized `env.yaml` files allow us to set different values for settings such as `STATIC_ROOT` and other deployment-sensitive
variations depending on the environment, without maintaining separate versions of `settings.py` in code and having to switch
between them.

Any secrets/passwords/sensitive strings should be put in this yaml file; its contents will 
be merged into `settings.py` and made available to the app. The secrets can be stored separately from the main source repo
and shared directly between developers. In production deployments, `env.yaml` should be made readable only by the web user. 
This is how we keep secrets out of source control.  

For local development, your `env.yaml` minimally only needs to have:

```
SECRET_KEY: <secret_key>
```

If you want to use MySQL for local dev, add a `DATABASES` block following the example in `env.template.yaml`.

`env.yaml` and `env.template.yaml` should be kept as small as possible, containing only those override values necessary
for the localized environment. `settings.py` itself should have development-like settings for all its contents (so a developer
who does not create an `env.yaml` file can ideally get up and running with minimal changes). `env.template.yaml` should indicate
all settings that will need to be filled in for production.

### ORM and Database management: Migrations

It is important to drive and track all database changes in code rather than by directly manipulating the DB. This is the
purpose of migrations.

Each time you make a change to a model in the ORM  (i.e. in a `models.py` file), you should run `./manage.py makemigrations` 
to auto-generate migration files capturing the changes to the model, which translate to appropriate DB alterations for the 
DB backend in use for a given environment. Then you can run `./manage.py migrate` to apply the migrations. Be sure to add 
your newly created migration files to your git checkins.

The first task as part of building this application should be to capture the entire database schema in Django models, and 
make it reproducible using migrations (including data migrations if necessary to fill in fixtures and architectural data —
see https://docs.djangoproject.com/en/3.1/topics/migrations/#data-migrations)

### API

It is good practice, for a "hybrid" style website like this one (i.e. contains both server-rendered template views, and raw
JSON APIs for consumption by SPAs and mobile apps), to have a separate "api" app which segregates out the views that are used
in the latter pattern. It will prove useful to use the Django REST Framework (https://www.django-rest-framework.org) for 
producing this view logic, and for handling RESTful, CRUD type operations with a minimum of custom work. There will be some 
need for custom logic, mapping to the functions in the `porknbeans.cfc` library in the old codebase; for this you can use
DRF serializers by overriding the `create` method (or other methods corresponding to pertinent CRUD operations) as necessary.

### Static Files & Media

Static files (images, js, css, etc) necessary for the infrastructure of the site are kept in `static` directories scoped to each
app directory. When deploying, run `./manage.py collectstatic` to gather all these static assets into the `/static_root` directory
which should be mapped to an Apache alias which serves them straight through without reverse proxy processing.
https://docs.djangoproject.com/en/3.1/howto/static-files/

Media files (changeable site content) will live in the `media` directory.
https://docs.djangoproject.com/en/3.1/ref/settings/#media-root

Both these paths are controlled via the `settings.py` which is overridden locally in `env.yaml`.

### Templates

HTML templates are stored in `templates` directories scoped to each app, as well as in a global `templates` directory (to reduce
the redundancy in the path made necessary by having per-app templates -- long story). TL;DR: to refer to a file called `template.html`
in a view, put it in the main top-level `templates` directory.

### Django Admin

The standard Django Admin interface is available at http://127.0.0.1/spork/. This provides the ability to do basic database
manipulation, CRUD operations, and other standard maintenance tasks. Give yourself access to the admin by creating a superuser account 
for yourself, `./manage.py createsuperuser`

Each model you create will need to be registered via the `admin.py` module in the appropriate app, in order for it to appear
in the admin.

### Django Shell and direct DB access

Use `./manage.py shell` to invoke a Python REPL/shell which allows you to do direct code experimentation within the Django
environment. The `ipython` repl variant is installed which provides a richer shell with history processing and other useful features.

Use `./manage.py dbshell` to get a native CLI shell into the local database instance, whichever DB engine is being used.

### A note about multiple datasources

If you want to continue with the pattern of segregated "front" and "back" databases for low- and high-value data, it's 
possible to do that (https://docs.djangoproject.com/en/3.1/topics/db/multi-db/). However, I feel that this adds 
unnecessary complexity for dubious benefit. Especially if, as I would prefer and recommend, we aren't storing any real 
PII such as decryptable credit cards or passwords (these should just be handled via Stripe to avoid all PCI compliance
issues), and with the datasourcees kept in the same infrastructure so a breach would expose both, there doesn't really 
seem to be any value to keeping the data segregated in this way. The whole site should be SSL-only anyway, and individual
views and apps can be protected as needed via authentication classes or middleware, so the conceptual division between
"www" and "secure" seems moot, unless there's something I'm overlooking.

### Authentication and Permissions

There are a variety of ways to protect views in Django with appropriate authentication/authorization controls, depending
on need. Per the documentation, a view can be restricted to an authenticated user via a decorator or mixin, and permissions
enforced via the built-in permissions system: https://docs.djangoproject.com/en/3.1/topics/auth/default/

However, because adding boilerplate controls to a lot of views becomes cumbersome and repetitive, I have set up auth
and permissions via a middleware; see `pri.middleware`. These are classes through which all requests are passed and which
can be leveraged to affect the request depending on aspects of the user or resources being accessed; so the way I have
set it up, all views within the `backoffice` app require the user to be a) authenticated and b) an admin, or else it
raises a `PermissionDenied` error. This structure may or may not need to be extended as the project grows; what is
present now should serve as a baseline on which to build.

Note that all login pages go through the django-two-factor auth flow; if 2-factor is enabled for a user, it will 
challenge with one of several different auth methods (such as an TOTP code via an authenticator app). Two-factor is
opt-in and will not be required unless enabled (which it should be on all admin accounts).   

## Django documentation

https://docs.djangoproject.com/en/3.1/