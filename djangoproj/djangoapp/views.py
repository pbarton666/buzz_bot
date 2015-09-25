from django.http import HttpResponse
from djangoproj.djangoapp.models import *
from djangoproj.djangoapp.forms import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django_dbRoutines import DatabaseMethods
import time
import forms


#added for login demo
from django.contrib.auth import authenticate
from django.contrib.auth import login as authlogin
from django.contrib.auth.decorators import login_required

#logging
import logging
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

DELETE_WARNINGS_ON = 1  #flag to warn user of permanent deletions


#instantiate the user from the authentication model
user = AuthUser()
dbMethods = DatabaseMethods()

def reviewSites(request, searchid=None):
    
    redirect = '../editsearch/%s' %searchid  #always return to the edit search screen
    
    if request.method == "POST":
	#for now, the user can only view the urls, not edit them
	###TODO: fix this
	return HttpResponseRedirect(redirect)
    
    else: #request.method = "GET"
	urls = dbMethods.getUrlsObjectsForSearch(searchid = searchid)
	data = {'searchid': searchid, 'urls':urls}
	return render_to_response("viewUrls.html", data)

def uploadSites(request, searchid=None):
    
    redirect = '../editsearch/%s' %searchid  #always return to the edit search screen
    
    if request.method == "POST":
	#the user will have hit "update" or "return"; process only on update
	if request.POST['thisAction']=='update':
	    urls = request.POST['urls']
	    #raw urls come in with newline delimiters '\r\n' (at least from FF)
	    urls = urls.split('\r\n')
	    #add these to the URLs database
	    dbMethods.addUrlsFromList(searchid = searchid, urls = urls, source = 'user', depth = 0)

	return HttpResponseRedirect(redirect)
    
    else: #request.method = "GET"
	data = {'searchid': searchid}
	return render_to_response("upload.html", data)
	
    

def warnUser(request, **kwargs):
    '''This is a little unconventional, but I want a general-purpose warning for users
       that are potentially doing something disasterous, like wiping out all the contents
       of a db.  I've set up a really generally regex:  "warnUser" to capture any calls.
       
       All we do here is render it as a resonse object with data related to the searchid, 
       action requested, etc.  The template's form "action" parameter ensures control is returned
       to processSearchOptions, so we don't have to worry about separate "GET" and "POST" branches here.
    '''
     #if this this came from processSearchOptions
    if kwargs.has_key('data'): 
	data= kwargs['data']
	#parse out the incoming dictionary
	action = data['action']
	message = data['message']
	searchid = data['searchid']
	#create a dict to inject into the form, adding a flag to show user has been warned
	data = {'action':action, 'searchid': searchid, 'message': message, 'alreadyWarned': 1}
	#render the form
	return render_to_response('warnUser.html', data)  

