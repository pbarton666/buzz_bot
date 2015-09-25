#this is django's default url configuration infrastructure
from django.conf.urls.defaults import *

#this imports the views
from djangoproj.djangoapp.views import *
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

#urlpatterns is mandatory here; we can refer to these by name later.

'''NB, the REs don't act as expected (they use Python's re module).  For instance Django's urlresolver uses the
   string:  ^login(.htm)?(.html)?$  to successfully identify the target to views.py::login.  However its call to
   Python's re module results in the return of two 'groups' [the re module's interpretation of '(.htm)' and '(.html)']
   These are returned as the tuple (None, None) which the urlresolver incorrectly interprets these as two positional 
   arguments to views.py::login.  I'm sure my regex could be improved but for now, we'll use simple separate
   url patterns.  
'''   
urlpatterns = patterns('',
	url (r'^login$', 'djangoproj.djangoapp.views.login', name = 'login'),
	url (r'^login.html$', 'djangoproj.djangoapp.views.login', name = 'login'),
    url (r'^pes$', 'djangoproj.djangoapp.views.index', name = 'pes'),

    url (r'^base$', 'djangoproj.djangoapp.views.base', name = 'base'),
    url (r'^table$', 'djangoproj.djangoapp.views.tables', name = 'table'),
	url (r'^header$', 'djangoproj.djangoapp.views.header', name = 'header'),
	url (r'^testSearch$', 'djangoproj.djangoapp.views.testSearch', name = 'testSearch'),
	url (r'^thanks$', 'djangoproj.djangoapp.views.thanks', name = 'thanks'),
	url (r'^reviewSearches$', 'djangoproj.djangoapp.views.reviewSearches', name = 'reviewSearches'),
	url (r'^displaySubSearches$', 'djangoproj.djangoapp.views.displaySubSearches', name = 'displaySubSearches'),
	url (r'^viewContentByCriteria/(?P<id>\d+)$', 'djangoproj.djangoapp.views.viewContentByCriteria', name = 'viewContentByCriteria'),

	url (r'^nonRational$', 'djangoproj.djangoapp.views.nonRational', name = 'nonRational'),
	url (r'^marketResearch$', 'djangoproj.djangoapp.views.marketResearch', name = 'marketResearch'),
	url (r'^addurls$', 'djangoproj.djangoapp.views.addurls', name = 'addurls'),
	url (r'^viewurls$', 'djangoproj.djangoapp.views.viewurls', name = 'viewurls'),

	url (r'^viewSecondaryFilters/(?P<urlid>\d+)$', 'djangoproj.djangoapp.views.viewSecondaryFilters', name = 'viewSecondaryFilters'),
	url (r'^content/(\d+)$', 'djangoproj.djangoapp.views.content', name = 'content'),
	url (r'^processManageSearches$', 'djangoproj.djangoapp.views.processManageSearches', name = 'processManageSearches'),
	
	url (r'^deletesearch/(\d+)$', 'djangoproj.djangoapp.views.deletesearch', name = 'deletesearch'),
	url (r'^addsearch$', 'djangoproj.djangoapp.views.addsearch', name = 'addsearch'),
	url (r'^processEditSearch$', 'djangoproj.djangoapp.views.processEditSearch', name = 'processEditSearch'),
	url (r'^processSearchOptions/(\d+)$', 'djangoproj.djangoapp.views.processSearchOptions', name = 'processSearchOptions'),
	
	
	url (r'^clearSearchContent/(\d+)$', 'djangoproj.djangoapp.views.clearSearchContent', name = 'clearSearchContent'),
	url (r'^clearSearchContentAndSites/(\d+)$', 'djangoproj.djangoapp.views.clearSearchContentAndSites', name = 'clearSearchContentAndSites'),
	url (r'^clearSites/(\d+)$', 'djangoproj.djangoapp.views.clearSites', name = 'clearSites'),
	url (r'^uploadSites/(\d+)$', 'djangoproj.djangoapp.views.uploadSites', name = 'uploadSites'),
	url (r'^reviewSites/(\d+)$', 'djangoproj.djangoapp.views.reviewSites', name = 'reviewSites'),
	url (r'^reviewSites/(\d+)/$', 'djangoproj.djangoapp.views.reviewSites', name = 'reviewSites'),
	url (r'^cleanUpData/(\d+)$', 'djangoproj.djangoapp.views.cleanUpData', name = 'cleanUpData'),
	
	url (r'^searches$', 'djangoproj.djangoapp.views.search', name = 'searches'),
	url (r'^editsearch/processSearchOptions/(\d+)$', 'djangoproj.djangoapp.views.processSearchOptions', name = 'processSearchOptions'),	
	url (r'^editsearch/processSearchOptions/editsearch/(\d+)$', 'djangoproj.djangoapp.views.editsearch', name = 'editsearch'),
	url (r'^editsearch/processManageSearches$', 'djangoproj.djangoapp.views.processManageSearches', name = 'processManageSearches'),	
	url (r'^editsearch/(\d+)$', 'djangoproj.djangoapp.views.editsearch', name = 'editsearch'),
	url (r'^editsearch/(\d+)/$', 'djangoproj.djangoapp.views.editsearch', name = 'editsearch'),
	url (r'^search$', 'djangoproj.djangoapp.views.search', name = 'search'),
	
	url (r'warnUser', 'djangoproj.djangoapp.views.warnUser', name = 'warnUser')  ,
	
	url (r'^editCriteria/(\d+)$', 'djangoproj.djangoapp.views.editCriteria', name = 'editCriteria'),

	
)












