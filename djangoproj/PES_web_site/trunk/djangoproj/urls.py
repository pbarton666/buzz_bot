#this is django's default url configuration infrastructure
from django.conf.urls.defaults import *

#this imports the views
from djangoproj.djangoapp.views import *
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

#urlpatterns is mandatory here; we can refer to these by name later
urlpatterns = patterns('',
    url (r'^pes$', 'djangoproj.djangoapp.views.index', name = 'pes'),
    url (r'^searches$', 'djangoproj.djangoapp.views.search', name = 'searches'),
    url (r'^search$', 'djangoproj.djangoapp.views.search', name = 'search'),
    url (r'^base$', 'djangoproj.djangoapp.views.base', name = 'base'),
    url (r'^table$', 'djangoproj.djangoapp.views.tables', name = 'table'),
	url (r'^header$', 'djangoproj.djangoapp.views.header', name = 'header'),
	url (r'^testSearch$', 'djangoproj.djangoapp.views.testSearch', name = 'testSearch'),
	url (r'^thanks$', 'djangoproj.djangoapp.views.thanks', name = 'thanks'),
	url (r'^reviewSearches$', 'djangoproj.djangoapp.views.reviewSearches', name = 'reviewSearches'),
	url (r'^displaySubSearches$', 'djangoproj.djangoapp.views.displaySubSearches', name = 'displaySubSearches'),
	url (r'^viewContentByCriteria/(?P<id>\d+)$', 'djangoproj.djangoapp.views.viewContentByCriteria', name = 'viewContentByCriteria'),
	url (r'^editCriteria/(?P<id>\d+)$', 'djangoproj.djangoapp.views.editCriteria', name = 'editCriteria'),
	url (r'^nonRational$', 'djangoproj.djangoapp.views.nonRational', name = 'nonRational'),
	url (r'^marketResearch$', 'djangoproj.djangoapp.views.marketResearch', name = 'marketResearch'),
	
)