def processSearchOptions(request, searchid):
    
    '''A POST request is generated in one of three ways:
       1.  Using a drop box in editsearch.html, the user can select different things to do with a search (edit, etc.)  
           When this happens, we'll update the search parameters.  Then, if the user has requested a potentially
	   dangerous action (deleting results, say), we'll issue a warning, else we'll honor the request.
       2.  We've issued a warning, and the user has responded (we know because 'userWarned' is one of the return
           parameters).  If the user OKs the action, we'll honor the request.  Otherwise, we'll refresh the 
	   editsearch screen..
       3.  User has updated the search parameters and hit the OK button.
       
       We'll parse out all potential actions at the top of this method and handle redirects at the bottom.  The
       actions (clear sites, etc.) are handled in the dbMethods module.
    '''
    
    if request.method == 'POST':
	#set some defaults
	alreadyWarned = False       #user has been warned of a dangerous operation
	warnOnThis = False          #used to flag a dangerous operation
	methodToInvoke = None       #used to identify processing step requested by user 
	redirectIdentified = False  #user action has been identified
	criteriaid = None           #presence of a criteriaID signals that the methodToInvoke will operate on secondary criteria
	action = 'thisAction'       #the form 'action' parameter (name of variable sent)
	actiondefault = 'select'    #the value of the 'no action' value from form controls

	#get the searchid
	searchid = request.POST['searchid']
	
	#the default redirect action will be this page (editsearch)
	redirect = "../editsearch/"+searchid
	
	#parse out the action the user has requested
	thisAction = pullActionFromPost(request.POST, action, actiondefault)
	
	actionList = request.POST.getlist('thisAction')
	if "update" in actionList: 
	    dbMethods.updateSearch(request.POST)  #updates the database w/ current search terms
	if 'return' in actionList:
	    redirect = "../searches"	
	
	
	#*****************************************************************************************    
	#* Parse out returns from the warning screen (warnUser.html)                             *
	#***************************************************************************************** 	
	
	#To test whether this method is invoked from warnUser (which allows user to hit 'Cancel' or 'OK'), check
	# if the request.POST object has 'Cancel' or 'alreadyWarned'.  We'll ensure these key words come only
	# from warnUser.
	
	if 'Cancel' in request.POST:
	    redirectIdentified = True		
	    	
	#Check if 'alreadyWarned' in key words.  If so the user has hit OK at the warning screen.
	if 'alreadyWarned' in request.POST:
	    alreadyWarned = True
    
	#*****************************************************************************************    
	#* Parse out returns from the general search management actions (editsearch.html)        *
	#*****************************************************************************************  
	
	# This block of logic handles user requests regarding the searches themselves.  The continuation of this block (below)
	#  handles requests regarding the secondary search criterial
	
	if not redirectIdentified:
	    #Parse out the request from drop box and pick redirect target.  The actionList will either be a single entity or a longer
	    #  set of all the values of drop boxes in the form.  In the latter case, we'll pick out the one that's not '--select--'.
	    
	    #'select...' (top option) chosen
	    if 'select' in thisAction:  
		pass    
	    
	    #user has asked to clear all content
	    elif thisAction == 'deleteSearchContent':
		message = "You've asked to delete all the content for this search.  This action can't be undone.  Are you sure?"
		warnOnThis = True
		methodToInvoke = dbMethods.deleteSearchContent
		
	    #user has asked to flush the URLS associated with this search	
	    elif thisAction == 'deleteSites':
		message = "You've asked to clear all the sites (URLs) for this search.  This action can't be undone.  Are you sure?"
		warnOnThis = True
		methodToInvoke = dbMethods.deleteUrlsForSearch
		
	    #user has asked to flush all the content and urls associated with this search	
	    elif thisAction == 'deleteSearchContentAndSites':
		message = "You've asked to delete all the content and sites (URLs) for this search.  This action can't be undone.  Are you sure?"
		warnOnThis = True
		methodToInvoke =dbMethods.deleteSearchContentAndSites
		
	    #user wants to upload his own URLs	
	    elif thisAction == 'uploadSites':
		redirect = '../uploadSites/'+ searchid   #upload more urls
		
	    #user wants to review the URL list	
	    elif thisAction == 'reviewSites':
		redirect = '../reviewSites/' + searchid  #review urls
		
	    #user wants to clean up the database (this is a temporary admin option)	
	    elif thisAction == 'cleanUpData/':
		redirect = '../cleaUpData/'+ searchid  #return to the editsearch screen
		methodToInvoke = cleanUpData
		
	    #user asked to revert changes to saved version
	    elif thisAction =='revert':
		redirect = '../editsearch/'+ searchid
	    
	#********************************************************************************************* 
	#User wants to do something with secondary search criteria if 'SearchCriteria' is the action *                             *
	#*********************************************************************************************		
	    
	    elif 'SearchCriteria' in thisAction:
		
		#get the criteriaId from the html (argument is something like 'delete/<criteriaId>')
		criteriaid = parseCriteriaID(thisAction)
		
		#the user has asked to delete the search criteria
		if 'delete' in thisAction:
		    warnOnThis=True		    
		    methodToInvoke =dbMethods.deleteCriteriaAndItsContent
		    message = "You've asked to delete this secondary search and any content already found.  Are you sure?"
		
	        #the user wants to view or edit (owners get to edit) the criteria
		elif 'edit' in thisAction:
		    redirect = '%s%s' %('../editCriteria/', criteriaid)
		    
	    #user wants to add a new criteria object - we'll add one then pass it off to edit 
	    elif 'new filter' in thisAction:
		criteriaid = dbMethods.addViewCriteria(searchid)		
		redirect = '%s%s' %('../editCriteria/', criteriaid)
	
	pass
    
	#*****************************************************************************************    
	#* Send the request off to the proper desination                                         *
	#*****************************************************************************************     
	
	#Except for the case where the user hit the "revert" button, we'll update the search
	#  terms.  If "revert" is hit, we'll update the editsearch page.	 	    
    
    	#if the warning flag is set, redirect to a warning screen; which will pass the local redirect (above) along
	if DELETE_WARNINGS_ON and warnOnThis and not alreadyWarned:
	    #pass along actions for the OK and cancel buttons on the warning page
	    data = {'action': thisAction, 'searchid':  searchid, 'criteriaid': criteriaid, 'message': message}	
	    #pass the request object to the warnUser routine	    
	    return render_to_response("warnUser.html", data)

	
	#...Otherwise, either we don't need a warning or it's already been issued and blown off.  We're ready to hand off control to
	#  a method what will act on either the Search object or the SearchCriteria object.
	else:  	    
	    if  methodToInvoke:
		#we'll invoke the method for some search id, unless a secondary criteria id has been set
		if criteriaid:
		    methodToInvoke(criteriaid)
		else:
		    methodToInvoke(searchid)
		    
	    #...then redirect to next view
	    return HttpResponseRedirect (redirect)
    

    else:  #we should never hit this point because we're only posting from editsearch
	pass
    
