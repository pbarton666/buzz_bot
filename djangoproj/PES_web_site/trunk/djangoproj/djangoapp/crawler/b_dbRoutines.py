'''
This module contains database routines that may be accessed with or without using a web framework.  All use SQLObject; this
adds a bit of overhead, but provides nice exception management.

The connection object is set locally based on parameters in the projectSpecs import.  We're using MySQL.  The database
schema is stored in a file called (cleverly enough) database schema.

Methods available:
    ManageURLs:
        addUrlsFromList(self, urls, deleteMe = False, searchId = None, source = 'test', depth = 0, order = None)
          - add a list of urls, optionally recording the order in which they appear; adds to url, url_search tables
        deleteFlaggedUrls() 
           - delete any rows with the deleteMe flag set to true
        addCatchFromUrlVisit
           - adds content, links, and tags from visited URL (assumes we know the searchid and urlid)
        
       
       
TODO:  optionally allow user to discard non-conforming content from the existing search database when changing search criteria
TODO:  search the database to add conforming content from other searches to current search

'''
#standard modules
from sqlobject import mysql, SQLObject, StringCol, dberrors, SQLObjectNotFound  #change the import to use dbs other than MySQL
from datetime import datetime
import logging
import unittest
import random
import test

#custom modules
import findDate as dateFinder
import projectSpecs


#instansiate imported classes
ancestorDepth = 20   #layers of nested, hierarchal url parse tree to use searching for dates
findObj = dateFinder.FindDateInSoup(ancestorDepth)

#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

#return codes 
RETURN_SUCCESS = projectSpecs.RETURN_SUCCESS
RETURN_FAIL = projectSpecs.RETURN_FAIL

#database parameters and connection object using specs from an external file; the connection object is global to this module
dbUser = projectSpecs.dbUser
dbPass = projectSpecs.dbPass
dbSchema = projectSpecs.dbSchema
dbHost = projectSpecs.dbHost
tableName_Url =projectSpecs.tableName_Url
tableName_Url_Tags= projectSpecs.tableName_Url_Tags
tableName_Url_Search = projectSpecs.tableName_Url_Search
tableName_Content = projectSpecs.tableName_Content
tableName_Content_Search =projectSpecs.tableName_Content_Search
tableName_Content_Score = projectSpecs.tableName_Content_Score
tableName_Search = projectSpecs.tableName_Search
tableName_Metasearch_Search =  projectSpecs.tableName_Metasearch_Search
tableName_Url_Html = projectSpecs.tableName_Url_Html
tableName_Search_Viewcriteria = projectSpecs.tableName_Search_Viewcriteria
tableName_Negationwords = projectSpecs.tableName_Negationwords
tableName_BadUrlFragment = projectSpecs.tableName_BadUrlFragment
tableName_Poswords = projectSpecs.tableName_Poswords
tableName_Negwords = projectSpecs.tableName_Negwords
tableName_Obscenewords = projectSpecs.tableName_Obscenewords
tableName_Scoremethods = projectSpecs.tableName_Scoremethods
tableName_Scores = projectSpecs.tableName_Scores
tableName_Wordcount = projectSpecs.tableName_Wordcount

conn = mysql.builder()(user=dbUser, password=dbPass, host=dbHost, db=dbSchema, use_unicode = True)

###Database Objects###
class Url(SQLObject):
    #An object to represent the table 'Urls'
    _connection = conn     #set the connection object
    class sqlmeta:	
        fromDatabase = True     #uses db table names and characteristics
        table = tableName_Url   #this allows the table to be called something besides the class name

class UrlSearch(SQLObject):
    #Representes relates search id, order, depth to the url
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Url_Search  

class Search(SQLObject):
    #Representes meta information for the url
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Search 
        
class BadUrlFragment(SQLObject):
    #Representes meta information for the url
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_BadUrlFragment         
        
class UrlTags(SQLObject):
    #Representes meta information for the url
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Url_Tags 	
        
class UrlHtml(SQLObject):
    #Representes meta information for the url
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Url_Html         
        
class Content(SQLObject):
    '''Representes meta information for the url.  A couple o'notes here.  The db filed 'content'
       is specified as a text type (56k).  However, MySQL won't index anything bigger than a VARCHAR(256),
       so we can't make content a unique key.  To get around this, I've put in another column called 'shortCont'
       to hold the first 50 characters of content.  Ugly but effective.
    '''   
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Content        

