# Standard libraries
from datetime import datetime
from string import join
from urlparse import urlsplit
import Queue
import random
import time

# TurboGears
from cherrypy import request, response
from sqlobject.sqlbuilder import *
from turbogears import *
from turbogears.identity import *
from turbogears.validators import Int
from turbogears.widgets import *
from turbogears.widgets.forms import *
import turbogears as tg
mode = "db" #this sets mode for operation; db is database only

# Logging
import logging
log = logging.getLogger("buzzbot.controllers")

# Local
from buzzbot import *
from buzzbot.model import *

myBotRoutines = bot.BotRoutines()

GUESTID=3

class myTableForm(widgets.TableForm):
    #this subclasses the TableForm widget to provide a value_for method
    #value is the dictionary of values injected into the form
    def value_for(self, item, value):
        return value.get(item.name)
    def params_for(self, item, value):
        return item.params
    #this method will display a field by name
    def getfld(self, name, fields):
        #find the field matching the name; we'll let it fail silently on a typo
        found = False
        for f in fields:
            try:
                if f.name==name:
                    myfield = f
                    found=True
            except:
                pass
        return f
            

class LPFields(widgets.WidgetsList):
    #the fields that appear on the 'edit_lp' form.  If we add more, be sure to update methods
    #  save_lp and save_lp_copy to make sure the input is captured
    id = widgets.HiddenField()
    lpid = widgets.HiddenField()
    userid = widgets.HiddenField()
    name=widgets.TextField(label= "Name:")    
    #UNUSED# description = widgets.TextField(label="Description:",width=200)
    description = widgets.TextField(label="Description:")
    targetword = TextField(label= "Target word:")
    is_client_worthy = widgets.CheckBox(label="Share with the world?")
    is_public = widgets.CheckBox(label="Share with my group?")
    update_nightly=widgets.CheckBox(label = "Update nightly?")
    extra_lpid=widgets.HiddenField()
    icamefrom = widgets.HiddenField()
    
class LPForm(myTableForm):
    template="buzzbot.templates.edit_lp"
#global instance of LPForm
edit_lp_form = LPForm(fields = LPFields.declared_widgets,
             action = "Post",
             submit_text="New")
class ContentFormFields (widgets.WidgetsList):
    userid = widgets.HiddenField()
    lpid = widgets.HiddenField()
    searchid = widgets.HiddenField()
    status= widgets.HiddenField()
    start= widgets.HiddenField()
    step= widgets.HiddenField()
    returntopage = widgets.HiddenField()
    lastbtn = widgets.HiddenField()
    nextbtn = widgets.HiddenField()
    icamefrom = widgets.HiddenField()  
class ContentForm(myTableForm):
    #try adding a fields component with an arbitrary hidden field...
    template = "buzzbot.templates.view_content"  
content_form = ContentForm(action = "Post",fields = ContentFormFields.declared_widgets)

class UrlFormFields(widgets.WidgetsList):
    userid = widgets.HiddenField()
    lpid = widgets.HiddenField()
    searchid = widgets.HiddenField()
    status= widgets.HiddenField()
    start= widgets.HiddenField()
    step= widgets.HiddenField()
    returntopage = widgets.HiddenField()
    lastbtn = widgets.HiddenField()
    nextbtn = widgets.HiddenField()
    icamefrom = widgets.HiddenField()
    deleteexisting = widgets.CheckBox(label="Delete Existing?", default = False)
    #UNUSED# rawurls = widgets.TextArea(width=500, rows=20, cols=50)
    rawurls = widgets.TextArea(rows=20, cols=50)
class URLForm(myTableForm):
    #try adding a fields component with an arbitrary hidden field...
    template = "buzzbot.templates.view_urls"  
url_form = URLForm(action = "Post",fields = UrlFormFields.declared_widgets)

   #create a widget list for fields in the search specification form
class SearchFields(widgets.WidgetsList):
    #the variable names reflect the column names in the database
    # they also are the names of the widgets in widget list for this class 
    #  i.e., EditSearches.declared_widgets
    #
    id = widgets.HiddenField()
    #UNUSED# name = widgets.TextField(label = "Name:", cols=40)
    name = widgets.TextField(label = "Name:")
    description = widgets.TextArea(label = "Description:",  rows=2, cols=40)
    targetword = widgets.TextField(label = "Product/Company:")
    searchstring=  widgets.TextArea(label = "Search for:",  rows=2, cols=40)        
    #UNUSED# eliminationwords = widgets.TextArea(label = "...except content that contains:", width=150, rows=2, cols=40)
    eliminationwords = widgets.TextArea(label = "...except content that contains:", rows=2, cols=40)
    maxurls=widgets.TextField(label = "Max URLs:")
    maxcontent= widgets.TextField(label = "Max content:")   
    userid= widgets.HiddenField()    
    datelastsearched= widgets.HiddenField()   
    urlsearchfor=widgets.TextArea(label="Find URLs containing:",  rows=2, cols=40)
    urleliminate=widgets.TextArea(label="...except those that contain:",  rows=2, cols=40)
    isrecursive=widgets.CheckBox(label="Recursive search?", default = False)
    is_client_worthy = widgets.CheckBox(label="Share with the world?", default = False)
    is_public = widgets.CheckBox(label="Share with my group?", default = False)
    freezeurllist=widgets.CheckBox(label="Freeze URLs?", default = True)
    #these aren't part of the database, but are part of the form; we'll
    #encode their names so we can catch them later
    extra_deleteExisting=widgets.CheckBox(label="Delete URLs?", default = True)
    extra_lpid=widgets.HiddenField()
    extra_clientid= widgets.HiddenField() 
    extra_searchid = widgets.HiddenField()
    status = widgets.HiddenField()
    icamefrom=widgets.HiddenField()

class SearchForm(myTableForm):
    template="buzzbot.templates.edit_search_form"
    
#global instance of SearchForm
search_form = SearchForm(fields = SearchFields.declared_widgets,
             action = "Post",
             submit_text="New")

#set up a widget list and form for the verify search delete screen
class verifyDeleteLPFields(widgets.WidgetsList):
    id = widgets.HiddenField()
    name = widgets.TextField()
    cancel = widgets.Button()
    status = widgets.HiddenField()
    lpid = widgets.HiddenField()
    
class VerifyDeleteLPForm(myTableForm):   
    template="buzzbot.templates.verify_delete_lp"
verifyDeleteLPForm = VerifyDeleteLPForm(fields = verifyDeleteLPFields.declared_widgets, 
                               action = "delete_lp")