def editCriteria(request, criteriaid):
    #Allows edits to the secondary search criteria
    
    #set some defaults
    alreadyWarned = False       #user has been warned of a dangerous operation
    warnOnThis = False          #used to flag a dangerous operation
    methodToInvoke = None       #used to identify processing step requested by user 
    redirectIdentified = False  #user action has been identified   
    action = 'thisAction'       #the form 'action' parameter (name of variable sent)
    actiondefault = 'select'    #the value of the 'no action' value from form controls    

    if request.method == "POST":	
	#parse the criteriaid out of the posted page and fetch the associated object
	
	#To test whether this method is invoked from warnUser (which allows user to hit 'Cancel' or 'OK'), check
	# if the request.POST object has 'Cancel' or 'alreadyWarned'.  We'll ensure these key words come only
	# from warnUser.
	
	if 'Cancel' in request.POST:
	    redirectIdentified = True		
	    	
	#Check if 'alreadyWarned' in key words.  If so the user has hit OK at the warning screen.
	if 'alreadyWarned' in request.POST:
	    alreadyWarned = True	

	if not redirectIdentified:
	    #parse out the action the user has requested
	    thisAction = pullActionFromPost(request.POST, action, actiondefault)	
	    
	    criteriaid = request.POST['criteriaid']
	    criteria = dbMethods.getViewCriteriaById(criteriaid)
	    
	    #Django is a bit funky in that the related field isn't really a field value but an object representing the field in
	    #  the other table.  'criteria' is a SearchViewcriteria object; 'criteria.searchid' is a Search object; criteria.searchid_id is the 
	    #  value of the Search object's 'id' field.
	    searchid = criteria.searchid_id
	    
	    #always return to the edit search screen
	    redirect = '../editsearch/%s' %searchid 	
	    
	    #only process the content of the page if the user hit 'update'
	    if thisAction=='update':
		redirect = '../editsearch/%s' %searchid 
		#parse out the page contents
		if request.POST.has_key('andor'):
		    andor = 'and'
		else:
		    andor = 'or'
		if request.POST.has_key('ispublic'):
		    ispublic = True
		else:
		    ispublic = False
		include = request.POST['include'].strip()
		exclude = request.POST['exclude'].strip()
		title = request.POST['title'].strip()
		
		#gin up a dict to pass to the db routine
		updatedict = {'include': include, 'exclude': exclude, 'andor': andor, 
			      'ispublic': ispublic, 'title': title, 'searchid': searchid, 'criteriaid': criteriaid}
		#pass it along
		dbMethods.updateViewCriteria(updatedict)
	    
	    #user asked to revert changes to saved version
	    elif thisAction =='revert':
		redirect = '../editCriteria/%s' %criteriaid
		
	    #user asked to delete the content for this filter		
	    elif 'clearContent' in thisAction:
		warnOnThis=True
		#if the warning flag is set, redirect to a warning screen; which will pass the local redirect (above) along
		message = 'You have asked to delete all content for this filter.  Are you sure?'
		if DELETE_WARNINGS_ON and warnOnThis and not alreadyWarned:
		    #pass along actions for the OK and cancel buttons on the warning page
		    data = {'action': thisAction, 'criteriaid':  criteriaid, 'message': message}	
		    #pass the request object to the warnUser routine	    
		    return render_to_response("warnUser.html", data)	
		else:
		    dbMethods.deleteContentForCriteria(criteriaid)
		    redirect = '../editsearch/%s' %searchid

	return HttpResponseRedirect(redirect)
    
    else: #request.method = "GET"
	
	#grab a copy of the criteria object
	criteria = dbMethods.getViewCriteriaById(criteriaid)	
	search =criteria.searchid
	
	#convert search.ispublic from and/or to 1/0 for checkbox display (this doesn't affect the database)
	if criteria.andor == 'and':
	    criteria.andor = 1
	else:
	    criteria.andor = 0
	
	#determine whether this user owns the search (will determine editing options)
	isowner = False
	if request.user.id == search.userid:
	    isowner= True	
	    
	#figure out how many content bits we have
	contentcount=dbMethods.countContentForCriteria(criteriaid)
	
	data = {'criteria': criteria, 'isowner': isowner, 'contentcount': contentcount}
	return render_to_response("editcriteria.html", data)    
    
	

