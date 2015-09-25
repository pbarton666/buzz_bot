from datetime import datetime
import pkg_resources
pkg_resources.require("SQLObject>=0.8")
pkg_resources.require("TurboGears>=1.0.4.4")
import sys
from os import getcwd
from os.path import dirname, exists, join
import cherrypy
import turbogears

cherrypy.lowercase_api = True

from turbogears.database import PackageHub

from sqlobject import SQLObject, SQLObjectNotFound, RelatedJoin
from sqlobject import StringCol, UnicodeCol, IntCol, DateTimeCol, FloatCol, BoolCol, ForeignKey
from turbogears import identity
from sqlobject.sqlbuilder import *
from turbogears import validate, redirect, widgets, validators, error_handler

__connection__ = hub = PackageHub('buzzbot')


def validator_txt(len):
    return validators.All(validators.NotEmpty(), validators.PlainText(), validators.MaxLength(len))
def validator_int():
    return validators.All(validators.NotEmpty(), validators.Int())


# main data tables
class Contsearch(SQLObject):
    class sqlmeta:
        table = 'cont_search'
    cont = IntCol(default = 0)
    search = IntCol (default = 0)
    lp = IntCol(default  = -666)
class URLsearch(SQLObject):
    class sqlmeta:
        table = 'url_search'
    url = IntCol(default = 0)
    search = IntCol (default = 0)  
    
class Content(SQLObject):
    class sqlmeta:
        table = 'content' 
    cont = StringCol(length=2000)
    urltext = StringCol(length = 500)
    poswords = IntCol(default = 666)
    negwords = IntCol(default = 666)
    polarity = FloatCol(default = 666)
    score1 = FloatCol(default = 666.6)
    score2 = FloatCol(default = 666.6)
    deleteme = BoolCol(default = False)
    urlid = IntCol(default = 0)
    userid=IntCol(default = 0)
    searchid = IntCol(default = -666)
    clientid = IntCol(default = 0)
    dateaccessed = DateTimeCol(default = datetime.now())
    lpid = IntCol(default = -666)
    
class NegationWords(SQLObject):
    class sqlmeta:
        table = 'negationwords'
    word = StringCol(length=50)
    
class PosWords(SQLObject):
    class sqlmeta:
        table = 'poswords'
    word = StringCol(length=50)
    
class NegWords(SQLObject):
    class sqlmeta:
        table = 'negwords'
    word = StringCol(length=50)   
class SemanticList(SQLObject):
    class sqlmeta:
        table = 'semanticlist'
    word = StringCol(length=50)
    defnum = IntCol(default = 1)
    worddef = StringCol(length=300)
    pctthisdef = IntCol(default = 100)
    wordatts = StringCol(length=300)   
class ObsceneWords(SQLObject):
    class sqlmeta:
        table = 'obscenewords'
    word = StringCol(length=50)
    defnum = IntCol(default = 1)
    worddef = StringCol(length=300, default = " ")
    pctthisdef = IntCol(default = 100)
    wordatts = StringCol(length=300, default = " ")
class Companies(SQLObject):
    class sqlmeta:
        table = 'companies'
    name = UnicodeCol(length = 200, default = "widget corp")   
    count = IntCol(default = 0)
    category = UnicodeCol(length = 20, default = 'company')
    
class URLS(SQLObject):
    class sqlmeta:
        table = 'urls'
    scheme = UnicodeCol(length=20, default = u"scheme") 
    netloc = UnicodeCol(length=100, default = u"netloc")
    path = UnicodeCol(length=700, default = u"path")
    query = UnicodeCol(length=500, default = u"query")
    fragment = UnicodeCol(length=10, default = u"fragment")
    source = UnicodeCol(length=500, default = u"source")
    etag = UnicodeCol(length=50, default = u"etag")
    score = FloatCol(default = 666.6)
    deleteme = BoolCol(default = False)
    searchorder = IntCol(default = 1)
    relatedcontent = UnicodeCol(length = 45, default = u"relatedcontent")
    is_verified_blog = BoolCol(default = False)
    is_verified_good = BoolCol(default = False)
    is_blacklisted = BoolCol(default = False)
    is_whitelisted = BoolCol(default = False)
    search_id=IntCol(default = 1)
    datelastsearched =DateTimeCol(default = datetime.now())
    datefound =DateTimeCol(default = datetime.now())
    #we don't really need the intact text as we've stored the components, but leave in for testing.
    urltext = UnicodeCol(length=500, default = u"http://www.nytimes.com")
    userid = IntCol(default = 666)
    polarity=FloatCol(default = 666)
    lpid = IntCol(default = 666)
    seedtype = IntCol(default = 666)
    referredby = UnicodeCol(length = 400, default = 'dummy')
    depth = IntCol(default = 0)