class adminFields(widgets.WidgetsList):
    technorati = widgets.CheckBox(label="Technorati", default = True)
    livejournal = widgets.CheckBox(label="LiveJournal", default = False)
    alexa = widgets.CheckBox(label="Alexa", default = False)
    xanga = widgets.CheckBox(label="Xanga", default = False)
    myspace = widgets.CheckBox(label="MySpace", default = False)
    aol = widgets.CheckBox(label="AOL", default = False)
    skyblog = widgets.CheckBox(label="SkyBlog", default = False)
    
class AdminForm(myTableForm):
    template = "buzzbot.templates.admin"
adminForm = AdminForm(fields = adminFields.declared_widgets, action = "runBackground")    

class verifyDeleteSearchFields(widgets.WidgetsList):
    id = widgets.HiddenField()
    name = widgets.TextField()
    cancel = widgets.Button()
    status = widgets.HiddenField()
    lpid = widgets.HiddenField()
    
class VerifyDeleteSearchForm(myTableForm):   
    template="buzzbot.templates.verify_delete_search"
verifyDeleteSearchForm = VerifyDeleteLPForm(fields = verifyDeleteSearchFields.declared_widgets, 
                               action = "delete_search")  


class checkBoxList(widgets.WidgetsList):
    pass

#month number to name array
months = ['','Jan','Feb','Mar','Apr','May','Jun', 'Jul', 'Aug', 'Spt', 'Oct', 'Nov', 'Dec' ]

#utility function for turning unicode to string (needed for search strings)
#  assumes either an integer or string; if division not supported assume string
def uniToStr(self, obj):
    for o in obj:
        try: int(o)/1
        except: o = str(o)    
    return(obj)   

def setUser(thisid):
    user =User.get(thisid)
    visit_key=tg.visit.current().key
    #VisitIdentity = tg.identity.soprovider.TG_VisitIdentity
    IdentityObject = tg.identity.soprovider.SqlObjectIdentity
    try:
        link =VisitIdentity.selectBy(visit_key)
    except :
        link = None
    if not link:
        link =VisitIdentity(visit_key=visit_key, user_id=user.id)
    else:
        link.user_id =user.id
    user_identity = IdentityObject(visit_key)
    identity.set_current_identity(user_identity)