def parseCriteriaID(inputStr):
    #takes an input from the html in the form "<someString>/<someNumber>" and returns <someNumber>
    return inputStr[inputStr.find("/")+1:]

    
def pullActionFromPost(postObj, fieldName, defaultValue):
    #Returns a single action from a potentially long form.  Here's the deal:  Sometimes we have a lot of drop boxes on a form (one per
    #  filter criteria, say).  Most will have the default value '--select--' and one will have the user's choice ('update') say.  Django
    #  can return the values as a list.  Our job here is to grab the one the user picked.
        
    actionList = postObj.getlist(fieldName)
    thisAction = actionList[0] 
    if len(actionList) > 1:
	for a in actionList:
	    if not defaultValue in a:
		thisAction = a  
    return thisAction
    
def processManageSearches(request, searchid=None):
    '''This routine is a bit screwy because the searchid info is passed into the searches template
       as the value parameter of the drop boxes.  The options for Search 1 would include 'deletesearch/1'.
       This allows us to parse out both the action and the target from the user selection.
       
       To keep the logic consistent with the handler for the editsearch template (processSearchOptions),
       we'll split thisAction into componenets e.g. 'thisAction = deletesearch' and 'searchid = 1'
       When we get a return from warnUser, we'll use the searchid it passes via the request.POST object
       as request.POST['thisAction'] will no longer contain this info.  Clear as mud?
    '''
    #set some defaults
    alreadyWarned = False       #user has been warned of a dangerous operation
    warnOnThis = False          #used to flag a dangerous operation
    methodToInvoke = None       #used to identify processing step requested by user 
    redirectIdentified = False  #user action has been identified    
    thisAction = None
    
    if request.POST.has_key('thisAction'):
	
	#*****************************************************************************************    
	#* Parse out returns from the warning screen (warnUser.html)                             *
	#***************************************************************************************** 	
	
	#If (and only if) this routine got control from the warnUser form, 'Cancel' request.POST kwargs
	#  If this is the case, set the redirect to return the user to editsearch.
	
	if 'Cancel' in request.POST:
	    redirectIdentified = True		
	    	
	#Check if 'alreadyWarned' in key words.  If so, the user has hit OK at the warning screen.
	#  We'll take our action and search id parameters from this return
	if 'alreadyWarned' in request.POST:
	    alreadyWarned = True
	    searchid = request.POST['searchid']
	    thisAction = request.POST['thisAction']

	#*****************************************************************************************    
	#* Parse out returns from the general search management actions (searches.html)        *
	#***************************************************************************************** 
	#If we have not yet defined thisAction, we're processing the initial request from the 
	#  searches template; we'll need to parse the searchid and action.
	if not thisAction:
	    postedAction = request.POST['thisAction']
            #user chose the drop box header value, return control to /search
            if  'select' in postedAction:
                redirect = '/search'
		redirectIdentified = True
	    else:  #parse out the action from the searchid
		searchid = int(postedAction.split('/')[1])
		thisAction = postedAction.split('/')[0]
		redirect = '/%s/%i' %(thisAction, searchid)
		
		
	#handle the requests (just one option, deletesearch, for now)
	if thisAction == 'deletesearch':
	    message = "You've asked to delete an entire search and all its contents.  This action can't be undone.  Are you sure?"
	    warnOnThis = True
	    methodToInvoke = dbMethods.deleteSearch	
	    redirect = '/search'
	else:
	    pass #other options here
		
	#*****************************************************************************************    
	#* Send the request off to the proper desination                                         *
	#*****************************************************************************************     	 	    
    
    	#if the warning flag is set, redirect to a warning screen; which will pass the local redirect (above) along
	if DELETE_WARNINGS_ON and warnOnThis and not alreadyWarned:
	    #pass along actions for the OK and cancel buttons on the warning page
	    data = {'action': thisAction, 'searchid':  searchid, 'message': message}	
	    #pass the request object to the warnUser routine	    
	    return render_to_response("warnUser.html", data)
	
	else:  #either we don't need a warning, or it's already been issued so...
	    #...if we're asked to so something, do it ...
	    
	    if  methodToInvoke:
		methodToInvoke(searchid)
	    #...then redirect to next view
	    return HttpResponseRedirect (redirect)		


    #if the user just hit 'new' update the database and refresh
    if request.POST.has_key('new'): 
        searchid = addsearch(request)
        if searchid:                    
            data = dbMethods.getSearch(searchid)
            return render_to_response('editsearch.html', {'search':data, 'urlcount':0, 'contentcount':0})                             
                      
    
