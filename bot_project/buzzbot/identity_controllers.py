import turbogears as tg
from turbogears import controllers, expose, flash, identity, widgets, validate, redirect, validators, error_handler
from turbogears import *
from cherrypy import request, response
from datetime import datetime
import time
from string import join
import random
from sqlobject.sqlbuilder import *
import model
from model import *
from string import join
import random

# from buzzbot import json
import logging
log = logging.getLogger("buzzbot.controllers")
    
   #create a widget list for fields in the search specification form
class SearchFields(widgets.WidgetsList):
    id = widgets.HiddenField()
    name=widgets.TextField(label= "Name:")    
    description = widgets.TextField(label="Description:")
    #client_id =  widgets.TextField(label="Client ID:")
    targetword = widgets.TextField(label="Target word:")
    searchstring = widgets.TextField(label="Find content containing:")
    maxurls = widgets.TextField(label="Max. URLs to Search:")
    maxcontent = widgets.TextField(label="Max. content blocks to find:")
    eliminationwords = widgets.TextField(label="...but not containing:")

#...these will be displayed on a custom form that instansiates the TableForm widget
class SearchForm(widgets.TableForm):
    template= "buzzbot.templates.searchTemplate"    
searchFormInstance = SearchForm(fields = SearchFields.declared_widgets, 
                            action = "Post",
                            submit_text="Save")
class tableFormTemplate(widgets.TableForm):
    pass

#set up a widget list and form for the verify search delete screen
class verifyDeleteFields(widgets.WidgetsList):
    id = widgets.HiddenField()
    name = widgets.TextField()
    cancel = widgets.Button()
verifyDeleteFormInstance = widgets.TableForm(fields = verifyDeleteFields.declared_widgets, 
                               action = "Post", submit_text="OK")  

class checkBoxList(widgets.WidgetsList):
    pass
            
