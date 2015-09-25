'''
This module contains database routines that may be accessed with or without using a web framework. 

'''
###TODO:  need to put the project and the app on the python path so these imports work (a copy of settings.py is in the current directory for now)
#I think all we realy need to do is make sure the settings module and the environment variables are correct.
#slam in the djang settings (this takes place of running manage.py
from django.core.management import execute_manager
import settings
import os
import sys
from MySQLdb.connections import IntegrityError

'''This block of code is for running the module in a 'stand-alone' mode for testing
   The import statement is very important because django is looking for a "fully specified"
   representation of the module 'models'  i.e. at least a first- and second-order path.
   Here, the object is <module 'djangoproj.djangoapp.models' from some_file_system>  If we simply say
   "import models", the object is <module 'models'> which django is unable to process.
'''
rootdir = '/home/pat1/workspace/'
if rootdir not in sys.path:
    sys.path.append(rootdir)
from djangoproj.djangoapp import models


#standard modules
##from sqlobject import mysql, SQLObject, StringCol, dberrors  #change the import to use dbs other than MySQL
from datetime import datetime
import logging
import unittest
import random
import test

#custom modules
import projectSpecs as projectSpecs

#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

#return codes 
RETURN_SUCCESS = projectSpecs.RETURN_SUCCESS
RETURN_FAIL = projectSpecs.RETURN_FAIL

#database parameters and connection object using specs from an external file; the connection object is global to this modul

###Database Objects###
#import models
#remove the sqlObject flavor; we'll import djangos

###Error Class(es)
class DbError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)	