def addsearch(request):
    '''Here' we'll add a default search, remembering its id.  Then we'll update the request object to reflect the
       search id and pass it to the editsearch routine.  On background, the GET and POST methods of the request are
       a Django type 'QueryDict' which are dictionary-like objects.  They are normally immutable, but can be made
       mutable by using their copy() method.  Django allows us to append a dictionary.  One other note
       of interest, the QueryDict object can have multiple values for a single key; if so, QueryDict.getlist returns 
       all these values as a list and QueryDict['<key name>'] returns a single value.
    '''
    userid=request.user.id
    username = request.user.first_name
    #instansiate a new search for this user
    searchid = dbMethods.addSearch(userid=userid, name= 'new search '+time.strftime("%B %d %Y at %I:%m"))
    #make sure we got a searchid; if the database returned a null object (for whatever reason) politely redirect
    if searchid:
        #edit the request object
        request.POST = request.POST.copy()
        return searchid 
    else:
        logging.warn ("failed to add new search")
        return None
    

    
def editsearch(request, searchid):
    '''The POSTed form will have user settings for search terms and search-specific flags. In this case we'll set
       the search object parameters in the db and move on.
       
       ##TODO: add processing logic to weed out any funky escape characters inadvertently added by the user; 
       html escaping to eliminate SQL injection attacks is handled within the form by django.
'''        
    request.path = ''
    if request.method == 'POST': 
        #send the form contents to the db
        #r
        srch = dbMethods.getSearch(searchid)
        
        
##TODO:  can't we just grab these as a dict and pass them along?        
        if srch:
            ret =dbMethods.updateSearch(request.POST)
        #request.path = ""
        return HttpResponseRedirect("/search")
    
    
    else: #we have a GET request, so we'll retrieve and display the search requested
        
        search = dbMethods.getSearch(searchid)
	#convert search.ispublic from and/or to 1/0 for checkbox display (this doesn't affect the database)
	if search.andor == 'and':
	    search.andor = 1
	else:
	    search.andor = 0
        urlCount = dbMethods.getUrlCountForSearch(searchid)
        contentCount = dbMethods.getContentCountForSearch(searchid)
	
	#determine whether this user owns the search (will determine editing options)
	isowner = False
	if request.user.id == search.userid:
	    isowner= True
	    
	#load up information for view criteria related to this search
	viewCriteria = dbMethods.getParseCriteriaForSearch(searchid)['criteria']
	
        return render_to_response('editsearch.html', {'search':search, 'isowner': isowner, 'urlcount':urlCount, 
						      'contentcount': contentCount, 'viewCriteria': viewCriteria})
     
def content(request):
    if request.method == 'POST':
        pass
    else:
        pass
    return HttpResponseRedirect('searches')
 
def viewSecondaryFilters(request):
    if request.method == 'POST':
        pass
    else:
        pass
    return HttpResponseRedirect('searches') 
 
#a decorator is a set of canned methods applied to the method hat follows it
@login_required
def goodLogin(request):
    pass