class Root(controllers.RootController):
    @expose(template="buzzbot.templates.welcome")
    @identity.require(identity.not_anonymous())
    def index(self):
        import time
        log.debug("Happy TurboGears Controller Responding For Duty")
        flash("Your application is now running")
        testme()
        return dict(now=time.ctime())

    @expose(template="buzzbot.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted() \
                and not identity.get_identity_errors():
            raise redirect(tg.url(forward_url or previous_url or '/', kw))

        forward_url = None
        previous_url = request.path
        msg = "You can use guest/guest if you don't yet have a login."
        if identity.was_login_attempted():
            msg = "The credentials you supplied were not correct or did not grant access to this resource."
        elif identity.get_identity_errors():
            msg = "You must provide your credentials before accessing this resource."
        else:
            msg = "Please log in."
            forward_url = request.headers.get("Referer", "/")
        forward_url="/buildLP"
        response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=request.params, forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect
    
    @expose(template="buzzbot.templates.edit_search_form")  
    #deprecated, but keep for use as template
    def testProjectFields1(self):    
        submit_action = "/saveProjectFields/"
        #set up some values to send to the form
        b=model.Search.select()
        someb = b[0]
        #inject these values into the form created from the ProjectFields widget list
        return dict(form=searchFormInstance, values = someb, action = submit_action)    
    
    
    @expose()
    #deprecated, but keep for use as template
    def saveProjectFields(self, **kwargs):
        #elements of the form have same names as the class attributes, so we can
        #  use them to set the database parameters.  
        #here, we're updating an existing search
        parameter_1 = 10
        if parameter_1 <> '0':  
            b= Search.get(parameter_1)
            b.set(**kwargs)
        else:
            #this command tells the Search object to add it.
            return "Search = (" + join(["%s : %s " %item for item in kwargs.iteritems()])
        raise redirect("/index")

    @expose(template="buzzbot.templates.viewContent")
    def viewContent(self,searchNum):
        conn = Content._connection
        #change this statement to = searchNum
        #sqlstmt = "SELECT * from content WHERE search_id > " + str(searchNum)
        b=Content.select()
        return dict(cont = b)
    
    @expose(template="buzzbot.templates.verifyDeleteSearch") 
    def verifyDeleteSearch(self, searchNum):
        #calls up a page to verify deletion of a search
        b = Search.get(searchNum)
        submit_action = "/deleteSearch/%s" %searchNum
        #inject these values into the form created from the verifyDeleteFields widget list   
        return dict(form=verifyDeleteFormInstance, values = b, action = submit_action)
        #to do: verify syntax here; write up a short data in/#aout piece for notes;
        #       do pop-up window for confirmation# ensure foreign keys work
    def deleteSearch(self, number):
        #actually deletes a search after user confirmation
        if int(number) >0:  #if number is less than zero, user cancelled action
            Search.delete(int(number))
        #returns user to main search view page
        raise redirect("/viewSearches/" + str(random.randint(1,10000)))
    
    @expose(template="buzzbot.templates.verifyDeleteLP") 
    def verifyDeleteLP(self, LPid):
        #calls up a page to verify deletion of a search
        b = Search.get(LPid)
        submit_action = "/deleteLP/%s" %LPid
        #inject these values into the form created from the verifyDeleteFields widget list   
        return dict(form=verifyDeleteFormInstance, values = b, action = submit_action)
        #to do: verify syntax here; write up a short data in/#aout piece for notes;
        #       do pop-up window for confirmation# ensure foreign keys work            
    
    def deleteLP(self, number):
        #actually deletes a search after user confirmation
        if int(number) >0:  #if number is less than zero, user cancelled action
            Listeningpost.delete(int(number))
        #returns user to main search view page
        raise redirect("/viewLPs/" + str(random.randint(1,10000)))    
    
    #lists all the searches made by this user, those saved by others in the same group, and those
    #  saved as client-worthy (by an admin)
    
    @expose(template="buzzbot.templates.viewSearches")   
    def viewSearches(self):
        #figure out who this user is and where he belongs
        thisID = identity.current.identity()
        thisUser = thisID.user_id
        thisUserGroup = thisID.groups
        #grab all the searches - this is a bit inefficient, but we won't have millions for a while
        searches = model.Search.select()
        searchesToDisplay = []  #an array of search objects to pass the the controller
        editURL = []  #  ...and a parallel array that flags that editing is allowed
        deleteURL =[] #  ...and one to signal that deletion is allowed 
        allUsers = User.select()
        
        #there's probably a more efficient way to do this, but this puts user's own searches on top
        for s in searches:
            if s.userid == thisUser:  #give the user full run of his own searches
                searchesToDisplay.append(s)
                editURL.append("/editsearch/" + str(s.id) + "?owner")
                deleteURL.append("/verifyDeleteSearch/" + str(s.id))
        
        #if the search begins to someone else and it's public consider adding it
        for s in searches:
            if s.userid <> thisUser and s.is_public:               
                ownerSearchObj = User.selectBy(s.userid)
                thisOwner = ownerSearchObj[0]
                thisOwnerGroup = thisOwner.groups

                if thisOwnerGroup == thisUserGroup:       
                    searchesToDisplay.append(s)
                    editURL.append("/editsearch/" + str(s.id)+ "?nonOwner")
                    deleteURL.append("")
                    
        #now find client-worthy searches (perhaps added by an admin) 
        for s in searches:
            if s.is_client_worthy:
                #screen out searches we've already added
                addMe=True
                for d in searchesToDisplay:
                    if d.id == s.id:
                        addMe=False
                if addMe:        
                    searchesToDisplay.append(s)
                    editURL.append("/editsearch/" + str(s.id)+ "?built_in")
                    deleteURL.append("") 
                        
        #create a widgetList to pass in; each will be named after the search it represents
        widgetList = widgets.WidgetsList()   #a true widgetsList object
        wNameList=[]                         #a list of the widget names
        for s in searchesToDisplay:
            #for testing, if it has an even number check the box
            if s.id%2 ==1:   #note: % is the modulus operator:
                mydefault = True  #note: this will not take a 1 in place of true
            else:
                mydefault = False
            wName = "ck_" + str(s.id)
            #w = widgets.CheckBox(name = wName, default = mydefault, validators=validators.Bool)
            w = widgets.CheckBox(name = wName, default = mydefault)
            #for some reason the default value doesn't stick unless we specify it separately
            w.default = mydefault
            widgetList.append(w)
            wNameList.append(wName)
         
        #prepare the objects for display; this instansiates a TableForm widget, passing in our check boxes
        myFormWidget = widgets.TableForm(fields = widgetList,
                                         method = "post",
                                         submit_text = "OK",
                                         name = "formName"
                                     )
        #this directs the returned form to the processSearchInput method          
        submit_action="/processSearchInput"

        return dict(form=myFormWidget, searches=searchesToDisplay, editlink = editURL, 
                      deletelink = deleteURL, action = submit_action)

    @expose()
    def processSearchInput(self, **kwargs):
        #the return is a tuple of (key, value) tuples for all the checked boxes, something like:
        #  {'ck_13': u'on',  'ck_11": u'on'}
        args = kwargs.items()
        searchOn=[]
        for a in args:
            boxName, state = args[a]          #parse the tuple
            searchOn.append(int(boxname[3:])) #strip the integer from the name
        #now we have an array of integers indicating which searches go with this LP
        #so...delete existing LP-search pairs
        a=1
        #...and add the current ones
        a=0
        return(dict[a])
        
        #Controller to allow the user to edit the search parameters.  Our named
        #  parameter_1 is the search number.  If its value is 0 (a new search), we'll grab a null row
        #  which is conveniently populated with default values.  This requires manual specification
        #  of the search in the db.  If this hasn't been set up, the form comes up blank.

 #lists all the Listening Posts owned by this user, those saved by others in the same group, and those
    #  saved as client-worthy (by an admin)
    @expose(template="buzzbot.templates.viewLPs")   
    def viewLPs(self):
        #figure out who this user is and where he belongs
        thisID = identity.current.identity()
        thisUser = thisID.user_id
        thisUserGroup = thisID.groups
        #grab all the searches - this is a bit inefficient, but we won't have millions for a while
        lps = model.Listeningpost.select()
        lpsToDisplay = []  #an array of search objects to pass the the controller
        editURL = []  #  ...and a parallel array that flags that editing is allowed
        deleteURL =[] #  ...and one to signal that deletion is allowed 
        allUsers = User.select()
        
        #there's probably a more efficient way to do this, but this puts user's own searches on top
        for s in lps:
            if s.userid == thisUser:  #give the user full run of his own searches
                lpToDisplay.append(s)
                editURL.append("/editsearch/" + str(s.id) + "?owner")
                deleteURL.append("/verifyDeleteLP/" + str(s.id))
        
        #if the search begins to someone else and it's public consider adding it
        for s in lps:
            if s.userid <> thisUser and s.is_public:               
                ownerSearchObj = User.selectBy(s.userid)
                thisOwner = ownerSearchObj[0]
                thisOwnerGroup = thisOwner.groups

                if thisOwnerGroup == thisUserGroup:       
                    lpsToDisplay.append(s)
                    editURL.append("/editLP/" + str(s.id)+ "?nonOwner")
                    deleteURL.append("")
                    
        #now find client-worthy searches (perhaps added by an admin) 
        for s in lps:
            if s.is_client_worthy:
                #screen out searches we've already added
                addMe=True
                for d in lpsToDisplay:
                    if d.id == s.id:
                        addMe=False
                if addMe:        
                    lpsToDisplay.append(s)
                    editURL.append("/editLP/" + str(s.id)+ "?admin")
                    deleteURL.append("") 
                        
        #create a widgetList to pass in; each will be named after the search it represents
        widgetList = widgets.WidgetsList()   #a true widgetsList object
        wNameList=[]                         #a list of the widget names
        for s in lpsToDisplay:
            #for testing, if it has an even number check the box
            if s.id%2 ==1:   #note: % is the modulus operator:
                mydefault = True  #note: this will not take a 1 in place of true
            else:
                mydefault = False
            wName = "ck_" + str(s.id)
            #w = widgets.CheckBox(name = wName, default = mydefault, validators=validators.Bool)
            w = widgets.CheckBox(name = wName, default = mydefault)
            #for some reason the default value doesn't stick unless we specify it separately
            w.default = mydefault
            widgetList.append(w)
            wNameList.append(wName)
         
        #prepare the objects for display; this instansiates a TableForm widget, passing in our check boxes
        myFormWidget = widgets.TableForm(fields = widgetList,
                                         method = "post",
                                         submit_text = "OK",
                                         name = "formName"
                                     )
        #this directs the returned form to the processSearchInput method          
        submit_action="/processSearchInput"

        return dict(form=myFormWidget, searches=searchesToDisplay, editlink = editURL, 
                      deletelink = deleteURL, action = submit_action)        
        
        
        
        @expose(template="buzzbot.templates.edit_search_form")
        def editsearch(self, parameter_1, tg_errors=None):
            try:
                submit_action = "/save_searchedit/%s" %parameter_1
                b = model.Search.get(int(parameter_1))      
            except:
                b = []
            return dict(form=edit_search_form, values = b, action = submit_action)
    
        #Process the user input here.  Elements of the form have the same names as the
        #  class attributes (i.e., database columns) so we can just pass the kwargs array
        #  to the database management routines (SQLObject)
        @expose()
        @error_handler(edit_search_form)
        @validate(form= edit_search_form)
        def save_searchedit(self, parameter_1, **kwargs): 
            #Form field parameters are strings, but some of the database fields are ints so
            #  we'll need to convert them.  This is a bit ugly but it works
            items = kwargs.items()  #this gets an dict array of (key, value) tuples
            for thisItem in items:
                k, v = thisItem #parse the tuple
                try: 
                    thisValueAsNumber = int(v)      #if this doesn't raise an error, the field is a number
                    kwargs[k]=thisValueAsNumber     #update the dict by assigning a new value to the key 
                except:    
                    pass     #if we have raised an error, we have text and will leave it alone
            #now we'll inject the data into the database.      
            if parameter_1 <> '0':  #this updates an existing record
                b= Search.get(int(parameter_1))
                b.set(**kwargs)
            else:
                #we have a new entry, and we'll let the database autoindex its id; this passes in
                #  a dict structure of form elements.  NB all db columns must be spec'd in widgetList.
                model.Search(**kwargs)
            #this brings control back to the viewSearches screen w/ a random number to ensure refresh
            raise redirect("/buildLP/" + str(random.randint(1,10000))) 
    
    def fixDB(self):
        mydata = model.Content.select()
        for d in mydata:
            d.set(user_id=1)
            d.set(search_id=1)
     