# Django settings for myproject project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Pat Barton', 'barton.pj@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'testdb'             # Or path to database file if using sqlite3.
DATABASE_USER = 'buzzbot'             # Not used with sqlite3.
DATABASE_PASSWORD = 'rootbak7'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/home/pat1/workspace/djangoproj/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = 'localhost:80/media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'dogma123'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'djangoproj.urls'

import os.path
#by convention we'll keep out templates in <project>/templates (the replace clause is for windows)
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin', 
    'djangoproj.djangoapp',
#    'djangoproj.pes',
)

#Logging directives
LOG_LEVEL_CRITICAL=50
LOG_LEVEL_ERROR=40
LOG_LEVEL_WARNING =30
LOG_LEVEL_INFO=20
LOG_LEVEL_DEBUG =10
LOG_LEVEL_NOTSET =0

#puts logs in a dir called (cleverly enough) logs
LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
LOG_NAME = "master.log"
LOG_LEVEL = LOG_LEVEL_DEBUG