###Management Classes  
class DatabaseMethods():
    '''This class adds urls from a list.  If doOrder is true, we'll add an "order" parameter to the table to indicate
	      the search engine's sequence of sites for this search (which we may use as an indicator of authority).
	'''	  
    def __init__(self):
        pass
    
    def deleteSearchContent(self, searchid):
	#deletes all the content bits for all the criteria associated with a search
	searchid = int(searchid)
	try:
	    criteriaObjects = self.getParseCriteriaForSearch(searchid)['criteria']
	except:
	    raise DbError("couldn't find filter criteria for search %i" %searchid)
	for c in criteriaObjects:
	    try:
		self.deleteContentForCriteria(c.id)	
	    except:
		raise DbError("couldn't delete content for search %i, criteria %i" %(searchid, c.id))
	return 
    
    def deleteSearchContentAndSites(self, searchid):
	#deletes the content and urls for a search
	searchid=int(searchid)
	self.deleteSearchContent(searchid)
	self.deleteUrlsForSearch(searchid)
	return 1

    def cleanUpData(self, searchid):
	#placeholder for ad hoc data cleaning routine for use w/ existing database
	return 1  
    
    def deleteContentForCriteria(self, criteriaid):
	criteriaid=int(criteriaid)
	try:
	    deleteList = models.Content.objects.filter(criteriaid=criteriaid)
	    deleteList.delete()
	    return 1
	except:
	    raise
    
    def gatherSearchSpecs(self, searchid= None):
        #pulls search specifications from db
        if searchid:
            try:     return models.Search.objects.filter(id=searchid)
            except:  raise DbError("Search requested: %s can't be found"%str(searchid))
            
    def gatherSearchIds(self, urlid = None):
        try:         return models.UrlSearch.objects.filter(urlid = urlid)
        except:      raise DbError("Lookup in urlSearch Failed for %i"%urlid)
    
    def addSingleUrl(self, url, deleteme = False, searchid = None, source = 'unknown', depth = 0, order = None, urlIx = 0):
        #adds a URL, updating tables Urls and Url_Search; returns the url id or an error
        urlobj = None
        try:         
            urlobj = models.Url(url = url, add_date = datetime.now(), delete_me = deleteme)
	    urlobj.save()
        except IntegrityError:
            logging.info("Failed to add duplicate url %s"%url)       
        except Exception, e:
            logging.info("addUrls encountered exception: %s while adding url %s"%(e, url))
            raise DbError("error inserting url %s"%url)
	
        #If we have added the url succesfully (or it's a duplicate) also update the url_search table (note, 'order' is optional - intended to handle
        #  record the search engines' idea of the relevance/authority)
        if urlobj:
            try:
		searchObj = models.Search(searchid)
                urlSearchObj = models.UrlSearch(urlid = urlobj, source = source, depth = depth, searchid = searchObj, urlorder = order)
		urlSearchObj.save()
		return urlobj.id                                
            except Exception, e:
                logging.info("addUrls encountered exception: %s while adding url %s to the urlSearch table"%(e, url))
                raise DbError("error inserting url %s: %s" %(url,e))
	
    def goodUrl(self, url):
        #Screens out obviously bad urls by name using a list stored in the BadUrlFragment table.  Also insures that they at least look
        #  legit http*.  The table contains strings like .pdf, .doc, .xls to weed out documents, along with names of sites we know we don't want.
        
        badFrags = models.BadUrlFragment.objects.all()
        badCount = badFrags.count()
	if badCount == 0:   #if we don't have any know bad url bits in our db, evaluate the url to be good
	    return True
        if url[:4].lower() <> 'http':
            return False
        good = True; ix = 0; done = False
        while not done:
            frag = badFrags[ix].badstring
            if url.find(frag) > 0:
                return False
            ix +=1
            if ix >= badCount: done = True
        return True    
                
                
    def addUrlsFromList(self, urls, deleteme = False, searchid = None, source = None, depth = 0, order = None):
        #add urls from a vetted list to the database

        if not isinstance(urls, list): #makes sure a single entry is treated as a short list
            urls = [urls]
        urlIx = 0
        for url in urls:
            urlIx=+1
	    url=url.strip()
            if self.goodUrl(url):  #screen out urls based on name
                try:
                    ret = self.addSingleUrl(url =  url, deleteme = deleteme, searchid = int(searchid), source = source, depth = int(depth), order =urlIx)
                except Exception, e:
                    logging.info("addUrls encountered exception: %s while adding url %s to the urlSearch table"%(e, url))
                    pass
                
        return RETURN_SUCCESS

    def deleteFlaggedUrls(self):
        #cleans up the database by deleting the rows with the deleteme flag set (affects both url and url_search)
        try:  
            deleteList = models.Url.objects.filter(delete_me=True)
	    deleteList.delete()
            return RETURN_SUCCESS 
        except Exception, e:
            logging.info("Failed to delete flagged urls.  %s"%e)
            raise 
    
    def deleteFlaggedSearches(self):
        #cleans up the database by deleting the rows with the deleteme flag set 
        try:  
            deleteList = models.Search.objects.filter(deleteme =True)  
	    deleteList.delete()
            return RETURN_SUCCESS 
        except Exception, e:
            logging.info("Failed to delete flagged searches.  %s"%e)
            raise

    def deleteUrlsForSearch(self, searchid):
	deletelist = models.UrlSearch.objects.filter(searchid = searchid)
	deletelist.delete()
	pass
        
    def addCatchFromUrlVisit(self, urlid, searchid, catchDict, urlAddDepth = 2, deleteme = False, criteriaid=None):
        '''Parse out the dict from a visit {content, metaData, links} and add to db.  We'll try to add dates
             to successfully-addded content).
        '''

        #update both content and contentSearch table
        contentSoup = catchDict['contentAsSoupObjects']
        contentUnicode = catchDict['polishedCont']
        for s, u  in zip(contentSoup,contentUnicode ):
            try:
                shortcont = u[:50]
                #try first to add the content; only if we do so will we try to parse out the date
                contObj = Content(content = u, shortcont = shortcont, dateacquired = datetime.now(), criteriaid = criteriaid, urlid=urlid)  
		csObj = ContentSearch(contentid = contObj.id, searchid = searchid, urlid = urlid)
                #parse the date
		date = None
                #logging.info( "trying to find a date in %s"%s)
                #date = findObj.findDate_main(s)
                if date:
                    contObj.dateposted = date
                    logging.info("found date: %s for content %s" %(str(date), shortcont))
                else: 
                    logging.info( "no date for content %s"%str(shortcont))
            except dberrors.DuplicateEntryError:
		#if we already have this content bit
                pass
            except Exception, e:
                msg = "couldn't add content %s for searchid %s and urlid %s"%(u,str(searchid), str(urlid))
                logging.info("%s: %s" %(msg, e))
                raise
            
        #delete existing metatags for this url then update with today's info
        try:
	    deleteList = models.UrlTags.objects.filter(urlid = urlid)
	    deleteList.delete()
            metaData = catchDict['metaData']
            for m in metaData:
                name, value = m
                urlTagObj = models.UrlTags(urlid =urlid, name = name[:20], value = value[:20])
		urlTagObj.save()
                
        except:
            msg = "couldn't add tags %s for searchid %s and urlid %s"%(value,str(searchid), str(urlid))
            logging.info(msg)
            raise      
        
        #Add any newly-harvested links to the url table.  Their depth will be one more than the initiating url's.  The urlAddDepth parameter allows us
        #  to control the amount of recursion.  A url added via google or an upload has a depth=0, urls captured from the initial ones have a depth=1, urls captured
        #  by following these links have a depth=3, and so on.
        urlSearchObj = models.UrlSearch.objects.filter(urlid = urlid, searchid = searchid)
        depth = urlSearchObj[0].depth + 1
        if depth <= urlAddDepth:
            links = catchDict['links']
            try:
                for link in links:
                    self.addSingleUrl(url = link, deleteme = deleteme, searchid = searchid, source = str(urlid), depth = depth)
            except dberrors.DuplicateEntryError:
                pass                
            except:
                logging.info("couldn't add new url %s"%link)
                raise 
            
            return RETURN_SUCCESS
    

    #"Getters" to return results of queries; all return iterable objects    
    def getUrl(self, urlid):
        #returns a url db object
        try:    models.URL.objects.filter(id = u.id).all()
        except: raise DbError("Url %s doesn't exist in url table"%str(urlid))
        
    def getAllUrls(self):
        try:    return models.Url.objects.all()
        except: raise DbError("getAllUrls failed")
	
    def getAllSearches(self):
        try:    return models.Search.objects.all()
        except: raise DbError("getAllSearches failed")	
	
    def getSearchesByUser(self, userid):
        try:    return models.Search.objects.filter(userid=userid)
        except: raise DbError("getAllSearches failed")		
	
    def getSearchesPublicOnlyNotUsers(self, userid):
	#gets searches that are public but not the user's
        try:    return models.Search.objects.filter(ispublic=True).exclude(userid=userid)
        except: raise DbError("getAllSearches failed")		
	
    def getSearchesPublicOnly(self):
	#gets searches that are public but not the user's
        try:    return models.Search.objects.filter(ispublic=True)
        except: raise DbError("getAllSearches failed")		
	
	
    def getContentForSearch(self, searchid, limit = None):
	ret = []
	contSearch =  models.ContentSearch.objects.filter(searchid = searchid)[:limit]  # a QureySet object
	for cont in contSearch:
	    contlist = models.Content.objects.filter(id = cont.id).all() 
	    for c in contlist:
		ret.append(c)
	return ret    
    
    def getViewCriteriaById(self, criteriaid):
	#returns a SearchViewcriteria object
	try:
	    criteriaObj = models.SearchViewcriteria.objects.get(id=int(criteriaid))
	    return criteriaObj
	except:
	    raise DbError("%s%i" %("couldn't fetch view criteria object ", int(criteriaid)))
	
    def updateViewCriteria(self, updatedict):
	'''updates ViewCriteria from a dict returned from views.editCriteria'''
	#parse out the dict
	searchid = updatedict['searchid']
	criteriaid = updatedict['criteriaid']
	include = updatedict['include']
	exclude = updatedict['exclude']
	andor = updatedict['andor']
	ispublic = updatedict['ispublic']
	title = updatedict['title']
	
	#add new info to the viewCriteria object
	vcObject = self.getViewCriteriaById(criteriaid)
	vcObject.include = include
	vcObject.exclude = exclude
	vcObject.andor = andor
	vcObject.ispublic = ispublic
	vcObject.title = title
	
	#update the database
	vcObject.save()

	    
    def getViewCriteria(self, onlyPublic=False, limit=None):
	#grabs the secondary search criteria for display in web page.  
	if not onlyPublic:
	    return models.SearchViewcriteria.objects.all()[:limit]
	else:
	    return models.SearchViewcriteria.objects.filter(isPublic = True)[:limit]
	
    def countContentForCriteria	(self, criteriaid):
	criteriaid=int(criteriaid)
	try: 
	    contentcount = self.getContentForCriteria(criteriaid = criteriaid).count()
	except:
	    raise
	return contentcount
        
    def getContentForCriteria(self, criteriaid, limit = None):
	criteriaid=int(criteriaid)
	ret = []
	contlist =  models.Content.objects.filter(criteriaid = criteriaid).order_by('-dateposted')[:limit]  # a QureySet object
	return contlist    
    
    def getContentForSearch(self, searchid, limit = None):
	ret = []
	#'latest' refers to the Content model's meta class variable 'get_latest_by'
	contlist =  models.ContentSearch.objects.filter(searchid = searchid)[:limit]  # a QureySet object
	return contlist      


    def cleanUpOrphanedContent(self):
	#cleans up content that belongs to no search
	for c in models.Content.object.all():
	    if models.ContentSearch.objects.filter(contentid = c.id).count() == 0:
		models.Content.delete(c.id)

	
    def getUrlsForSearchWithGoodHtml(self, searchid):
	ret = []
	allUrls = self.getUrlsForSearch(searchid)
	for url in allUrls:
	    htmlSelect = models.UrlHtml.objects.filter(urlid = url.id)
	    for h in htmlSelect:
		if len(h.html) >  10:
		    ret.append(h)
	return ret	    
	    
        
    def getHtmlForUrl(self, urlid):
        #find all content for a search
        try:    return models.UrlHtml.objects.filter(urlid = urlid)
        except: raise DbError("getHtmlForUrl failed") 
        
    def getSearchesforUrl(self, urlid):
        #find all searches associated with a url
        try:    return models.UrlSearch.objects.filter(urlid = urlid)
        except: raise DbError("UrlSearch failed")  
	
    def getScoreMethod(self, id = None):
        #find all searches associated with a url; if none provided, returns first method
	try:
	    if not id:
		allmethods = models.ScoreMethods.objects.all()
		ret = allmethods[0]
	    else: 
		ret = models.ScoreMethods.objects.filter(id = id)
	    return ret
        except: raise DbError("UrlSearch failed")  
	
    def getScore(self, contentid, methodid):
        #find all searches associated with a url; if none provided, returns first method
	try:
	    scoreObj = models.Scores.objects.filterBy(methodid = methodid, contentid = contentid)
	    score = scoreObj.score
        except: 
	    score = "n/a"
	return score    
	      
    def getUrlCountForSearch(self, searchid):
	#returns number of urls for this search
	try:
	    return self.getUrlsForSearch(searchid= searchid).count()
	except:
	    raise DbError("UrlCountForSearchFailed")
	
    def getContentCountForSearch(self, searchid):
	#returns number of content bits we have for this search
	try: 
	    return models.ContentSearch.objects.filter(searchid=searchid).count()
	except:
	    raise DbError("UrlCountForSearchFailed")
	
    def getUrlsForSearch(self, searchid, limit=None):
        #find urlSearch objects
        try:    return models.UrlSearch.objects.filter(searchid = searchid)[:limit]
        except: raise DbError("UrlSearch failed")  
	
    def getUrlsObjectsForSearch(self, searchid, limit=None):
        #find all urlObjects for a search
	urlSearchObjects = self.getUrlsForSearch(searchid, limit)
	retList = []
	for u in urlSearchObjects:
	    retList.append(u.urlid)  #returns URL objects (i.e., the whole db object)	
        try:    return retList
        except: raise DbError("getUrlsObjectsForSearch failed")  	
        
    def getParseCriteriaForSearch(self, searchid):
        ''''Find the search criterion associated with a search; 
          return a dict of searchid, object (since content is stored by search we need to keep these together)
	
	#Note:  This doesn't really belong here but until we have a wrapper around addition of new searches to force addition of
	  a serch criteria table entry, we'll add one here.  The criteria's exclude/enclude entries will echo the ones used on the
	  search engine.  They can easily be overridden.   
	'''
	criteria = models.SearchViewcriteria.objects.filter(searchid = searchid)
	if criteria.count() == 0:
	    try:
		s = models.Search.objects.filter(id = searchid)
		#models.SearchViewcriteria.objects.filter(searchid= searchid, exclude = s.exclude, include = s.include)	
		criteria = models.SearchViewcriteria.objects.filter(searchid = searchid)
	    except Exception, e:
		msg = "getParseCriteriaForSearch couldn't add a SearchViewcriteria object for search %i" %searchid
		logging.debug(msg + '  ' + e)
		raise DbError("getParseCriteriaForSearch couldn't add a SearchViewcriteria object for search %i" %searchid)
	    
        try:    return {'searchid': searchid, 'criteria': models.SearchViewcriteria.objects.filter(searchid = searchid)}
        except: raise DbError("SearchesCriteria failed")        
    
    def getParseCriteriaForUrl(self, urlid):
        #find the search criterion associated with a url (there may be many searches associated w/ a url)
        #  return a list of  dict of searchid, object (content is stored by search)
        criteria = []
        try:
            UrlSearchObjs = self.getSearchesforUrl(urlid)
            for s in UrlSearchObjs:
                criteria.append(self.getParseCriteriaForSearch(s.searchid))
            return criteria
        except: raise DbError("SearchesCriteria failed") 
        

    def getHtmlForSearch(self, searchid):
        #find all html for a search
        ret = []
        try:    
            urlObjs = self.getUrlsForSearch(searchid)
            for u in urlObjs:
                #if we've added html for this url, we'll get one item returned; otherwise the return will not have elem[0]
                try:
                    ret.append(models.UrlHtml.objects.filter(urlid=u.id)[0])
                except:
                    pass
        except: 
            raise DbError("Can't find html object")
            
        return ret       
    
    def deleteRawHtmlNoParse(self):
	urlhtml = self.getUrlHtmlObj()
	allrows = urlhtml.select()
	for row in allrows:
	    row.html = ''

	    
    def addUrlIdToContent(self, criteriaid, limit=None):
	'''one-off fix to add the urlid to the Content table; this due to long
	   delays in grabbing the url through a chain of lookups
	'''
	mycont = self.getContentForCriteria(criteriaid)[:limit]
	for c in mycont:
	    try:
		url = models.ContentSearch.objects.get(contentid=c.id).urlid.url 
		cont = models.Content.objects.get(id=c.id)
		cont.urlid = models.ContentSearch.objects.get(contentid=c.id).urlid
	    except:
		pass	    
	    
    def getContentAndUrlForCriteria(self, criteriaid, limit=None, first=None, methodid = None):
	'''
	Finds content bits in db using keywords in the Criteria table.  Returns a list of dict
	items carrying the content, url.  To facilitate the "next" and "back" buttons, the dict
	also contains the index of the first record (i.e., the list index, not the id field) and the
	number of matching content records found.
	
	'''
	allRecords = self.getContentForCriteria(criteriaid)
	first = first or 0  #ensures we have an integer to work with
	mycont = allRecords[first:first+limit]
	totalRecords = allRecords.count()
	
	#if we haven't set a scoring method, we'll use the first one in the database
	##TODO allow users to pick scoring method reported
	if not methodid:
	    methodObj = self.getScoreMethod()
	    methodid = methodObj.id
	ret =[]
	for c in mycont:
	    try:
		#url = models.ContentSearch.objects.get(contentid=c.id).urlid.url 
		url = c.urlid.url
		score = self.getScore(c.id, methodid)
		ret.append({"cont":c, "url": url, "first": first, "totalRecords": totalRecords, "score" : score})
	    except:
		pass
	return ret    
		       
       
 ### This might be overkill, but these simply return database objects to other modules           
        
    def getUrlHtmlObj(self):
        try:    return models.UrlHtml
        except: raise DbError("Can't find UrlHtml object")

    def getSearchObj(self):
        try:    return models.Search
        except: raise DbError("Can't find Search object")    
        
    def getContentObj(self):
        try:    return models.Content
        except: raise DbError("Can't find getContentObj object")         
        
    def getUrlSearchObj(self):
        try:    return models.UrlSearch
        except: raise DbError("Can't find UrlSearch object")           
        
    def getSearchViewCriteriaObj(self):
        try:    return models.SearchViewcriteria
        except: raise DbError("Can't find SearchViewCriteria object")     
        
    def getUrlSearchObj(self):
        try:    return models.UrlSearch
        except: raise DbError("Can't find UrlSearch object")     
	
    def addViewCriteria(self, searchid):
	#adds new viewCriteria to a search; returns criteria id
	include = ''; andor = 'and'
	search = self.getSearch(searchid)
	try: 
	    vc = models.SearchViewcriteria(searchid = search, include=include, andor = andor)
	    vc.save()
	except: 
	    raise DbError("Can's add new criteria")    
	return vc.id
	
    def addSearch(self, userid, name):
	#adds a search and returns the id
	try:
	    srch = models.Search(userid = userid, name = name)    
	    srch.save()
        except Exception, e:
            logging.info("addUrls encountered exception: %s while adding url %s"%(e, url))
            raise DbError("error creating new search")	    	
	return srch.id   
    
    def getSearch(self, searchid):
	try:
	    return models.Search.objects.get(id = int(searchid))
	except:            
	    logging.info("couldn't return search %i" %searchid)
            raise DbError("error retrieving search %i" %searchid)
	
    def deleteSearch(self, searchid):
	searchid = int(searchid)
	try:
	    srch = self.getSearch(searchid)
	    srch.delete()
	except:            
	    logging.info("couldn't return search %i" %searchid)
            raise DbError("error retrieving search %i" %searchid)	    
	return 1
    
    def deleteCriteriaAndItsContent(self, criteriaid):	
	criteraid = int(criteriaid)
	try:
	    criteriaObj = models.SearchViewcriteria.objects.get(id=criteriaid)
	    criteriaObj.delete()
	except:
	    raise DbError("couldn't delete searchViewcriteria db object")	
	pass

	
    def updateSearch(self,  qdict):
	'''updates a search based on user input, using the dict returned from editsearch'''
	#get a search object
	srch = self.getSearch(int(qdict['searchid']))
	#inject text from the form
	if 'include' in qdict: srch.include = qdict['include'].strip()
	if 'exclude' in qdict: srch.exclude = qdict['exclude'].strip()
	if 'name' in qdict: srch.name = qdict['name']
	#when there are checkboxes on a form, they appear in the qdict object only if checked
	if 'andor' in qdict: 
	    srch.andor = 'and'
	else:
	    srch.andor = 'or'
	if 'ispublic' in qdict: 
	    srch.ispublic = 1
	else:
	    srch.ispublic = 0
	    
	#these aren't used by the editsearch form, buy may eventually be used by other UI forms
	if 'clearall' in qdict: srch.clearall = self.to_boolean(qdict['clearall'], 1, 0)
	if 'clearnonconform' in qdict: srch.clearnonconform = self.to_boolean(qdict['clearnonconform'], 1, 0)
	if 'deleteme' in qdict: srch.deleteme = self.to_boolean(qdict['deleteme'], 1, 0)
	
	try:
	    srch.save()
	except:
	    logging.warn("search edits not saved for search %i" %srch.id)
	return    
	
    def to_boolean(self, inp, onval, offval):
	#changes a check box value 'on'/'off' to boolean equivalent
	if inp == 'on':
	    return onval
	else:
	    return offval

    def _set_logger(self):
        #Our friend the logger. Sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
        #  at the top of this module).
        LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
        log_filename = LOGDIR + '/' + LOG_NAME
        logging.basicConfig(level=LOG_LEVEL,
                            format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_filename,
                            filemode='w')	
	
    def getSearchNumFromName(self, name):
	#simply return a search's number if its name is known
	allSearches = self.getAllSearches()
	found = False
	for s in allSearches:
	   if name.lower() == s.name.lower():
	       return s.id
	#if we're here, we've not found a search by that name
	return 0
        
