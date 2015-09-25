import pkg_resources
pkg_resources.require("SQLObject>=0.8,<=0.10.0")
from turbogears.database import PackageHub
from sqlobject import *
from sqlobject.sqlbuilder import *
from turbogears import validate, redirect, widgets, validators, error_handler

__connection__ = hub = PackageHub('sqlob')

def validator_txt(len):
    return validators.All(validators.NotEmpty(), validators.PlainText(), validators.MaxLength(len))
def validator_int():
    return validators.All(validators.NotEmpty(), validators.Int())

class EditSearches(widgets.WidgetsList):
    #the variable names reflect the column names in the database
    # they also are the names of the widgets in widget list for this class 
    #  i.e., EditSearches.declared_widgets
    #
    name = widgets.TextField(label = "Name:")
    description = widgets.TextField(label = "Description:")
    target_word = widgets.TextField(label = "Target word:")
    search_string=  widgets.TextArea(label = "Search for:")        
    elimination_words = widgets.TextArea(label = "...except content that contains:")
    max_urls=widgets.TextField(label = "Max URLs:")
    max_content= widgets.TextField(label = "Max content:")   
    user_id= widgets.HiddenField()    
    client_id= widgets.HiddenField() 
    date_last_searched= widgets.HiddenField()            
        

edit_search_form = widgets.TableForm(fields=EditSearches.declared_widgets, 
                               submit_text="Save", action = "Post")

class Content(SQLObject):
    #id=IntCol()
    #contprimarynumber = IntCol(alternateID=True)
    urls= ForeignKey('Urls')
    cont = UnicodeCol()
    urlItems = RelatedJoin('Urls')
    urlid = IntCol()
    search_id=IntCol()
    user_id = IntCol()
    dateaccessed = UnicodeCol()
    polarity =FloatCol()
    
class Urls(SQLObject):
    #id=IntCol()    urlnumber= IntCol(alternateID=True)
    relatedcontent = RelatedJoin('Content')
    netloc = UnicodeCol()
    scheme=UnicodeCol()
    
class Search(SQLObject): 
    name = UnicodeCol()
    description = UnicodeCol()
    client_id=IntCol()
    target_word = UnicodeCol()
    user_id= IntCol()
    search_string = UnicodeCol()
    date_last_searched=UnicodeCol()
    max_urls=IntCol()
    max_content=IntCol()
    elimination_words=UnicodeCol()

        
    

        
    