def login(request):
    #Note this internal class is local to the logMein namespace
    def errorHandle(error):
        form = LoginForm()
        return render_to_response('login.html', {
            'error' : error,
            'form' : form,
        })
    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Uses the built in 
                    authlogin(request, user)
                    return HttpResponseRedirect('searches')
                else:
                    # Return a 'disabled account' error message
                    error = u'account disabled'
                    return errorHandle(error)
            else:
                # Return an 'invalid login' error message.
                error = u'sorry, invalid login - could you try again?'
                return errorHandle(error)
        else: 
            error = u'form is invalid'
            return errorHandle(error)		
    else:
        form = LoginForm() # An unbound form
        return render_to_response('buzzlogin.html', {
            'form': form,
        })


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
        formData = dbMethods.getViewCriteria(onlyPublic = True)
    return render_to_response('displaySubSearches.html', {'form': formData})

def viewContentByCriteria(request, id, first = None, maxDisplayRows=None, backRequested=None):
    '''Displays content found for a secondary subSearch (i.e., a criteria set) against the whole database.
       Request object provides criteria id.  

       If this is an initial request for data (say from the nav button), we'll return the first chunk of content;
       ...if it's a secondary request from a POST, and it's from the "next" button, we'll use the same logic for the next chunk;
       ...but if it's a secondary request from a POST with the "back" button, we'll adjust our first/last parameters accordingly
    '''
    maxDisplayRows = maxDisplayRows or 300  #default page size   

    if request.method == 'POST':
        #read the post data to get the first value and find if back button pushed
        first = int(request.POST['first'])
        if request.POST.has_key('backRequested.x'):  
            first = max(0, first - maxDisplayRows)            
        else:
            first = first + maxDisplayRows         

    else:     
        first = 0

    formData = dbMethods.getContentAndUrlForCriteria(criteriaid = id, first = first, limit = maxDisplayRows -1)
    '''We'll pull the total record count out of the first record.  '''
    if len(formData) > 0:
        count = formData[0]['totalRecords']
    else: count = 0    

    #show the "back" button if there are any records before the current position
    showNext = False; showBack = False
    if first > 0:
        showBack = True
    if first + maxDisplayRows -1 < count and count > 0:
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

'''
def editCriteria(request, id):
    #allows edit of a secondary subSearch (inherently on whole db).  Request object has criteria id
    from forms import editCriteria
    if request.method == 'POST':
        pass
    else:
        formData = dbMethods.getViewCriteria(id)
    return render_to_response('content.html', {'form': formData})
'''

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
    '''Returns all the searches specificed by this user, along with any public ones.  If the user
       is a guest, return public ones only.  The template looks for two objects: public searches and
       private ones.  "Public" is all public searches for a guest, and all searches not owned by the user
       but public if the user is logged in.
       '''
    
    ###TODO:  allow option for viewing 'within group' searches
    
    template = 'searches.html'
    #Get the user if from the auth object; 
    thisUserName = request.user.username or None
    thisUserNum= request.user.id or None
    
    #provide null objects as default values for the objects passed to the template
    publicSearches = None   
    mySearches = None
    
    #grab the right flavor of public searches
    if thisUserName =='guest':
        try:
            publicSearches = dbMethods.getSearchesPublicOnly()
        except:
            logging.info('no searches available for guest')
    else:
        try:
            publicSearches=dbMethods.getSearchesPublicOnlyNotUsers(thisUserNum)
        except:
            logging.warn('*** no public searches available to registred user - something broke')            

            pass
        
    if thisUserNum:   
        try:
            mySearches = dbMethods.getSearchesByUser(thisUserNum)
        except:    
            logging.info('no searches available for user %i' %thisUserNum)
                      
    try:
        #set a null templateData object
        templateData = {'null': None}
        #reset the templateData object based on what we've retrieved
        if mySearches and publicSearches:
                templateData = {'mySearches':mySearches, 'publicSearches':publicSearches}
        if mySearches and not publicSearches:
                templateData = {'mySearches':mySearches}  
        if not mySearches and publicSearches:
                templateData = {'publicSearches':publicSearches}                    
        return render_to_response(template, templateData)
    except:
        raise 

def nonRational(request):
    template = 'nonRational.html'
    return render_to_response(template)

def marketResearch(request):
    template = 'marketResearch.html'
    return render_to_response(template)

#def serve(request, path, document_root, show_indexes=False):
def set_logger():
    #Our friend the logger. Sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
    #  at the top of this module).
    LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
    log_filename = LOGDIR + '/' + LOG_NAME
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_filename,
                        filemode='w')
    
if __name__ =='__main__':    
    set_logger()