class testDbRoutines(unittest.TestCase):
    def __init__(self):
        #some randomized urls (keeps unique constraint from interfering)
        self._urls = ["xyz.html"+ str(random.random()), "http://www.dogma.com"+ str(random.random()),
                      "http://www.dogma.com/test/"+ str(random.random()), "http://www.dogma.com/test?id=123"+ str(random.random())]
        self._urls1 = ["xyz.html"+ str(random.random()), "http://www.dogma.com"+ str(random.random()),
                       "http://www.dogma.com/test/"+ str(random.random()), "http://www.dogma.com/test?id=123"+ str(random.random())]

    def testAddUrlsFromList(self):
        #add a bunch of urls from a list
        clsObj = DatabaseMethods()
        ret = clsObj.addUrlsFromList(self._urls, deleteme = True, searchid = 0, source = 'test')
        assert ret is RETURN_SUCCESS


    def testDeleteUrls(self):
        #delete rows with deleteme flag set
        clsObj = DatabaseMethods()
        ret = clsObj.deleteFlaggedUrls()
        assert ret is RETURN_SUCCESS
        
    def testAddCatchFromUrlVisit(self):
        #
        clsObj = DatabaseMethods()
        searchObj = clsObj.getSearchObj()
        urlSearchObj = clsObj.getUrlSearchObj()
        
        #add placeholder search, url and urlSearch database entries
        fakeSearch = searchObj(include = "michigan, football", exclude = "osu", deleteme = True)
        fakeUrlId = clsObj.addSingleUrl(url = "http://fake"+str(random.random()), deleteme = True, searchid = fakeSearch.id, source = 'test')
        urlSearchObj(urlid = fakeUrlId, searchid = fakeSearch.id)
        
        #see if we can add a fake return from a url to the content table
        fakeCont = ['and a one'+str(random.random()), 'and a two'+str(random.random()), 'and a three'+str(random.random())]
        fakeDates= [datetime.now(), datetime.now(), datetime.now()]
        fakeLinks= ['http://www.dogma.com'+str(random.random()), 'http://www.karma.com'+str(random.random()), 'http://www.fang.com'+str(random.random())]
        fakeMeta = [(u'http-equiv', u'Content-Type'), (u'content', u'text/html; charset=%SOUP-ENCODING%')]
        fakeDict =  {'polishedCont': fakeCont, 'dates':fakeDates, 'links': fakeLinks, 'metaData':fakeMeta,'contentAsSoupObjects':  fakeCont}
        ret = clsObj.addCatchFromUrlVisit(urlid = fakeUrlId, searchid = fakeSearch.id, deleteme=True, catchDict = fakeDict)
        clsObj.deleteFlaggedSearches()
        assert ret == RETURN_SUCCESS
        
    def installSomeFakeRecords(self):   
        srch = models.Search(include = 'xx', exclude = 'yy, yy, yy', clearall = False, clearnonconform = True, viewcriteriaid = 1, andor = 'or', deleteme = True)
	srch.save()
        srchview = models.SearchViewcriteria(searchid = srch, include = 'xx', exclude = 'yy', andor = 'and')
	srchview.save()
        url = models.Url(url = 'http://www.python.org/?'+str(random.random()), add_date = datetime.now(), url_order = 1, delete_me = True, visit_date = datetime.now(), source = 'xxxx')
	url.save()
       # urlsrch = models.UrlSearch(urlid = url.id, searchid = srch.id)
      # urltags = models.UrlTags(urlid = url.id, name = 'xxx', value = 'yyy')
        urlsrch = models.UrlSearch(urlid = url, searchid = srch)
	urlsrch.save()
        urltags = models.UrlTags(urlid = url, name = 'xxx', value = 'yyy')
	urltags.save()
        urlhtml = models.UrlHtml(urlid = url, html = "test html")
	urlhtml.save()
        cont = models.Content(content = "mycontent"+str(random.random()), dateacquired = datetime.now(), dateposted = datetime.now(), shortcont = "shortcont"+str(random.random()))
	cont.save()
        #contsrch = models.ContentSearch(searchid = srch.id, urlid = url.id, contentid = cont.id)   
	contsrch = models.ContentSearch(searchid = srch, urlid = url, contentid = cont) 
	contsrch.save()
        return {'url': url.id, 'srch': srch.id, 'cont': cont.id}
        
    def testDatabaseReturnObjects(self):
        #this module returns a bunch of (sometimes nested) query results; we'll add some fake content then return it
        fakeDict = self.installSomeFakeRecords()
        url = fakeDict['url']
        srch = fakeDict['srch']
        cont = fakeDict['cont']
        #now return it
        methodCls = DatabaseMethods()
        logging.debug("results from testDatabaseReturnObjects")
        urls4srch =methodCls.getUrlsForSearch(srch)
        for u in urls4srch: 
            logging.debug('urls %s' %str(u))
            
        urls4srch =methodCls.getUrlsForSearch(srch)
        for u in urls4srch: 
            logging.debug('urls with limit %s' %str(u))            
            
        cont4srch = methodCls.getContentForSearch(srch)
        for u in cont4srch: 
            logging.debug('cont %s' %str(u))

            
        html4url = methodCls.getHtmlForUrl(url)
        for u in html4url: 
            logging.debug('html for url %s' %str(u))

        html4srch = methodCls.getHtmlForSearch(srch)
        for u in html4srch: 
            logging.debug('html for search %s'%str(u))    
	    

	    
    def testReferentialIntegrity(self):
	    #tests referential integrity of the database; first by adding a complete set of records then deleting the top level object
	    #  attempts to access dependent objects should fail if the cascading deletes work as expected
	    clsObj = models()
	    #
	    deleteme = True; include = 'michigan, football'; exclude = 'ohio state'; urlname = 'urlname'
	    search = clsObj.Search(name = 'test', include = include, exclude = exclude, deleteme = True)
	    criteria = clsObj.SearchViewcriteria(searchid = search.id, include = search.include, exclude = search.exclude, andor = search.andor)
	    url1 = clsObj.Url(url = urlname + str(random.random()))
	    urlsrch1 = clsObj.UrlSearch(urlid = url1.id, searchid = search.id)
	    url2 = clsObj.Url(url = urlname + str(random.random()))
	    urlsrch2 = clsObj.UrlSearch(urlid = url2.id, searchid = search.id)
	    cont = clsObj.Content(content = 'cont' + str(random.random()), shortcont = 'short' + str(random.random()))
	    contsrch1 = clsObj.ContentSearch(urlid = url1.id, contentid = cont.id, searchid = search.id)
	    
	    clsObj.Url.delete(url1.id)
	    
	    #These should all fail on the first command of each try block.  If not, it should raise an error
	    try:
		clsObj.Url.objects.filter(id = url1.id)
		raise WrapperError("DB Integrity failed")
	    except:
		    pass
	    try:
		    clsObj.UrlSearchUrl.objects.filter(id = urlsrch1.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass	
	    try:
		    clsObj.ContentSearchUrl.objects.filter(id = contsrch1.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass	
	    try:
		    clsObj.ContentUrl.objects.filter(id = cont.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass
	    
	    pass
			    

	
class testWebMethods():
   
    def __init__(self, methodObj):
	self.methodObj = methodObj
	
    def testGetViewCriteria_and_getContentForCriteria(self):
	#just make sure we can snag the SerchViewCriteria data
	
	try:
	    viewCriteriaObj = self.methodObj.getViewCriteria()
	    viewCriteriaObj = self.methodObj.getViewCriteria(onlyPublic=True)
	    viewCriteriaObj = self.methodObj.getViewCriteria(onlyPublic=False)
	except:
	    raise DbError("DB method getviewCriteria failed")
	#now, make sure we can read it (one way is to ensure that the mandatory 'include' column has something)
	for r in viewCriteriaObj:
	    assert len(r.include) >0
	#make a query to the content table to be sure this doesn't blow up
	for r in viewCriteriaObj:
	    mycont = self.methodObj.getContentForCriteria(r.id)
	    mycont = self.methodObj.getContentForCriteria(r.id, limit = 1)
	    #make sure we can try to get some content
	    for c in mycont:
		myId = c.id

    def testGetContentAndUrlForCriteria(self, criteriaLimit=None, contentLimit=None):
	#just make sure we can snag the SerchViewCriteria data
	from datetime import datetime
	try:
	    viewCriteriaObj = self.methodObj.getViewCriteria(limit=criteriaLimit)
	except:
	    raise DbError("DB method getviewCriteria failed")
	#now, make sure we can read it (one way is to ensure that the mandatory 'include' column has something)
	startCont = datetime.now()
	mycont = self.methodObj.getContentForCriteria(viewCriteriaObj[0].id)
	endCont = datetime.now()
	print "time to get content: %s" %str(endCont-startCont)
	#make a query to the content table to be sure this doesn't blow up
	for r in viewCriteriaObj:
	    startUrl = datetime.now()
	    mycont = self.methodObj.getContentAndUrlForCriteria(r.id, limit = contentLimit)
	    endUrl=datetime.now()
	    print "time to dig out urls: %s" %str(endUrl-startUrl)
	    a=1
	return "done"
    
class fixDb():
    #adds urlid to existing Content database - one-time fix
    def addUrlidToContent(self):
	dbMethods = DatabaseMethods()
	viewCriteriaObj = dbMethods.getViewCriteria()
	for r in viewCriteriaObj:
	    dbMethods.addUrlIdToContent(criteriaid=r.id)
    

if __name__=='__main__':
    
    #instansiate the class object
    test = testDbRoutines()


    #run the tests    

    #test.testDatabaseReturnObjects()
    #test.testAddUrlsFromList()
    #test.testAddCatchFromUrlVisit()
    #test.testDeleteUrls()
    testWeb = testWebMethods(DatabaseMethods())
    
    myret = testWeb.testGetContentAndUrlForCriteria(criteriaLimit=1, contentLimit=None)
    #mycont = testWeb.testGetViewCriteria_and_getContentForCriteria()

    #a=1