class ContentSearch(SQLObject):
    #Representes grouping of searches in to a metasearch object (allows similar ones to be combined easily)
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Content_Search 	
    
class SearchViewcriteria(SQLObject):
    #Representes grouping of searches in to a metasearch object (allows similar ones to be combined easily)
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Search_Viewcriteria       
	
class NegationWords(SQLObject):
    #Negation words e.g., not, nor
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Negationwords 
	
class PosWords(SQLObject):
    #Positive words
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Poswords 
	
class NegWords(SQLObject):
    #Negative words
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Negwords 
	
class ObsceneWords(SQLObject):
    #List of obscene words
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Obscenewords  
	
class ScoreMethods(SQLObject):
    #Methods for scoring
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Scoremethods  
	
class Scores(SQLObject):
    #Scores for each bit of content, for each scoring method
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Scores 
	
class WordCount(SQLObject):
    #Number of pos, neg, obscene words
    _connection = conn   
    class sqlmeta:
        fromDatabase = True     
        table = tableName_Wordcount  
			
        

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
    
    def gatherSearchSpecs(self, searchid= None):
        #pulls search specifications from db
        if searchid:
            try:     return Search.selectBy(id=searchid)
            except:  raise DbError("Search requested: %s can't be found"%str(searchid))
            
    def gatherSearchIds(self, urlid = None):
        try:         return UrlSearch.selectBy(urlid = urlid)
        except:      raise DbError("Lookup in urlSearch Failed for %i"%urlid)
    
    def addSingleUrl(self, url, deleteMe = False, searchId = None, source = 'unknown', depth = 0, order = None, urlIx = 0):
        #adds a URL, updating tables Urls and Url_Search; returns the url id or an error
        urlobj = None
        try:         
            urlobj = Url(url = url, addDate = datetime.now(), deleteMe = deleteMe)
        except dberrors.DuplicateEntryError:
            logging.info("Failed to add duplicate url %s"%url)       
        except Exception, e:
            logging.info("addUrls encountered exception: %s while adding url %s"%(e, url))
            raise DbError("error inserting url %s"%url)
	
        #If we have added the url succesfully (or it's a duplicate) also update the url_search table (note, 'order' is optional - intended to handle
        #  record the search engines' idea of the relevance/authority)
        if urlobj:
            try:
                urlSearchObj = UrlSearch(urlid = urlobj.id, source = source, depth = depth, searchid = searchId, urlorder = order)
                return urlobj.id                                
            except Exception, e:
                logging.info("addUrls encountered exception: %s while adding url %s to the urlSearch table"%(e, url))
                raise DbError("error inserting url %s: %s" %(url,e))
	
    def goodUrl(self, url):
        #Screens out obviously bad urls by name using a list stored in the BadUrlFragment table.  Also insures that they at least look
        #  legit http*.  The table contains strings like .pdf, .doc, .xls to weed out documents, along with names of sites we know we don't want.
        
        badFrags = BadUrlFragment.select()
        badCount = badFrags.count()
	if badCount == 0:   #if we don't have any know bad url bits in our db, evaluate the url to be good
	    return True
        if url[:4].lower() <> 'http':
            return False
        good = True; ix = 0; done = False
        while not done:
            frag = badFrags[ix].badString
            if url.find(frag) > 0:
                return False
            ix +=1
            if ix >= badCount: done = True
        return True    
                
                
    def addUrlsFromList(self, urls, deleteMe = False, searchId = None, source = None, depth = 0, order = None):
        #add urls from a vetted list to the database

        if not isinstance(urls, list): #makes sure a single entry is treated as a short list
            urls = [urls]
        urlIx = 0
        for url in urls:
            urlIx=+1
            if self.goodUrl(url):  #screen out urls based on name
                try:
                    ret = self.addSingleUrl(url =  url, deleteMe = deleteMe, searchId = searchId, source = source, depth = depth, order =urlIx)
                except Exception, e:
                    logging.info("addUrls encountered exception: %s while adding url %s to the urlSearch table"%(e, url))
                    raise DbError("error inserting url %s"%url)
                
        return RETURN_SUCCESS

    def deleteFlaggedUrls(self):
        #cleans up the database by deleting the rows with the deleteMe flag set (affects both url and url_search)
        try:  
            Url.deleteBy(deleteMe =True)  
            return RETURN_SUCCESS 
        except Exception, e:
            logging.info("Failed to delete flagged urls.  %s"%e)
            raise 
    
    def deleteFlaggedSearches(self):
        #cleans up the database by deleting the rows with the deleteMe flag set 
        try:  
            Search.deleteBy(deleteMe =True)  
            return RETURN_SUCCESS 
        except Exception, e:
            logging.info("Failed to delete flagged searches.  %s"%e)
            raise

    def deleteUrlsForSearch(self, searchid):
	for s in UrlSearch.selectBy(searchid = searchid):
	    Url.delete(s.urlid)
        
    def addCatchFromUrlVisit(self, urlid, searchid, catchDict, urlAddDepth = 2, deleteMe = False, criteriaid=None):
        '''Parse out the dict from a visit {content, metaData, links} and add to db.  We'll try to add dates
             to successfully-addded content).
        '''

        #update both content and contentSearch table
        contentSoup = catchDict['contentAsSoupObjects']
        contentUnicode = catchDict['polishedCont']
        for s, u  in zip(contentSoup,contentUnicode ):
            try:
                shortCont = u[:50]
                #try first to add the content; only if we do so will we try to parse out the date
                contObj = Content(content = u, shortCont = shortCont, dateAcquired = datetime.now(), criteriaid = criteriaid)  
		csObj = ContentSearch(contentid = contObj.id, searchid = searchid, urlid = urlid)
                #parse the date
		date = None
                #logging.info( "trying to find a date in %s"%s)
                #date = findObj.findDate_main(s)
                if date:
                    contObj.datePosted = date
                    logging.info("found date: %s for content %s" %(str(date), shortCont))
                else: 
                    logging.info( "no date for content %s"%str(shortCont))
            except dberrors.DuplicateEntryError:
		#if we already have this content bit
                pass
            except Exception, e:
                msg = "couldn't add content %s for searchid %s and urlid %s"%(u,str(searchid), str(urlid))
                logging.info("%s: %s" %(msg, e))
                raise
            
        #delete existing metatags for this url then update with today's info
        try:
            UrlTags.deleteBy(urlid = urlid)
            metaData = catchDict['metaData']
            for m in metaData:
                name, value = m
                urlTagObj = UrlTags(urlid =urlid, name = name[:20], value = value[:20])
                
        except:
            msg = "couldn't add tags %s for searchid %s and urlid %s"%(value,str(searchid), str(urlid))
            logging.info(msg)
            raise      
        
        #Add any newly-harvested links to the url table.  Their depth will be one more than the initiating url's.  The urlAddDepth parameter allows us
        #  to control the amount of recursion.  A url added via google or an upload has a depth=0, urls captured from the initial ones have a depth=1, urls captured
        #  by following these links have a depth=3, and so on.
        urlSearchObj = UrlSearch.selectBy(urlid = urlid, searchid = searchid)
        depth = urlSearchObj[0].depth + 1
        if depth <= urlAddDepth:
            links = catchDict['links']
            try:
                for link in links:
                    self.addSingleUrl(url = link, deleteMe = deleteMe, searchId = searchid, source = str(urlid), depth = depth)
            except dberrors.DuplicateEntryError:
                pass                
            except:
                logging.info("couldn't add new url %s"%link)
                raise 
            
            return RETURN_SUCCESS
    

    #"Getters" to return results of queries; all return iterable objects    
    def getUrl(self, urlid):
        #returns a url db object
        try:    return Url.get(urlid)
        except: raise DbError("Url %s doesn't exist in url table"%str(urlid))
        
    def getAllUrls(self):
        try:    return Url.select()
        except: raise DbError("getAllUrls failed")
	
    def getAllSearches(self):
        try:    return Search.select()
        except: raise DbError("getAllSearches failed")	
	
    def getContentForSearch(self, searchid, limit = None):
	ret = []
 	if limit:
	    contSearch = ContentSearch.selectBy(searchid=searchid).limit(limit)
	else:
	    contSearch = ContentSearch.selectBy(searchid=searchid)
	for c in contSearch:
	    ret.append(Content.get(c.contentid))
	return ret    
        
    def getUrlsForSearch(self, searchid, limit = None):
        #find urls in urlSearch table
        urls = []
        try:
            if limit:
                urlsearch =  UrlSearch.selectBy(searchid = searchid).limit(limit)
            else:
                urlsearch =  UrlSearch.selectBy(searchid = searchid)
            for u in urlsearch:
		try:
		    urls.append(Url.get(u.urlid))      
		except SQLObjectNotFound: 
		    raise DbError("The UrlSearch table has entry for url %i, which doesn't exist" %u.urlid)
		    
            return urls
    
        except Exception, e:
            raise DbError("getUrlsForSearch failed")

    def cleanUpOrphanedContent(self):
	#cleans up content that belongs to no search
	for c in Content.select():
	    if ContentSearch.selectBy(contentid = c.id).count() == 0:
		Content.delete(c.id)

	
    def getUrlsForSearchWithGoodHtml(self, searchid):
	#for some searchid, return all the url ids for which we have harvested html
	ret = []
	allUrls = self.getUrlsForSearch(searchid)
	for url in allUrls:
	    htmlSelect = UrlHtml.selectBy(urlid = url.id)
	    for h in htmlSelect:
		if len(h.html) >  10:
		    ret.append(h)
	return ret	    
	    
        
    def getHtmlForUrl(self, urlid):
        #find all content for a search
        try:    return UrlHtml.selectBy(urlid = urlid)
        except: raise DbError("getHtmlForUrl failed") 
        
    def getSearchesforUrl(self, urlid):
        #find all searches associated with a url
        try:    return UrlSearch.selectBy(urlid = urlid)
        except: raise DbError("UrlSearch failed")  
        
    def getParseCriteriaForSearch(self, searchid):
        ''''Find the search criterion associated with a search (there's one per search); 
          return a dict of searchid, object (since content is stored by search we need to keep these together) 
	'''
	criteria = SearchViewcriteria.selectBy(searchid = searchid)
	if criteria.count() == 0:
	    try:
		s = Search.get(searchid)
		SearchViewcriteria(searchid= searchid, exclude = s.exclude, include = s.include)
		criteria = SearchViewcriteria.selectBy(searchid = searchid)
	    except SQLObjectNotFound:
		msg = "getParseCriteriaForSearch couldn't add a SearchViewcriteria object for search %i" %searchid
		logging.debug(msg)
	    except:
		raise DbError("getParseCriteriaForSearch couldn't add a SearchViewcriteria object for search %i" %searchid)
	    
        try:    return {'searchid': searchid, 'criteria': SearchViewcriteria.selectBy(searchid = searchid)}
        except: raise DbError("SearchesCriteria failed")        
    
    def getParseCriteriaForUrl(self, urlid):
        '''find the search criterion associated with a url (there may be many searches associated w/ a url)
         return a list of  dict of searchid, object (content is stored by search)
	 '''
        criteria = []
        try:
	    logging.debug("getting searches for url %i" %urlid)
            UrlSearchObjs = self.getSearchesforUrl(urlid)
	    logging.debug("succeeded")
            for s in UrlSearchObjs:
		logging.debug("getting parse criteria for search %i"%s.searchid)
                criteria.append(self.getParseCriteriaForSearch(s.searchid))
		logging.debug("succeeded.")
            return criteria
        except: raise #DbError("SearchesCriteria failed") 
        

    def getHtmlForSearch(self, searchid):
        #find all html entries for a search
        ret = []
        try:    
            urlObjs = self.getUrlsForSearch(searchid)
            for u in urlObjs:
                #if we've added html for this url, we'll get one item returned; otherwise the return will not have elem[0]
                try:
                    ret.append(UrlHtml.selectBy(urlid=u.id)[0])
                except:
                    pass
        except: 
            raise DbError("Can't find html object")
            
        return ret       
    
    def deleteRawHtmlNoParse(self):
	#deletes captured html
	urlhtml = self.getUrlHtmlObj()
	allrows = urlhtml.select()
	for row in allrows:
	    row.html = ''
	
    def haveWordCountForContent(self, contentid):
	#tests to see if we have word counts for a content block
	allWords = 0
	try:
	    wcRecord = WordCount.selectBy(contentid = contentid)
	    #do we have an entry in the WordCount table for this content?
	    if wcRecord.count() > 0:
		return True
	    else:
		return False
	except Exception, e:
	    raise DbError("error looking up word count for %i"%contentid)	
	
    def getWordCountFor(self, contentid):
	#returns the pos, neg, obscene word count for a content item
	try:
	    return WordCount.selectBy(contentid = contentid)
	except:
	    logging.info("Failed to get word count for content: %i"%contentid)
            raise 
	
    def updateWordCount(self, contentid, posWords, negWords, obsWords):
	#adds info to the WordCount table ('contentid' is really a content row object)
	try:
	    dbRow = WordCount.selectBy(contentid = contentid)
	    if dbRow.count() == 0:  #new entry
		newRow = WordCount(pos = posWords, neg = negWords, obscene = obsWords, contentid = contentid)
		a=1
	    else:
		dbRow[0].pos = posWords
		dbRow[0].neg = negWords
		dbRow[0].obs = obsWords
	except Exception ,e:
            logging.info("Failed to update word count for contentid %i %s" %(int(contentid.id), e))
            raise 
	a=1
	
    def getContent(self):
	try:
	    return Content.select()
	except:
            logging.info("Failed to find Content object")
            raise 	    
	    
    def getScoreMethods(self):
	try:
	    return ScoreMethods.select()
	except:
            logging.info("Failed to find ScoreMethods object")
            raise 

    def getScoreMethodFor(self, methodid):
	try:
	    return ScoreMethods.selectBy(id = methodid)
	except:
            logging.info("Failed to find ScoreMethods object")
            raise 	
	
    def getScoresObject(self):
	try:
	    return Scores.select()
	except:
            logging.info("Failed to find Scores object")
            raise	
	
    def getScoresObjectForContentMethod(self, contentid, methodid):
	try:
	    return Scores.selectBy(contentid = contentid, methodid = methodid)
	except:
            logging.info("Failed to find Scores object")
            raise
	return None
    
    def setScoreForContentMethod(self, score, contentid, methodid, overwrite):
	'''sets scores for a content id and scoring method (if there's already a record and overwrite = true)
	   adds new score if there isn't one
	'''
	scoreObj = self.getScoresObjectForContentMethod(contentid, methodid)
	scoreMethodsObj = self.getScoreMethodFor(methodid = methodid)
	if scoreObj.count() == 0:  #new entry
	    newRow = Scores(score = score, contentid = contentid, methodid = methodid)
	else:  
	    if overwrite: #update old entry if overwrite is True 
		scoreObj.score = score    	
    
    def generateWordListFrom(self, name):
	#Returns a list of the words found in a word list data table
	if name == 'pos': words = PosWords.select()
	if name == 'neg': words = NegWords.select()
	if name == 'obs':words =  ObsceneWords.select()
	ret = []
	for w in words:
	    ret.append(w.word)
	return ret 

       
 ### This might be overkill, but these simply return database objects to other modules           
        
    def getUrlHtmlObj(self):
        try:    return UrlHtml
        except: raise DbError("Can't find UrlHtml object")

    def getSearchObj(self):
        try:    return Search
        except: raise DbError("Can't find Search object")    
        
    def getContentObj(self):
        try:    return Content
        except: raise DbError("Can't find getContentObj object")         
        
    def getUrlSearchObj(self):
        try:    return UrlSearch
        except: raise DbError("Can't find UrlSearch object")           
        
    def getSearchViewCriteriaObj(self):
        try:    return SearchViewcriteria
        except: raise DbError("Can't find SearchViewCriteria object")     
        
    def getUrlSearchObj(self):
        try:    return UrlSearch
        except: raise DbError("Can't find UrlSearch object")     
	
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
        ret = clsObj.addUrlsFromList(self._urls, deleteMe = True, searchId = 0, source = 'test')
        assert ret is RETURN_SUCCESS


    def testDeleteUrls(self):
        #delete rows with deleteMe flag set
        clsObj = DatabaseMethods()
        ret = clsObj.deleteFlaggedUrls()
        assert ret is RETURN_SUCCESS
        
    def testAddCatchFromUrlVisit(self):
        #
        clsObj = DatabaseMethods()
        searchObj = clsObj.getSearchObj()
        urlSearchObj = clsObj.getUrlSearchObj()
        
        #add placeholder search, url and urlSearch database entries
        fakeSearch = searchObj(include = "michigan, football", exclude = "osu", deleteMe = True)
        fakeUrlId = clsObj.addSingleUrl(url = "http://fake"+str(random.random()), deleteMe = True, searchId = fakeSearch.id, source = 'test')
        urlSearchObj(urlid = fakeUrlId, searchid = fakeSearch.id)
        
        #see if we can add a fake return from a url to the content table
        fakeCont = ['and a one'+str(random.random()), 'and a two'+str(random.random()), 'and a three'+str(random.random())]
        fakeDates= [datetime.now(), datetime.now(), datetime.now()]
        fakeLinks= ['http://www.dogma.com'+str(random.random()), 'http://www.karma.com'+str(random.random()), 'http://www.fang.com'+str(random.random())]
        fakeMeta = [(u'http-equiv', u'Content-Type'), (u'content', u'text/html; charset=%SOUP-ENCODING%')]
        fakeDict =  {'polishedCont': fakeCont, 'dates':fakeDates, 'links': fakeLinks, 'metaData':fakeMeta,'contentAsSoupObjects':  fakeCont}
        ret = clsObj.addCatchFromUrlVisit(urlid = fakeUrlId, searchid = fakeSearch.id, deleteMe=True, catchDict = fakeDict)
        clsObj.deleteFlaggedSearches()
        assert ret == RETURN_SUCCESS
        
    def installSomeFakeRecords(self):   
        srch = Search(include = 'xx', exclude = 'yy, yy, yy', clearAll = False, clearNonconform = True, viewcriteriaid = 1, andOr = 'or', deleteMe = True)
        srchview = SearchViewcriteria(searchid = srch.id, include = 'xx', exclude = 'yy', andOr = 'and')
        url = Url(url = 'http://www.python.org/?'+str(random.random()), addDate = datetime.now(), urlOrder = 1, deleteMe = True, visitDate = datetime.now(), source = 'xxxx')
        urlsrch = UrlSearch(urlid = url.id, searchid = srch.id)
        urltags = UrlTags(urlid = url.id, name = 'xxx', value = 'yyy')
        urlhtml = UrlHtml(urlid = url.id, html = "test html")
        cont = Content(content = "mycontent"+str(random.random()), dateAcquired = datetime.now(), datePosted = datetime.now(), shortCont = "shortCont"+str(random.random()))
        contsrch = ContentSearch(searchid = srch.id, urlid = url.id, contentid = cont.id)   
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
            
        urls4srch =methodCls.getUrlsForSearch(srch, limit = 1)
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
	    clsObj = DatabaseMethods()
	    #
	    deleteMe = True; include = 'michigan, football'; exclude = 'ohio state'; urlname = 'urlname'
	    search = clsObj.Search(name = 'test', include = include, exclude = exclude, deleteMe = True)
	    criteria = clsObj.SearchViewcriteria(searchid = search.id, include = search.include, exclude = search.exclude, andOr = search.andOr)
	    url1 = clsObj.Url(url = urlname + str(random.random()))
	    urlsrch1 = clsObj.UrlSearch(urlid = url1.id, searchid = search.id)
	    url2 = clsObj.Url(url = urlname + str(random.random()))
	    urlsrch2 = clsObj.UrlSearch(urlid = url2.id, searchid = search.id)
	    cont = clsObj.Content(content = 'cont' + str(random.random()), shortCont = 'short' + str(random.random()))
	    contsrch1 = clsObj.ContentSearch(urlid = url1.id, contentid = cont.id, searchid = search.id)
	    
	    clsObj.Url.delete(url1.id)
	    
	    #These should all fail on the first command of each try block.  If not, it should raise an error
	    try:
		    dbRoutines.Url.get(url1.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass
	    try:
		    dbRoutines.UrlSearch.get(urlsrch1.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass	
	    try:
		    dbRoutines.ContentSearch.get(contsrch1.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass	
	    try:
		    dbRoutines.Content.get(cont.id)
		    raise WrapperError("DB Integrity failed")
	    except:
		    pass
	    
	    pass
			    
        

if __name__=='__main__':
    #instansiate the class object
    #test = testDbRoutines()
    #run the tests    
    
    
    '''these all work
    test.testDatabaseReturnObjects()
    test.testAddUrlsFromList()
    test.testAddCatchFromUrlVisit()
    test.testDeleteUrls()
    '''
    a=1