class Root(controllers.RootController):
    @expose(template="buzzbot.templates.welcome")
    def index(self):
        raise redirect("/login")

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
        forward_url="/view_lps/?new=None"
        response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=request.params, forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect
    
    @expose(template="buzzbot.templates.edit_search_form")  
    #deprecated, but keep for use as template
    def test_project_fields_1(self):    
        submit_action = "/save_project_fields/"
        #set up some values to send to the form
        b=model.Search.select()
        someb = b[0]
        #inject these values into the form created from the ProjectFields widget list
        return dict(form=searchFormInstance, values = someb, action = submit_action)    
    
    @expose()
    #deprecated, but keep for use as template
    def save_project_fields(self, **kwargs):
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

    @expose(template="buzzbot.templates.verify_delete_search")    
    @expose()
    def verify_delete_search(self, **kwargs):
        #calls up a page to verify deletion of a search
        searchNum=int(kwargs.get('id'))
        b = Search.get(searchNum)
        #create a return string from the kwargs)
        retStr = ""
        for i in kwargs.items():
            k, v = i
            retStr=retStr + "&" + k + "=" + str(v)
        submit_action = "/delete_search/?" + retStr
        #inject these values into the form created from the verifyDeleteSearchFields widget list   
        return dict(form=verifyDeleteSearchForm, value = b, action = submit_action)
    
    @expose()    
    def delete_search(self,  **kwargs):
        #actually deletes a search after user confirmation
        if 'submit' in kwargs:  #user hit the submit button
            searchToDelete = int(kwargs.get('id'))
            Search.delete(searchToDelete)
        #we'll revert to the edit_lp form no matter which button was hit  
        #create a return string from the kwargs)
        retStr = ""
        for i in kwargs.items():
            k, v = i
            retStr=retStr + "&" + k + "=" + str(v)        
        raise redirect("/edit_lp/?" + retStr)  
                                 
    
    @expose(template="buzzbot.templates.verify_delete_lp") 
    def verify_delete_lp(self, **kwargs):
        #calls up a page to verify deletion of an LP
        lpToDelete=int(kwargs.get('extra_lpid'))
        b = Listeningpost.get(lpToDelete)
        #create a return string from the kwargs)
        retStr = ""
        for i in kwargs.items():
            k, v = i
            retStr=retStr + "&" + k + "=" + str(v)
        submit_action = "/delete_lp/?" + retStr
        #inject these values into the form created from the verifyDeleteLPFields widget list   
        return dict(form=verifyDeleteLPForm, value = b, action = submit_action)            

    @expose()
    def delete_lp(self, **kwargs):
        #actually deletes a search after user confirmation
        if 'submit' in kwargs:  #user hit the submit button
            lpToDelete = int(kwargs.get('extra_lpid'))
            Listeningpost.delete(lpToDelete)
        raise redirect("/view_lps/" + str(random.randint(1,10000)))

    
    def create_lp(self, **kwargs):
        #creates a new LP and invokes edit_lp routine
        thisID = identity.current.identity()
        thisUser = str(thisID.user_id)
        #if the user isn't logged in, provide a guest ID; This is best handled
        # with the identity logic, but we can deal with this later
        if thisUser == 'None':
            thisUser = GUESTID
        user = int(thisUser)
        lp = Listeningpost(name=unicode('New LP'),
                  userid = user,
                  created = datetime.now(),
                  modified = datetime.now()
              )
        lpid = lp.id
        retStr="?extra_lpid=" + str(lpid) + "&userid=" + str(user)  + "&status=owner" 
        raise redirect("/edit_lp/" + retStr)  
                         
    
    #view the LPs, allowing for selection, editing, and deletion
    @expose(template="buzzbot.templates.view_lps")   
    @expose()
    def view_lps(self, **kwargs):
        #figure out who this user is and where he belongs
        thisUserIDObj = identity.current.identity()
        msg=""
        #tg's identity module relies on cookies.  If the user has these blocked, the user is 
        #  set to 'None', which confuses the routine.  In this case, we'll provide a 'guest' id
        #  and a notification
        if thisUserIDObj.user_id == None:
            setUser(GUESTID)
            thisUserIDObj = identity.current.identity()
            msg = "Note: you are logged in as guest because cookies are blocked on your browser."
            
        thisUser = thisUserIDObj.user_id
        thisUserGroup = thisUserIDObj.groups    
        #the only group we really care about at this point is admin (to allow access to the
        #  interface)
        isadmin = False
        if 'admin' in thisUserGroup:
            isadmin = True
            

 
        #grab all the LPs - this is a bit inefficient, but we won't have millions for a while
        lps = model.Listeningpost.select()         
        lpsThisUser=model.Listeningpost.selectBy(userid=thisUser)
        lpsToDisplay = []  #an array of search objects to pass the the controller
        editURL = []  #  ...and a parallel array that flags that editing is allowed
        deleteURL =[] #  ...and one to signal that deletion is allowed 
        viewURL = []  #  ...and one to view the results
        ownerName =[]
        allUsers = User.select()
        
        #if we have a first-time user, create a new LP and start again
        if lpsThisUser.count() <1 :
            mylpid = self.create_lp()
        
        #list the LPs in this order: user's, group's, admin's    
        for s in lps:
            if s.userid == thisUser:  #give the user full run of his own searches
                lpsToDisplay.append(s)
                editURL.append("/edit_lp/" + "?extra_lpid=" + str(s.id) + "&userid=" + str(thisUser)  +"&status=owner" )
                deleteURL.append("/verify_delete_lp/" + "?" + "extra_lpid=" + str(s.id) + "&userid=" + str(thisUser)  +"&status=owner" )
                #find the "search" associated with this LP (it's an amalgom of all related searches)
                if s.searchtorun > 0 and model.Content.selectBy(searchid=s.searchtorun).count()>0:                
                    viewURL.append("/view_content/" + "?" + "searchid=" + str(s.searchtorun) + "&userid=" + str(thisUser)  +"&status=owner" )
                else: viewURL.append("")    
                ownerName.append(getUserName(thisUser))
        
        #if the LP begins to someone else and it's public then add it
        for s in lps:
            if s.userid <> thisUser and s.is_public:               
                ownerSearchObj = User.selectBy(id=s.userid)
                thisOwner = ownerSearchObj[0]
                thisOwnerName = thisOwner._get_display_name()
                thisOwnerGroup = thisOwner.groups
                
                if thisOwnerGroup == thisUserGroup:       
                    lpsToDisplay.append(s)
                    editURL.append("/edit_lp/" + "?" + "extra_lpid=" + str(s.id) + "&userid=" + str(thisUser)  +"&status=nonowner" )
                    deleteURL.append("")
                    
                    #find the "search" associated with this LP (it's an amalgom of all related searches)
                    if s.searchtorun > 0 and model.Content.selectBy(searchid=s.searchtorun).count()>0:                
                        viewURL.append("/view_content/" + "?" + "searchid=" + str(s.searchtorun) + "&userid=" + str(thisUser)  +"&status=owner" )
                    else: viewURL.append("") 
                        
                    ownerName.append(getUserName(s.userid))
                    
        #now find client-worthy LPs (perhaps added by an admin) 
        for s in lps:
            if s.is_client_worthy:
                #screen out searches we've already added
                addMe=True
                for d in lpsToDisplay:
                    if d.id == s.id:
                        addMe=False
                if addMe:        
                    lpsToDisplay.append(s)
                    editURL.append("/edit_lp/" + "?"+ "extra_lpid=" + str(s.id) + "&userid=" + str(thisUser)+"&status=nonowner" )
                    deleteURL.append("")
                    #find the "search" associated with this LP (it's an amalgom of all related searches)
                    if s.searchtorun > 0 and model.Content.selectBy(searchid=s.searchtorun).count()>0:                
                        viewURL.append("/view_content/" + "?" + "searchid=" + str(s.searchtorun) + "&userid=" + str(thisUser)  +"&status=owner" )
                    else: viewURL.append("")               
                    ownerName.append(getUserName(s.userid))

        #this directs the returned form to the processSLPInput method 
        retStr="&userid=" + str(thisUser)
        submit_action = "/process_view_lp_buttons/?"+retStr        
        
        
        return dict(form=edit_lp_form, lps=lpsToDisplay, editlink = editURL, 
                    owner=ownerName, deletelink = deleteURL, viewlink=viewURL,
                    msg=msg, action = submit_action, isadmin = isadmin)     
 
    @expose(template  = "buzzbot.templates.edit_lp")    
    def process_view_lp_buttons(self, **kwargs):
        #if a new LP has been requested, call edit_lp to make one
        if "new" in kwargs:
            self.create_lp()
            return
        if "admin" in kwargs:
            raise redirect("/admin/")
        
        if "home" in kwargs:
            raise redirect("/login/" )
        
    
    @expose(template="buzzbot.templates.edit_lp")
    @expose()
    def edit_lp(self, tg_error=None, **kwargs):
        args=[]
        args=kwargs
        thisID = identity.current.identity()
        thisUser = thisID.user_id
        thisUserGroup = thisID.groups
        thisLP = -666

        #the lpid field will come from the listeningPosts database 
        #  or from the search controller (as extra_lpid); this to differentiate
        #  status when updating different db tables

        if "extra_lpid" in kwargs:
            thisLP = int(kwargs.get('extra_lpid'))
        if "lpid" in kwargs:
            thisLP = int(kwargs.get('lpid')) 
 
            
        #find this lp and determine if the user owns it    
        try:#this succeeds if the LP exists
            lp = model.Listeningpost.get(thisLP)
            if lp.userid == thisUser:
                thisStatus = 'owner'
            else: thisStatus = 'nonowner' 
        except:#...if it fails, we'll build a new one
            lp = model.Listeningpost(userid = thisUser, name = "new LP", status = "owner")
 
            
        #create a dict of user-specifiable parameters of the listening post    
        inputDict = {'name' : lp.name,
                     'description' : lp.description,
                     'is_client_worthy' : lp.is_client_worthy,
                     'is_public' : lp.is_public,
                     'update_nightly': lp.update_nightly,
                     'userid': lp.userid,
                     'submit_text': 'OK',
                     'extra_lpid': thisLP,
                     'targetword': lp.targetword
                     }
        
        #get all the searches associated with this LP; we'll inject them into the template
        #  with as links to the edit search template; each link will carry url tags to identify 
        #  the owner, group, and LPid, and to (dis)allow editing or deletion of others' searches;
        #  we could just set cookies, but this is a bit cleaner vis-a-vis security

        searchesThisLP = model.LPSearch.selectBy(lp_id=thisLP)         
        searchesThisUser=model.Search.selectBy(userid=thisUser)
        allSearches = model.Search.select()
        searchesToDisplay = []  #an array of search objects to pass the the controller
        editURL = []  #  ...and a parallel array that flags that editing is allowed
        deleteURL =[] #  ...and one to signal that deletion is allowed 
        ownerName =[]
        allUsers = User.select()           
        
        #List the searches in this order: this LP's, user's, group's, admin's 
        #   Icons will get the tags to direct user to edit and delete methods; the delete tag
        #   is null if the user lacks permission to delete (not the owner, for now).  We'll refine the
        #   permissions to define group, sub-group, etc. permissions later.
        
        for s in searchesThisLP:
            try:
                #add the name of the search, links to edit, delete, and the owner's name to their own lists
                thisSearch = model.Search.get(int(s.search_id))
                searchesToDisplay.append(thisSearch)
                editURL.append("/edit_search/" + "?id=" + str(s.search_id) + "&user=" + str(thisUser)  +"&status=owner" + "&lpid=" + str(thisLP))
                deleteURL.append("/verify_delete_search/" + "?" + "id=" + str(s.search_id) + "&user=" + str(thisUser)  +"&status=owner"+ "&lpid=" + str(thisLP) )
                ownerName.append(getUserName(thisUser))
            except:    
                pass
            
        #get this user's searches  
        for s in searchesThisUser:
            if s.userid == thisUser and not s.islp:  #give the user full run of his own searches                    
                #screen out searches we've already added to our list
                addMe=True
                for d in searchesToDisplay:
                    if d.id == s.id:
                        addMe=False
                if addMe:        
                    searchesToDisplay.append(s)
                    editURL.append("/edit_search/" + "?id=" + str(s.id) + "&user=" + str(thisUser)  +"&status=owner"+ "&lpid=" + str(thisLP) )
                    deleteURL.append("/verify_delete_search/" + "?" + "id=" + str(s.id) + "&user=" + str(thisUser)  +"&status=owner" + "&lpid=" + str(thisLP))
                    ownerName.append(getUserName(thisUser))
    
        #these searches belong to other users in the same group and are marked public
        for s in allSearches:
            if s.userid <> thisUser and s.is_public and not s.islp:  
                #find this search owner's group
                thisOwner = User.get(s.userid)
                thisSearchOwnersGroup = thisOwner.groups
                
                if thisSearchOwnersGroup == thisUserGroup:   
                    addMe=True
                    for d in searchesToDisplay:
                        if d.id == s.id:
                            addMe=False        
                    if addMe:                     
                        searchesToDisplay.append(s)
                        editURL.append("/edit_search/" + "?" + "id=" + str(s.id) + "&user=" + str(thisUser)  +"&status=nonowner"+ "&lpid=" + str(thisLP) )
                        deleteURL.append("")
                        ownerName.append(getUserName(s.userid))
                
        #now find client-worthy searches (perhaps added by an admin) 
        for s in allSearches:
            if s.is_client_worthy and not s.islp:
                #screen out searches we've already added to our list
                addMe=True
                for d in searchesToDisplay:
                    if d.id == s.id:
                        addMe=False
                if addMe:        
                    searchesToDisplay.append(s)
                    editURL.append("/edit_search/" + "?" + "id=" + str(s.id) + "&user=" + str(thisUser)  +"&status=nonowner"+ "&lpid=" + str(thisLP) )
                    deleteURL.append("") 
                    ownerName.append(getUserName(s.userid))
        
        #make a list of check-box widgets for (de)selecting searches        
        widgetList=[]  
        #we'll keep count and check the ones currently associated with this LP
        count = 1
        currentSearches=searchesThisLP.count()

        for s in searchesToDisplay:
            #we'll name systematically to find the later; they'll be called  "ck_<LPid>" e.g., ch_1
            wName = "ck_" + str(s.id)
            w = widgets.CheckBox(name = wName)
            w.label = ""
            #we added the existing searches first, so we know to 'check' them
            if count <= currentSearches:
                w.default = True
            widgetList.append(w)   
            count=count+1
        #inject our check boxes into the table form widget
        retStr = "?thisLP="+str(thisLP)
        submit_action = "/save_lp/"+retStr
        
        return dict(form = edit_lp_form, checks = widgetList,  value = inputDict, 
                    searches = searchesToDisplay, owner = ownerName, action = submit_action, 
                    editlink = editURL, deletelink = deleteURL)      


    def update_lp_search_table(self, **kwargs):
        try:
            #first, we'll delete the existing searches associated with this lp
            thisLP = int(kwargs.get('extra_lpid'))
            LPSearch.deleteBy(lp_id = thisLP)
            #the return from the form includes a tuple of (key, value) tuples for all the checked boxes 
            #  all with names like 'ck_13'  e.g.,  {'ck_13': u'on',  'ck_11": u'on'}
            #...so, we'll loop through them and add rows to lpsearch as needed
            
            items = kwargs.items()
            for i in items:
                boxname, state = i         
                #parse the tuple (state will always be 'on' as only checked values returned)
                if boxname[:3] == 'ck_':
                    searchNum = int(boxname[3:])
                    LPSearch(lp_id = thisLP, search_id = searchNum) 
        except:
            "try, try, again"
        
    

    @expose()
    @validate(validators=dict(userid=Int(),
                              extra_lpid=Int()))
    def save_lp(self, **kwargs):
    #This handles three possibilities: the user has requested a new *search*, requested
    #  changes to the LP, or wants to run a test.  
    
        scoreContent = True    
    
        thisUser = kwargs.get('userid')
        thisStatus='owner'
        thisLP = kwargs.get('extra_lpid')
        userstr = "user=" + str(thisUser)
        useridstr = "userid=" + str(thisUser)
        statusstr = "status=" + thisStatus
        lpstr = "lpid=" + str(thisLP )
        kwargs.pop('icamefrom', None)
        icamefromstr = "icamefrom=lp"
                             
                 
        #if the user hit 'new', we'll provide a new search, otherwise we'll save this LP
        if 'newsearch' in kwargs:  
            thisName = 'New Search'
            newSearch = model.Search(name = "New Search", userid = thisUser)
            thisSearch=newSearch.id
            searchstr = 'id=' + str(thisSearch)
            #now set up a redirect to edit_search 

            retStr = userstr + '&' + statusstr + '&'  + lpstr + '&'  + searchstr
            raise redirect("/edit_search/?" + retStr)
        
        #save the lp if requested
        if 'home' in kwargs:
            deleteme=False
            searchid = myBotRoutines.createSearchFromLPspec(thisLP, deleteme, **kwargs)     
            #redirect back to the view_lps page, forcing a refresh
            raise redirect("/view_lps/" + str(random.randint(1,10000)))

        if 'web' in kwargs: #do a quick web search and view the results
            deleteme = True #move this off to the interface
            searchid = myBotRoutines.createSearchFromLPspec(thisLP, deleteme, **kwargs)
            perform_web_search_for(searchid)
            #display the content in the 'live' mode (Jason's logic)
            kwargs.pop('lpid')
            kwargs.pop('extra_lpid')
            raise redirect('/test_lp',
                           lpid=thisLP, icamefrom='lp', **kwargs)


    @expose("buzzbot.templates.edit_search_form")
    def edit_search(self, **kwargs):
    #Allows the user to edit or create searches. There are three possibilities:
    # - the searchID passed in has no value, implying a new search
    # - the searchID is valid and the user is its owner, so we edit the original
    # - the searchID is valid but now owned by the user, so edit a copy        
        #pick apart the kwargs
        if 'userid' in kwargs : 
            thisUser = int(kwargs.get('userid'))
        if 'user' in kwargs : 
            thisUser = int(kwargs.get('user'))            
        thisStatus=kwargs.get('status')
        thisLP = kwargs.get('lpid')
        if 'id' in kwargs:
            thisSearchID = kwargs.get('id')
        if 'searchid' in kwargs:
            thisSearchID = kwargs.get('searchid')
            
        thisReturnPage = "edit_search"
        #this checks to see if we have a searchID parameter
        try:  #if we can grab the search object, we do
            s = Search.get(thisSearchID)
            #if the user does not own the search, seed the new search with key fields
            if thisStatus <> 'owner':
                newSearch=model.Search(name="copy of " + s.name, description=s.description,
                         targetword=s.targetword, searchstring = s.searchstring,
                         eliminationwords = s.eliminationwords, maxurls=s.maxurls, 
                         urleliminate = s.urleliminate, urlsearchfor = s.urlsearchfor,
                         maxcontent = s.maxcontent, userid = thisUser,
                         datelastsearched=datetime.now()
                     )
                s=model.Search.get(newSearch.id)
        #if we can't find the search object make a new one
        except:  
            new=model.Search(userid=thisUser, name = "new Search")
            s = model.Search.get(new.id)
            thisSearchID = s.id
      
        #count the number of urls associated with this search
        numURLS= URLS.selectBy(search_id=thisSearchID).count()
        #...and the number of content blocks
        numContent=Content.selectBy(searchid=thisSearchID).count()
        #we'll pass this information in as a string
        m1= str(numURLS) + " URLS and " 
        m2 =  str(numContent) + " content blocks."
        msg = m1+m2
        #we'll pass the template the form (which specifies the fields to show)
        #  and a dict object containing the values.  This combination will allow
        #  the values to be passed automatically to the fields, assuming
        #  the field names are named in the dict and it's passed in as 'value'
        
        #this is a list of value:key tuple pairs representing the search object cols
        #for whatever reason, s._reprItems() truncates long strings; we'll have to
        #build our dictionary from components
        myvals = []
        myvals.append(('id', s.id))
        myvals.append(('userid', s.userid))
        myvals.append(('name', s.name))
        myvals.append(('description', s.description))
        myvals.append(('targetword', s.targetword))
        myvals.append(('searchstring', s.searchstring))
        myvals.append(('maxurls', s.maxurls))
        myvals.append(('maxcontent', s.maxcontent))
        myvals.append(('eliminationwords', s.eliminationwords))
        myvals.append(('datelastsearched', s.datelastsearched))
        myvals.append(('is_client_worthy', s.is_client_worthy))
        myvals.append(('urlsearchfor', s.urlsearchfor))
        myvals.append(('urleliminate', s.urleliminate))
        myvals.append(('isrecursive', s.isrecursive))
        myvals.append(('freezeurllist', s.freezeurllist))
        #we'll append a tuple representing this lpid
        myvals.append(('lpid', kwargs.get('lpid')))
        myvals.append(('extra_lpid', kwargs.get('lpid')))
        myvals.append(('status', thisStatus))
        

        #...then package it as a dict object for injection into the form
        myvalues=dict(myvals) 
               
        buttonText = "OK"
        submit_action = "/save_search/"     
        return dict(form=search_form, value = myvalues, message=msg, 
                    action = submit_action)

    @expose()   
    def save_search(self, **kwargs):  
    #Process the user input here.  Saves search specs to the database then either
    #  returns user to the edit_lp screen or (if a test has been requested) to
    #  the viewContents routine that's the ringmaster for showing results.         
        items = kwargs.items()  #this gets an dict array of (key, value) tuples
        #convert any string integers e.g., '1' to integer equivalent e.g., 1
        for thisItem in items:
            k, v = thisItem #parse the tuple
            try: 
                thisValueAsNumber = int(v)      #if this doesn't raise an error, the field is a number
                kwargs[k]=thisValueAsNumber     #update the dict by assigning a new value to the key 
            except:    
                pass     #if we have raised an error, we have text and will leave it alone
        
        #Now we'll inject the data into the database. We have to do some pruning, though
        #  because there are some fields in the form that aren't in the database.  If we try
        #  to add them, the database (actually SQLObject) will barf.  By convention we've named
        #  these 'helper fields' to begin with 'extra_'; this allows us to build a replacement
        #  kwargs list with only valid db fields.
        
        #datetime objects don't translate well as kwargs passed around, we'll
        #  kill those, as well as the kwargs for the submit buttons and 'id' which is assumed
        validKwargs=[]
        for i in kwargs.items():
            k,v = i  #key, value
            if k[:6]<>"extra_" and k[:4]<>"date" and k<> 'home' and \
               k<> 'id' and k<> 'icamefrom' and k<>'urls' and k<>'web':
                validKwargs.append((k,v))
         
        #update the database  
        searchid = kwargs.get('id')
        b= Search.get(int(searchid))
        #this syntax is a bit strange, but it's what the set() method needs: a keyword dict object
        b.set(**dict(validKwargs))
 
        useridstr = "userid=" + str(kwargs.get('userid'))
        searchstr = "searchid="+str(kwargs.get('id'))
        if 'lpid' in kwargs:
            lpstr = str(kwargs.get('lpid'))
        else: lpstr = "extra_lpid=" + str(kwargs.get('extra_lpid'))
        statusstr = "status=" + str(kwargs.get('status'))
        icamefromstr = "icamefrom=edit_search"
        returnstr = 'returntopage=edit_search'
        startstr = 'start=0'
        
        if 'web' in kwargs: #do a quick web search and view the results
            perform_web_search_for(searchid)

            #send a parameter to let view_contents know to return to the edit search page
            #  (instead of the edit lp page
            raise redirect ('/live_content/?'  + useridstr + '&' + lpstr + '&' + searchstr + '&' + \
                        returnstr + '&' + startstr + '&' + statusstr )
            #raise redirect ('/view_content/?'  + useridstr + '&' + lpstr + '&' + searchstr + '&' + \
            #            returnstr + '&' + startstr + '&' + statusstr )
        
        
        if 'urls' in kwargs:  #check out the URLS
            raise redirect ('/view_urls/?'  + useridstr + '&' + lpstr + '&' + searchstr +  '&' + returnstr+ '&' + startstr + '&' + statusstr + '&' + icamefromstr )
            
        if 'home' in kwargs:  #return to edit_lp
            raise redirect ('/edit_lp/?'  + useridstr + '&' + lpstr)

    @expose("buzzbot.templates.view_urls")
    @expose()
    def view_urls(self, **kwargs):
        #allows user to manage the urls associated with this search
        #these are the hidden fields that are output as kwargs
        thisSearch = kwargs.get('searchid')
        thisUser = kwargs.get('userid')
        if 'lpid' in kwargs:
            thisLP = int(kwargs.get('lpid'))
        else: thisLP =int(kwargs.get('extra_lpid'))        
        thisStatus = kwargs.get('status')
        icamefrom = kwargs.get('icamefrom')
        
        #massage these for inclusion in the kwarg string for the return
        useridstr = "userid=" + str(thisUser)
        searchstr = "searchid="+str(thisSearch)
        lpstr = "lpid=" + str(thisLP)
        statusstr = "status=" + thisStatus
        icamefromstr = "icamefrom=" + icamefrom
        
        #if the user clicked 'add', we'll redirect to the add_urls page
        if 'add' in kwargs:
            retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr + '&' + icamefromstr
            raise redirect('/add_urls/?' + retStr)
        
        #if the user clicked 'ok', we'll send him/her to originating page
        if 'ok' in kwargs:
            if icamefrom == "edit_search":
                retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr
                raise redirect ('/edit_search/?' + retStr)
            if icamefrom == "edit_lp":
                retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr
                raise redirect ('/edit_lp/?' + retStr)            
        
        #...otherwise, we'll be viewing the urls in the database
        
        #if starting record is in kwargs grab it, else start at top    
        if 'start' in kwargs:
            lastStart =int(kwargs.get('start'))
        else: thisStart = 0
        #set the default step action
        stepAction = 'none'    
        thisStep = 20  
        #figure out whether to return
        returnPage = 'view_urls'
 
        #grab the data (in this case the URLS)
        myData = model.URLS.selectBy(search_id = thisSearch)
        myCount = myData.count()

        #set start and end, making sure we don't overrun the end of the content
        lastbtn = True; nextbtn=True
        #find whether next or last buttons were hit
        if 'next' in kwargs: 
            stepAction = 'next'
        if 'last' in kwargs:
            stepAction = 'last'                
                
        #if we're going backwards we know the end is OK; make sure the beginning >=0
        if stepAction == 'last':
            thisStart = max(lastStart - thisStep, 0)
            thisEnd = min(thisStart + thisStep, myCount)   

        else: #we're going forward
            if stepAction == 'none': #this is the first look at the content
                thisStart = 0
            else:   #we're already looking at content and want to see more
                thisStart = min(lastStart + thisStep, myCount)  
            thisEnd = min(thisStart + thisStep, myCount)                 
        
        #set flags for displaying next/last buttons
        if thisStart ==0: lastbtn = False
        if thisEnd >=myCount: nextbtn = False
        
        #nibble off a piece of the content for display
        data = myData[thisStart:thisEnd] 
        
        #build remaining kwargs and submission string
        startstr = "start=" + str(thisStart)
        stepstr = "step=" + str(thisStep)
        returnstr = "returntopage=" + returnPage         

        retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr + '&' + startstr + '&' + stepstr + '&' + returnstr
        submit_action = "/view_urls/?" + retStr
        
        #we might put an if block to return user to originating page if we have no data to show,
        #  but here we'll give the user a chance to add his/her own even if there is no existing content

        #we'll make a list of check boxes to accompany each data row (can be used to flag delete, 
        #  etc.)
        widgetList = []
        for d in data:
            wName = "ck_" + str(d.id)
            w = widgets.CheckBox(name = wName)
            w.label = ""
            #set default to False
            w.default = False   
            widgetList.append(w) 
            
        #...along with a list to hold the data
        formdata=[]
        for d in data:            
            formdata.append(d.urltext)
        
        #the input dict will be injected into our form
        inputDict = {'userid' : str(thisUser),
                     'lpid' : str(thisLP),
                     'searchid' : str(thisSearch),
                     'start': str(thisStart),
                     'step': str(thisStep),
                     'returntopage': returnPage,
                     'nextbtn': nextbtn,
                     'lastbtn': lastbtn,
                     'icamefrom': icamefrom,
                     'status': thisStatus
                 }
        return dict(form = url_form, data=formdata,  checks=widgetList, value = inputDict, 
                    action = submit_action)
  
       
      ####################################################  
    @expose()
    def process_add_urls(self, **kwargs):
        #processes return from the 'add_urls' form
        thisSearch = kwargs.get('searchid')
        thisUser = kwargs.get('userid')
        if 'lpid' in kwargs:
            thisLP = int(kwargs.get('lpid'))
        else: thisLP =int(kwargs.get('extra_lpid'))        
        thisStatus = kwargs.get('status')
        icamefrom = kwargs.get('icamefrom')
        
        #massage these for inclusion in the kwarg string for the return
        useridstr = "userid=" + str(thisUser)
        searchstr = "searchid="+str(thisSearch)
        lpstr = "lpid=" + str(thisLP)
        statusstr = "status=" + thisStatus
        
        if not 'cancel' in kwargs:
            #the user has the option to delete existing urls or add new ones
            if 'deleteexisting' in kwargs and thisLP > 0:
                model.URLS.deleteBy(search_id = thisSearch)
            
            #grab the user-supplied urls; 
            userUrls = kwargs.get('rawurls')
            now = datetime.now()
            if len(userUrls)>0:
                fakeRetObj = dict(status = 0, data = kwargs.get('rawurls'))
                urlList = myBotRoutines.digUrlsOutOfPage(fakeRetObj)  #returns a list of urls
                
                #fixUrlsinArray cleans up (dedups, etc.) the list of urls.  The parameter targetwordArray is
                #  used to eliminate the client's own web site, but we won't second-guess the user
                targetWordArray = []
                cleanUrlList = myBotRoutines.fixURLSinArray(urlList, targetWordArray)
                
                #add these new urls to the database
                for u in cleanUrlList:
                    scheme, netloc, path, query, fragment = urlsplit(u)
                    newurl = model.URLS(scheme = scheme, netloc=netloc, path=path, search_id = int(thisSearch),
                                               query = query, fragment=fragment, urltext=u,
                                               lpid = int(thisLP), datefound=now, userid = int(thisUser)) 
                    
                #De-dup the URLs database
                mycont = model.URLS.selectBy(search_id = int(thisSearch)).orderBy('urltext')
                lastcont=""
                for c in mycont:
                    if c.urltext == lastcont:
                        model.URLS.delete(c.id)
                    else: lastcont = c.urltext
                    
                # end of 'if cancel' loop    
                    
            #Build kwargs and submission string
            useridstr = "userid=" + str(thisUser)
            searchstr = "searchid="+str(thisSearch)
            icamefromstr = "icamefrom=" + icamefrom
            lpstr = "lpid=" + str(thisLP)
            statusstr = "status=" + thisStatus
            retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr + '&' + icamefromstr    
        
        if icamefrom == 'view_urls':
            raise redirect ('/view_urls/?' + retStr) 
        
        if icamefrom == 'view_lps':
            raise redirect ('/view_lps/?' + retStr)       
        
        if icamefrom == 'edit_search':
            raise redirect ('/edit_search/?' + retStr)         

    @expose("buzzbot.templates.add_urls")
    @expose()
    def add_urls(self, **kwargs):
        #exposes form to allow user to add urls via copy/paste operation
        submit_action = "/process_add_urls/"

        #grab the kwargs
        thisSearch = kwargs.get('searchid')
        thisUser = kwargs.get('userid')
        thisLP = kwargs.get('extra_lpid')  
        icamefrom = kwargs.get('icamefrom')
        thisStatus = kwargs.get('status')
                  
        #Build kwargs and submission string
        useridstr = "userid=" + str(thisUser)
        searchstr = "searchid="+str(thisSearch)
        lpstr = "lpid=" + str(thisLP)
        statusstr = "status=" + thisStatus
        icamefromstr = "icamefrom=" +kwargs.get('icamefrom')   
        retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr    
    
        #the input dict will be injected into our form
        inputDict = {'userid' : str(thisUser),
                     'lpid' : str(thisLP),
                     'searchid' : str(thisSearch),
                     'icamefrom': icamefrom,
                     'status': thisStatus
                 }
        return dict(form = url_form, value = kwargs, action = submit_action)          

    @expose("buzzbot.templates.live_content")
    @validate(validators=dict(userid=Int(), lpid=Int()))
    def test_lp(self, userid=None, lpid=None, **kwargs):
        # TODO consider renaming this action because it's no longer testing anything, but merely displaying results

        if mode == 'db':
            def prep():
                #bot.dedupcontent()
                #model.Content.deleteBy(lpid=lpid)
                #model.Contsearch.deleteBy(lp=lpid)
                #myBotRoutines.runLPOnDatabase(lpid, 50, True, userid=userid,
                #                              extra_lpid=lpid, **kwargs)

                return model.Listeningpost.get(lpid).searchtorun
        else:
            pass
            #def prep():
                #searchid = model.Listeningpost.get(lpid).searchtorun
                #myBotRoutines.runSearch(self, searchid, **kwargs) # self? looks funky
                #return searchid

        # TODO why isn't searchid in there already!?
        searchid = model.Listeningpost.get(lpid).searchtorun
        return self.live_content(userid=userid, extra_lpid=lpid, _prep=prep, searchid=searchid, **kwargs)

    @expose("buzzbot.templates.live_content")
    @validate(validators=dict(searchid=Int(),
                              userid=Int(),
                              extra_lpid=Int(),
                              lpid=Int()))
    def live_content(self, searchid=None, userid=None, lpid=None,
                     extra_lpid=None, status=None, icamefrom=None,
                     _prep=None, **kwargs):
        #this will display content for either a single search or for a LP
        lpid = extra_lpid or lpid

        if icamefrom == 'search':
            back = url('/edit_search',
                       userid=userid, searchid=searchid, lpid=lpid, status=status)
        elif icamefrom == 'lp':
            back = url('/edit_lp',
                       userid=userid, lpid=lpid, status=status)
        else:
            back = url('/view_lps',
                       userid=userid, searchid=searchid, lpid=lpid, status=status,
                       returntopage='view_content')

        queue_url = url('/nibble_content', queue_id=searchid)
        
        return dict(back=back, queue_url=queue_url)

    @expose('json')
    def nibble_content(self, queue_id):
        cherrypy.response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        cherrypy.response.headers['Pragma'] = 'no-cache'

        # hack: need security, less suckage
        ## print "nibbling start"
        queue_id = int(queue_id)
        res = dict(status='ok', items=[])
        content_ids = []

        # TODO figure out how to determine if crawler_runner is done
        try:
            content_ids = crawler_runner().results_for(queue_id)
        except Exception, e:
            print "crawler_runner().results_for(%s) failed: %s" % (queue_id, e)

        if content_ids:
            for content_id in content_ids:
                content = model.Content.get(content_id)
                date = content.dateaccessed.strftime('%b-%d-%Y')
                res['items'].append([content.polarity, date, content.cont, content.urltext])

        print "nibbled %s items" % len(res['items'])
        return res
    
            
    @expose("buzzbot.templates.view_content")
    @expose()
    def view_content(self,  **kwargs):
        #this will display content for either a single search or for a LP
        thisSearch = kwargs.get('searchid')
        thisUser = kwargs.get('userid')
        if 'extra_lpid' in kwargs:
            thisLP = kwargs.get('extra_lpid')
        else: thisLP = kwargs.get('lpid')

        thisStatus = kwargs.get('status')
        icamefrom= kwargs.get('icamefrom')
        #if starting record is in kwargs grab it, else start at top    
        if 'start' in kwargs:
            lastStart =int(kwargs.get('start') or 0)
        else: thisStart = 0
        #set the default step action
        stepAction = 'none'    
        thisStep = 20  
        #figure out whether to return
        returnPage = 'view_content'
   
        #grab the content from the database
        allcont = model.Content.selectBy(searchid = thisSearch).orderBy('polarity')
        contentCount = allcont.count()
        #set start and end, making sure we don't overrun the end of the content
        lastbtn = True; nextbtn=True
        #find whether next or last buttons were hit
        if 'next' in kwargs: 
            stepAction = 'next'
        if 'last' in kwargs:
            stepAction = 'last'                
                
        #if we're going backwards we know the end is OK; make sure the beginning >=0
        if stepAction == 'last':
            thisStart = max(lastStart - thisStep, 0)
            thisEnd = min(thisStart + thisStep, contentCount)   

        else: #we're going forward
            if stepAction == 'none': #this is the first look at the content
                thisStart = 0
            else:   #we're already looking at content and want to see more
                thisStart = min(lastStart + thisStep, contentCount)  
            thisEnd = min(thisStart + thisStep, contentCount)                 
        
        #set flags for displaying next/last buttons
        if thisStart ==0: lastbtn = False
        if thisEnd >=contentCount: nextbtn = False
        
        #nibble off a piece of the content for display
        cont = allcont[thisStart:thisEnd]
        
        #analyze the content, if it hasn't been analyzed already; we'll poke in any changed score then
        #  re-query the database.  Note, we could do this more efficiently, but this should cut the processing
        #  time for each page processed by the user; besides, SQLObject uses lazy updates so results are returned
        #  only when needed.
        anyupdates = False
        for c in cont:
            if int(c.polarity) == 666:  #our default value
                anyupdates = True
                polarity = myBotRoutines.analyzeContentBlock(c.cont)
                rec = model.Content.get(c.id)
                rec.polarity = int(polarity)
        if anyupdates:
            allcont = model.Content.selectBy(searchid = thisSearch).orderBy('polarity')
            cont = allcont[thisStart:thisEnd]
        
        #we'll make a list of check boxes to accompany each bit of content
        widgetList = []
        for c in cont:
            wName = "ck_" + str(c.id)
            w = widgets.CheckBox(name = wName)
            w.label = ""
            #set default to False
            w.default = False   
            widgetList.append(w)  
            
        useridstr = "userid=" + str(thisUser)
        searchstr = "searchid="+str(thisSearch)
        lpstr = "lpid=" + str(thisLP)
        statusstr = "status=" + thisStatus
        startstr = "start=" + str(thisStart)
        stepstr = "step=" + str(thisStep)
        returnstr = "returntopage=" + returnPage
        
        retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr + '&' + startstr + '&' + stepstr + '&' + returnstr
        submit_action = "/view_content/?"
        
        #if we've got something to show, content-wise, then show it
        #  sqlObject won't let us do a count on a slice, so we'll ask for the first
        #  element; if the request fails, the request object is empty
        haveContent = True
        try: 
            testcont = cont[0]
        except:
            haveContent = False
        if haveContent  and not 'ok' in kwargs:
            #these are the hidden fields that are output as kwargs
            inputDict = {'userid' : str(thisUser),
                         'lpid' : str(thisLP),
                         'searchid' : str(thisSearch),
                         'status' : thisStatus,
                         'start': str(thisStart),
                         'step': str(thisStep),
                         'returntopage': returnPage,
                         'nextbtn': nextbtn,
                         'lastbtn': lastbtn,
                         'icamefrom': icamefrom
                     }   
            #instead of passing in the whole search object, we'll parse out the good stuff;
            #  while we're at it, we'll reformat the GMT date and re-do the links
            mycont=[] #this will hold dict elements of the values we'll pass in
            mydate=[]
            myscore=[]
            mylink=[]
            for c in cont:
                rawDate = c.dateaccessed
                dateString = months[rawDate.month] + '-' + str(rawDate.day) + '-' + str(rawDate.year)
                mydate.append(dateString)
                mycont.append(c.cont)
                myscore.append(str(c.polarity))
                if c.urltext[0] =='"':
                    mylink.append(c.urltext[1:-1])  #the slice operation removes bracketing ""
                else: mylink.append(c.urltext)    
            return dict(form = content_form, date=mydate, cont=mycont, score=myscore, 
                        link = mylink, checks=widgetList, value = inputDict, 
                        action = submit_action, is_search=True)             
                       
        else: #we don't have anything to show content-wise or use hit 'ok'
            #go back to editing whatever we're editing
          
            if icamefrom == 'search':
                retStr = useridstr + '&' + searchstr + '&' + lpstr + '&' + statusstr
                raise redirect ('/edit_search/?' + retStr)  
            if icamefrom == 'lp':
                retStr = useridstr + '&' + lpstr + '&' + statusstr
                raise redirect ('/edit_lp/?' + retStr)   
            if icamefrom == '': #we're viewing the content from the view_lp screen
                raise redirect ('/view_lps/?' + retStr)

    @expose("buzzbot.templates.admin")
    @expose()
    def admin(self):
        submit_action = "/process_admin/"
        value = {}
        return dict(form = adminForm, action = submit_action, value = value)          
        
    @expose("view_lps")
    @expose()
    def process_admin(self, **kwargs):
        #this is a placeholder for the ultimate admin interface; for now it just
        #lets the user pick which search sites to ping to populate each lp's url list
        #later, we'll want to set options to freeze url listings for different lps, run
        #a search over all known blog urls then add content to each lp, etc.
        mySites = []
        if "ok" in kwargs:
            #figure out what the user has checked and add the search engine
            #  site to the list of engines to ping
            #to update this list, go to class adminFields (above)
            if 'technorati' in kwargs: mySites.append ('www.technorati.com')
            if 'livejournal' in kwargs: mySites.append ('www.livejournal.com')
            if 'alexa' in kwargs: mySites.append ('www.alexa.com')
            if 'myspace' in kwargs: mySites.append ('forums.myspace.com')
            if 'aol' in kwargs: mySites.append ('search.aol.com')
            if 'skyblog' in kwargs: mySites.append ('www.skyrock.com')
            if 'xanga' in kwargs: mySites.append ('www.technorati.com')

            searcher.RunBackgroudSearch(mySites)              
            
           
            raise redirect("/view_lps/")
        if "cancel" in kwargs:
            raise redirect("/view_lps/")
        
    def fixDB(self):
        mydata = model.Content.select()
        for d in mydata:
            d.set(user_id=1)
            d.set(search_id=1)

def getUserName(id):
    userObject = User.get(id)
    name = userObject.display_name
    return name

#this takes out everything (urls, content, words)using foreign keys
def cleanUrlsContentAndWords(searchID):
    model.URLS.deleteBy(search_id = searchID)
    
def perform_web_search_for(searchid, deleteme=True, scoreContent=False, max_results=None):
    """
    Perform a web search for the Search record matching `searchid`. This
    retrieves search results and visits them to get their data.

    Keyword arguments:
    * `deleteme`: Delete existing records.
    * `scoreContent`: Score contents.
    """
    # TODO Is there any situation where deleteme will be False?
    # TODO Is there any situation where scoreContent will be True?

    max_results = 8 # TODO eliminate this max_results override when visitor is parallelized
    crawler_runner().enqueue(search_id=searchid, delete_existing=deleteme, max_results=max_results)

def crawler_runner():
    return crawler.CrawlerRunner.get_instance()