class Word(SQLObject):
    class sqlmeta:
        table = 'word'        
    word = StringCol(length=45, default = "word")
    connotation = StringCol(length=45, default = "connotation")
    urlid = IntCol()    
    searchid = IntCol(default = 666)
    contid = IntCol(default = 666)
class Search(SQLObject):
    class sqlmeta:
        table = 'search'
    #tried to make these unicode, but strings displayed as u'<something>', which
    #  completely screws up searches and aesthetics
    name = StringCol(length=45, default = "name")
    description = StringCol(length=200, default = "description")
    targetword = StringCol(length=45, default = "target word")
    userid = IntCol()
    searchstring=StringCol(length=3000, default = "search string")
    maxurls=IntCol(default = 100)
    maxcontent = IntCol(default = 100)
    eliminationwords = StringCol(length=300, default = "elimination words")
    datelastsearched = DateTimeCol(default = datetime.now())
    is_client_worthy = BoolCol(default = False)
    is_public = BoolCol(default = False)
    urlsearchfor=StringCol(length=400, default="http")
    urleliminate=StringCol(length=400, default="aardvark")
    isrecursive = BoolCol(default = False)
    freezeurllist=BoolCol(default=True)  
    status = StringCol(length=45, default = "owner")
    islp = BoolCol(default = False)
    
    
#this stores LP-search pairs    
class LPSearch(SQLObject):
    class sqlmeta:
        table = 'lp_search'
    search_id = IntCol(default = 666)
    lp_id = IntCol(default=666)

#contains the attributes of the listening post        
class Listeningpost(SQLObject):
    class sqlmeta:
        table = 'listeningpost'    
      
    is_public = BoolCol(default = False)
    is_client_worthy = BoolCol(default=False)
    name = StringCol(length=45, default = "my LP")
    description = StringCol(length = 200, default = u"description")
    userid = IntCol()
    lp_key = StringCol(alternateID=True, alternateMethodName='by_lp_key', default = 'myLP')
    created=DateTimeCol(default = datetime.now())
    modified=DateTimeCol(default = datetime.now())
    update_nightly=BoolCol(default = False)
    freezeurllist = BoolCol(default = True)
    keepcontent = BoolCol(default = True)
    targetword = StringCol(default = "target word")
    searchtorun = IntCol(default = -666)
#    listeningpost = RelatedJoin('Search', intermediateTable='lp_search',
#                        joinColumn='listeningpost_id', otherColumn='search_id')    
    #finds all searches associated with this LP
    def lookup_searches(cls, lp_id):
        try:
            return cls.by_lp_key(lp_id)
        except SQLObjectNotFound:
            return None
    lookup_searches = classmethod(lookup_searches)    
    
    #clears all search associations with this LP (does not delete searches)
    def clearSearchAssociations (cls, lp_id):
        try:
            return cls.by_lp_key(lp_id)
        except SQLObjectNotFound:
            return None
    clearSearchAssociations = classmethod(clearSearchAssociations)     
    
    def addSearchAssociations (cls, lp_id, searches):
        try:
            return cls.by_lp_key(lp_id)
        except SQLObjectNotFound:
            return None
    addSearchAssociations = classmethod(addSearchAssociations)     
    
    
# classes for the identity (authentication) system         
class Visit(SQLObject):
    """
    A visit to your site
    """
    class sqlmeta:
        table = 'visit'

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName='by_visit_key')
    created = DateTimeCol(default=datetime.now())
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)


class VisitIdentity(SQLObject):
    """
    A Visit that is link to a User object
    """
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName='by_visit_key')
    user_id = IntCol()

class Group(SQLObject):
    """
    An ultra-simple group definition.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = 'tg_group'

    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName='by_group_name')
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin('User', intermediateTable='user_group',
                        joinColumn='group_id', otherColumn='user_id')

    # collection of all permissions for this group
    permissions = RelatedJoin('Permission', joinColumn='group_id',
                              intermediateTable='group_permission',
                              otherColumn='permission_id')
 

class User(SQLObject):

    class sqlmeta:
        table = 'tg_user'

    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName='by_user_name')
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName='by_email_address')
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)
    company = UnicodeCol(length = 50, default = "Widget International")

    # groups this user belongs to
    groups = RelatedJoin('Group', intermediateTable='user_group',
                         joinColumn='user_id', otherColumn='group_id')

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms |= set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        """Runs cleartext_password through the hash algorithm before saving."""
        password_hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(password_hash)

    def set_password_raw(self, password):
        """Saves the password as-is to the database."""
        self._SO_set_password(password)
    
class Permission(SQLObject):
    """
    A relationship that determines what each Group can do
    """
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName='by_permission_name')
    description = UnicodeCol(length=255)

    groups = RelatedJoin('Group',
                         intermediateTable='group_permission',
                         joinColumn='permission_id',
                         otherColumn='group_id')




