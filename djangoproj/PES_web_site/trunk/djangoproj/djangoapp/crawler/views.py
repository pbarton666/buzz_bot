from django.http import HttpResponse
from djangoproj.djangoapp.models import Search
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django_dbRoutines import DatabaseMethods
import models

#instantiate the user from the authentication model
user = models.AuthUser()
dbMethods = DatabaseMethods()


def index(request):
    return HttpResponse("Hello, world. You're at the root dogma index.")

def displaySubSearches(request):
    '''
    This shows the secondary 'viewCriteria' search specs (it finds content bits belonging to
    a drill-down).  We'll upgrade later, but for now, it will allow the users to choose one of these
    to display the associated content.
    '''
    
    #this handles the display to the user
    if request.method == 'POST':
        pass
    else:
        formData = dbMethods.getViewCriteria()
    return render_to_response('displaySubSearches.html', {'form': formData})

def viewContentByCriteria(request, id, first = None, maxDisplayRows=None, backRequested=None):
    '''Displays content found for a secondary subSearch (i.e., a criteria set) against the whole database.
       Request object provides criteria id.  
       
       If this is an initial request for data (say from the nav button), we'll return the first chunk of content;
       ...if it's a secondary request from a POST, and it's from the "next" button, we'll use the same logic for the next chunk;
       ...but if it's a secondary request from a POST with the "back" button, we'll adjust our first/last parameters accordingly
    '''
    maxDisplayRows = maxDisplayRows or 100  #default page size   

    if request.method == 'POST':
        #read the post data to get the first value and find if back button pushed
        first = int(request.POST['first'])
        if request.POST.has_key('backRequested.x'):  
            first = max(0, first - maxDisplayRows)            
        else:
            first = first + maxDisplayRows         
        
    else:     
        first = 0
            
    formData = dbMethods.getContentAndUrlForCriteria(criteriaid = id, first = first, limit = first + maxDisplayRows -1)
    '''We'll pull the total record count out of the first record.  '''
    if len(formData) > 0:
        count = formData[0]['totalRecords']
    else: count = 0    
        
    #show the "back" button if there are any records before the current position
    showNext = False; showBack = False
    if first > 0:
        showBack = True
    if first + maxDisplayRows -1 < count:
        showNext = True
        
    #there's probably a more elegant way to do this, but the presenece or absence of a dict element is all I can
    #  get the django template parser to acknowledge
    if showBack and showNext:
        return render_to_response('content.html', {'form': formData, 'showBack': showBack, 'showNext': showNext, 'first': first})
    elif showBack:
        return render_to_response('content.html', {'form': formData, 'showBack': showBack, 'first': first})
    elif  showNext:
        return render_to_response('content.html', {'form': formData, 'showNext': showNext, 'first': first})    
    else:
        return render_to_response('content.html', {'form': formData,  'first': first})     
    

def editCriteria(request, id):
    #allows edit of a secondary subSearch (inherently on whole db).  Request object has criteria id
    from forms import editCriteria
    if request.method == 'POST':
        pass
    else:
        formData = dbMethods.getViewCriteria(id)
    return render_to_response('content.html', {'form': formData})


def reviewSearches(request):
    '''
    Allow users to look at searches already defined, delete, modify, or combine them
    '''
    userid =  user.id
    matchUser = False #for testing, we'll eventually only allow users to see their own searches
    if request.method == 'POST':
        #process user input
        pass
    else:
        '''
        prepare a dict of the information to be displayed on the form; this will include:
        - name: name
        - screenCriteriaInclude: secondary filtering include criteria
        - screenCriteriaExclude: secondary filtering exclude criteria
        - screenCriteriaAndOr
        - contentBits

        
        #render the form
        return render_to_response('reviewSearches.html')        
        pass
        '''

def testSearch(request):
    '''
    When this method is called it operates in one of a few ways:
      - called from code: sends a blank form to the user with (implicitly) a request.GET
      - returned from the user as valid:  grabs the data, processes it, then redirects control (prevents reloading/redispatching)
      - returned from user as invalid: sends the form back to the user
      
    The template 'testSearch_form.html' displays the form fields and an input button
    that posts the data when the user is done
    '''
    from django.shortcuts import render_to_response
    from forms import displaySearchForm
    #this handles the display to the user
    if request.method == 'POST':
        form = displaySearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            return HttpResponseRedirect('thanks')
    else:
        form = displaySearchForm()
    return render_to_response('testSearch.html', {'form': form})

def thanks(request):
    template = "thanks.html"
    return render_to_response(template)


def tables(request):
    template = 'table.html'
    mysearch = Search.objects.all()
    return render_to_response(template, {'outputDir':mysearch})


def header(request):
    return

def search(request):
    template = 'searches.html'
    try:
        mysearch = Search.objects.all()
        #output = ', '.join([str(p.id) for p in mysearch])
        output = mysearch
    except:
        raise Http404
    return render_to_response(template, {'outputDir':output, 
'table_title': "Search Table"})

def nonRational(request):
    template = 'nonRational.html'
    return render_to_response(template)

def marketResearch(request):
    template = 'marketResearch.html'
    return render_to_response(template)

#def serve(request, path, document_root, show_indexes=False):
