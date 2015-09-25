'''
Classes to wrap up common tasks e.g., 'run a search, visit the urls, add content', or 'remove flagged content'

Class to employ one or more searchers and add returned urls to the database.  This is intended to be generic.  
The __init__ method to SearchAndAdd is passed an instance of the search module's main searcher class (called, 
cleverly enough SearcherClass in all instances).  The searcher modules have methods to run a single search or to
max out what the search engine will provide.  These are:
    run_search_engine(include, exclude, position)
    getMaxResults(include, exclude)
'''

#import standard module(s)
import logging
from datetime import datetime
from HTMLParser import HTMLParseError
from optparse import OptionParser
#third party modules
from sqlobject.dberrors import DuplicateEntryError
import sys
import random

#custom modules
import b_googleSearch as google
import b_bingSearch as bing
import b_dbRoutines as dbRoutines
#import django_dbRoutines as dbRoutines
import projectSpecs as projectSpecs
import captureContent
import scorer as scorerRoutines

#instansiate imported classes
dbUtils = dbRoutines.DatabaseMethods()
captureUtils = captureContent.CaptureContent()
searchers = [google.SearcherClass(),bing.SearcherClass()]
#these allow easy access to one or the other as a command line option
namedSearchers = {'google':google.SearcherClass(), 'bing': bing.SearcherClass()}
scorer = scorerRoutines.CountAndScore()

#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

#return codes 
RETURN_SUCCESS = projectSpecs.RETURN_SUCCESS
RETURN_FAIL = projectSpecs.RETURN_FAIL

class Visitor():
	'''Routines for visiting urls, parsing html, etc.  They import functionality from separate modules that: run search engines; capture content
	   from the urls; dig the date out of blog postings; and interact with the database.
	'''
	def __init__(self):
		self._defaultVisitInterval = 86400  #seconds, 86400 sec/day
	
	def dueToVisit(self, visitInterval, lastVisit=None):
		#figure out whether it's time to visit given how often we want to ping a site, when we last visited, and the current time
		weAreDue = True
		minInterval = visitInterval or self._defaultVisitInterval
		if lastVisit:
			elapsedTime = datetime.now() - lastVisit
			if elapsedTime.seconds < minInterval:
				weAreDue = False		
		return weAreDue
	
	def readAndStoreSingleUrl(self, urlid,  streamType, visitInterval = None, socket_timeout = 2):
		'''given a urlid, find the url, visit it, and store its html int he database 
		
		'''
		#usd visit interval passed in or the default 
		visitInterval = visitInterval or self._defaultVisitInterval
		
		try:
			urlObj = dbUtils.getUrl(urlid)
			url = urlObj.url
		except:
			msg = "Couldn't access the url %s"%str(urlid)
			raise
		
		try:
			#if we're due for a visit, go for it
			if self.dueToVisit(visitInterval, urlObj.visitDate):
				rawData = captureUtils.acquire_data(name = url, streamType='u', socket_timeout = socket_timeout)
				logging.info("We got content from url %i"%urlid)
				uRawData = unicode(rawData, errors = 'ignore') #the ignore flag drops bad unicode
				urlObj.visitDate = datetime.now()
				#check if we have an entry for this url in the urlHtml table
				htmlObj = dbUtils.getHtmlForUrl(urlid)
				#if we have an entry for this url, update the record; otherwise make a new one
				if htmlObj.count() >0:  #we can just update the current record
					htmlObj[0].html=uRawData
				else:	
					dbRoutines.UrlHtml(urlid = urlid, html = uRawData)
					
			##TODO write a routine to cull urls that can't be read for whatever reason 					
			urlObj.readSuccesses = urlObj.readSuccesses + 1		
			return RETURN_SUCCESS	

		except Exception, e:   #we don't really care why we can't load the data
			logging.info("Failed to load take from %s into database"%url)
			urlObj.readFailures = urlObj.readFailures+ 1
			raise
		
		return RETURN_SUCCESS

	def visitUrls(self, searchid = None, urlid = None, limit = None, visitInterval = None):  
		'''
		Visits url(s) in the database and loads its html to the database.  Mostly for testing, this can be limited:
		1.  If a urlid is provided, we only visit that url; 
		2.  If a searchid is provided we only visit urls for that search (up to limit if provided).		
		'''
		visitInterval = visitInterval or self._defaultVisitInterval
		
		if searchid: #return urls up to the limit ...
			urls = dbUtils.getUrlsForSearch(searchid)	
			urlCount = len(urls)
			urlIx = 0
			while urlIx < urlCount:  #... then visit each
				try:
					ret = self.readAndStoreSingleUrl(urlid = urls[urlIx].id, visitInterval = visitInterval, streamType = 'u')
				except Exception ,e:
					logging.info("url %i: %s"%(urls[urlIx].id, e))
					
				urlIx += 1		

		elif urlid:  #only visit the search specified (returns RETURN_SUCCESS if it's happy)
			try:
				return self.readAndStoreSingleUrl(urlid = urls[urlIx].id, visitInterval = visitInterval, streamType = 'u')
			except:
				logging.info("url %i"%urlid)
				
		else:   #Neither a searchid nor a urlid has been provided, so visit them all.  We'll
			#   do this by passing the request back to the top of this routine.
			allSearches = dbUtils.getAllSearches()
			for s in allSearches:
				searchid = s.id
				self.visitUrls(searchid = searchid, urlid = urlid, limit = limit, visitInterval = visitInterval)
				a=1	

		return RETURN_SUCCESS			
	
	def parseHtmlInDb(self, nukeHtmlFlag  = False,  urlAddDepth =1, urlid = None, searchid = None, limit = None):
		'''Finds  html stashed in the database (url table).  
		
		1.  If a searchid specified, parse all urls associated with the search, according to the search's parsing criteria
		2.  If a url is specified, find all the searches that use it.  Then parse it separately for each of the searches.
		3.  The parsed content is stored by search, so different bits of a blog might show up in different places
		4.  If the nukeHtmlFlag is set, the html will be deleted after all the parsing is complete

		'''
		urls = None
		
		if searchid: #create a list of urls up to the limit ...
			urls = dbUtils.getUrlsForSearch(searchid, limit = limit)		

		elif urlid:  #create a one-element list of the url object
			urls = [dbUtils.getUrl(urlid)]
			
		else: 
			urls = dbUtils.getAllUrls()
			urls = urls[0:limit]
			
		urlCount = urls.count()	
		
		#if we don't have valid urls (maybe a non-existing one was specified) declarer succes and return
		if urlCount ==0:
			logging.info("no valid urls to parse")
			return RETURN_SUCCESS
		
		#So far, so good.  Now loop thru the urls
		for url in urls:
			
			loopUrlid = url.id #this is for sanity, as urlid is an input parameter
			
			#create a list of parse criteria objects
			criteriaObjects = []
			if searchid:  #i.e., if searchid in arguments get the criterion for a single search
				criteriaObjects = [dbUtils.getParseCriteriaForSearch(searchid)]
			elif urlid:   #i.e., if urlid in arguments, get criteria for each search that uses the url
				criteriaObjects = dbUtils.getParseCriteriaForUrl(urlid)
			else:        #otherwise, we'll grab the criteria for the url in this loop
				logging.debug("getting parse criteria for url %i" %loopUrlid)
				criteriaObjects = dbUtils.getParseCriteriaForUrl(loopUrlid)				
				
			#find the html for this url
			htmlObj = dbUtils.getHtmlForUrl(loopUrlid)
			html = None
			if htmlObj.count() > 0:
				html = htmlObj[0].html
			
			#if the html is any good, parse away
			if html: 
				if len(html)> 0 and not url.deleteMe:
					#Go thru our criteria objects (note each is associated with a *search*, not a url - that's why 'loopSearchid'.
					for critDict in criteriaObjects:  #
						criteriaSelectObj = critDict['criteria']
						loopSearchid = critDict['searchid']
						#since a search can have a bunch of criteria, we'll parse separately for each
						for critObj in criteriaSelectObj:
							try:							
								#parse according to the include/exclude criteria
								capture= captureUtils.capture_main(name=html, streamType='o', include= critObj.include, exclude = critObj.exclude, 
												   minLength=10, andOr = critObj.andOr, socket_timeout=2)
								#...and add the content, new urls found to the database
								ret = dbUtils.addCatchFromUrlVisit(urlid = loopUrlid, searchid = loopSearchid, catchDict = capture,
												   urlAddDepth= urlAddDepth, criteriaid = critObj.id)
								'''if len(capture['polishedCont'])>0:
									logging.debug("For search %i, criteria %i added %s"%(loopSearchid, critObj.id, capture['polishedCont']))
								else:
									a=1
								'''	
								
							except HTMLParseError, e:
								#if we can't parse this html, flag it for deletion
								url.deleteMe = True
								logging.info(e)
								pass
							except Exception, e:
								logging.info("Can't parse out url %i %s:  %s"%(url.id, url.url, e))
							
			#when done with parsing this url's html w/ all parse criteria delete the html text	
			if nukeHtmlFlag:
				htmlObj = dbUtils.getHtmlForUrl(loopUrlid)
				htmlObj.html = None

		pass

   
class SearchAndAddUrls():
	'''Routines to run the search engines and add the take to the database
	'''
	def __init__(self, searcherClassList):
		self._searcherList = searcherClassList
		
	def addUrlsAllSearches(self):
		searchObj = dbUtils.getSearchObj()
		searches = searchObj.select()
		for s in searches:
			self.addUrlsForSearch(s.id)
		
	def addUrlsForSearch(self, searchid = None, deleteMe = False, include = None, exclude = None, doOrder = False):
		'''Runs all the search engines specified at instansiation and adds the urls found to the database.
		   If a searchid is specified, the criteria are taken from the database.  Otherwise, we'll look to the include and
		   exclude parameters for direction.
		   '''
		if searchid:
			dbResults = dbUtils.gatherSearchSpecs(searchid)
			searchDbObj=dbResults[0]
			if not isinstance(searchDbObj, Exception):
				include = searchDbObj.include
				exclude = searchDbObj.exclude
				for searcher in self._searcherList:
					results = searcher.getMaxResults(include = include, exclude = exclude)
					logging.info("found %i results from %s" %(len(results), searcher.engineName))
					retCode = dbUtils.addUrlsFromList(results, deleteMe = deleteMe, searchId = searchid, source = searcher.engineName, order = doOrder)
					if retCode == RETURN_FAIL:
						msg = "%s Failed to get results from %s"%(retCode, searcher.engineName)
						logging.info(msg)
						return WrapperError(msg)
			else: 
				msg = "Failed to gather search specs for search %i"%searchid
				logging.info(msg)
				raise WrapperError(msg)
		else:
			msg="No search id provided to addUrlsForSearch"
			raise WrapperError(msg)
	
	def _set_logger(self):
		#this sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
		#  at the top of this module).
		LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
		log_filename = LOGDIR + '/' + LOG_NAME
		logging.basicConfig(level=LOG_LEVEL,
					format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
					datefmt='%Y-%m-%d %H:%M:%S',
					filename=log_filename,
					filemode='w')	

class WrapperError(Exception):
	#a generic error for catching url-related errors
	def __init__(self, value):
		self.parameter = value
	def __str__(self):
		return repr(self.parameter)
	
class MainCls():
	'''
	Parses the options and serves as the ringmaster, dispatching tasks requested by said options
	'''
	def __init__(self):
		pass
	def _set_logger(self):
		#this sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
		#  at the top of this module).
		LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
		log_filename = LOGDIR + '/' + LOG_NAME
		logging.basicConfig(level=LOG_LEVEL,
				    format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
				    datefmt='%Y-%m-%d %H:%M:%S',
				    filename=log_filename,
				    filemode='w')	
		
	def main(self, testArgs=None):
		# testArgs is a stand-in for sys.argv (the command line arguments) and used for testing
		parser = OptionParser()
		
		# Indentify the options recognized
		parser.add_option("-e", dest = "engines", action="store_true", help = "Only run search engines")
		parser.add_option("-g", dest = "engineName",   help = "Run only named search google|bing")
		parser.add_option("-v", dest=  "visit",   action="store_true",   help = "Only visit urls and collect html")
		parser.add_option("-p", dest=  "parse",   action="store_true",   help = "Only parse html")
		parser.add_option("-u", dest = "url",     help = "Specify a url by its ID")
		parser.add_option("-s", dest = "search",  help = "Specify a search by its ID")
		parser.add_option("-l", dest = "limit",   help = "Maximum number of items to process")
		parser.add_option("-t", dest = "tests",   action="store_true", help = "Run tests")
		parser.add_option("-m", dest = "more",    action="store_true", help = "Tell me more")	
		parser.add_option("-o", dest = "setVisInt",action = "store_true", help = "(with visit) Override default visit interval")
		parser.add_option("-n", dest = "nukeHtml",action = "store_true", help = "(with parse) Destroys captured html after parsing")
		parser.add_option("-d", dest = "depth", help = "(with parse) Set maximum depth storing links")
		parser.add_option("-k", dest = "score",    action="store_true", help = "Score the content.  Use -k -f to force overwrite of existing scores.")
		parser.add_option("-f", dest = "forceScore",    action="store_true", help = "(with -k) forces overwrite of scores.")
		
		#testArgs are applied from __main__ and used for debugging (otherwise, we use the ones supplied at the command-line
		if testArgs:
			(options, args) = parser.parse_args(testArgs)
		else:
			(options, args) = parser.parse_args()		
			
		#gather the common flags
		urlid = None; searchid = None; visitInterval=None; limit = None; nukeHtml=None; engineName = None; urlAddDepth = None
		if options.url:
			urlid = int(options.url)
		if options.search:
			searchid = int(options.search)
		if options.setVisInt:
			visitInterval = .0001  #minimum time (seconds) between visits to a url - this allows immediate revisit
		if options.limit:
			limit = int(options.limit)          #number of items ot process
		if options.nukeHtml:
			nukeHtml = True
		if options.engineName:
			engineName = options.engineName
		if options.depth:
			urlAddDepth = int(options.depth)
		if options.score:
			if options.forceScore:
				scoresOverride = True
			else:
				scoresOverride = False
			

		#Perform the indicated task	
		#...run search engines only
		if options.engines: 
			if options.search:
				runEnginesFor(searchid = int(options.search), engineName = engineName)
			else:	
				runEnginesAllSearches(engineName = engineName)
		
		#...visit the urls in the database only
		if options.visit: 
			visitCls = Visitor()
			visitCls.visitUrls(searchid = searchid, urlid = urlid, limit = limit, visitInterval =visitInterval)
		
		#...parse the stored html only	
		if options.parse:  #invoke html parsing routines
			visitCls = Visitor()
			visitCls.parseHtmlInDb(nukeHtmlFlag  = nukeHtml,  urlid = urlid, searchid = searchid, limit = limit)

		#...score the captured content
		if options.score:
			scorer.countAndScoreAll(overwrite = scoresOverride)			
			
		#run the tests (except for the test that runs this class)
		if options.tests: #run the tests (except for the test that runs this class)
			runTests()
		
		#print the verbose version of help
		if options.more:
			msg = []
			msg.append('The bot does three basic things: gets urls from search engines; visits the urls; capturing ' )
			msg.append('the html; and applies screening criteria to find bits of content of interest.  When running ' )
			msg.append('routines, you can operate at a fairly granular level.  You can: ')
			msg.append('')
			msg.append(' Run all the search engines for all the searches: -e')
			msg.append(' Run one of the search engines: -e -g google ')
			msg.append(' Run one of the search engines for a single search: -e -g google -s <search id')
			msg.append('')
			msg.append(' Visit all the urls in the database not visited today: -v ')
			msg.append(' Visit all the urls regardless of when last visited: -v -o ')
			msg.append(' Visit urls associated with a search:  -v -s <search id> ')
			msg.append(' Visit urls associated with a search, limiting the  # of urls visited:  -v s <search id> -l <number visited>')
			msg.append('')
			msg.append(' Parse all the html in the database, storing content bits, metadata, and links: -p')
			msg.append(' Parse html for all urls for a search: -p -s <search id> ')
			msg.append(' Parse html for all urls for a search, up to a maximum number: -p -s <search id> -l <url limit> ')	
			msg.append(' Parse html for a single url (it may be used associated w/ different searches): -p -u <url id> ')
			msg.append(' Parse html for a single url, getting rid of the raw html after parsing: -p -u <url id> -n ')
			msg.append(' Parse html for a single url, setting max. "degrees of separation" (links to links ...) from search engine return: -p -u <url id> -d 2')
			msg.append(' To do everything, set separate instances as -e, -v, -p, -k (engines, visit, parse, score)')
			for m in msg:
				print m

			
			
			
###	
###*************************************** method wrappers triggered by command line options*********************************************
###
#runs all search engines against all searches specified and adds the urls found to the database
def visitUrl(searchid = None, urlid = None, limit = None, visitInterval = None):
	clsObj = Visitor()
	ret = clsObj. visitUrls(searchid, urlid, limit, visitInterval)
	
def runEnginesAllSearches(engineName = None): 	
	#If a search engine name is provided, override the 'searchers' list with a single entity; otherwise run all available
	if engineName:
		try:
			searchers = [namedSearchers[engineName]]
		except:
			print "Sorry, we don't use a search engine called %s" %str(engineName)
			return
		
	#otherwise do them all	
	else:
		searchers = []
		for s in namedSearchers.itervalues():
			searchers.append(s)		

	clsObj = SearchAndAddUrls(searchers)
	ret = clsObj.addUrlsAllSearches()
	
def runEnginesFor(searchid, engineName = None):
	#If a search engine name is provided, override the 'searchers' list (see top of this file) with a single entity; otherwise run all available
	if engineName:
		try:
			searchers = [namedSearchers[engineName]]
		except:
			print "Sorry, we don't use a search engine called %s" %str(engineName)
			return	
		
	#otherwise do them all	
	else:
		searchers = []
		for s in namedSearchers.itervalues():
			searchers.append(s)
	

	clsObj = SearchAndAddUrls(searchers)
	ret = clsObj.addUrlsForSearch(searchid = searchid)	
	

#visits all the html stored in the database, parses and adds the content (several searches might use the same html)		
def parseHtml(nukeHtmlFlag  = False,  urlAddDepth =None, urlid = None, searchid = None, limit = None):	  
	clsObj=  Visitor()	
	clsObj.parseHtmlInDb(nukeHtmlFlag=nukeHtmlFlag,  urlAddDepth=urlAddDepth, urlid=urlid, searchid=searchid, limit=limit)

def runTests():
	pass

###	
###*************************************** Tests*********************************************
###
	
def testVisitUrls():
	# tests different permutations of VisitUrls - success doesn't mean we've gotten content, just that it the visitor won't crash things
	dbTestCls = dbRoutines.testDbRoutines()
	visitorCls = Visitor()
	#add a test url
	fakeDict = dbTestCls.installSomeFakeRecords()
        urlid = fakeDict['url']
	searchid = fakeDict['srch']
	visitInterval = .000001  #seconds, forces revisit
	#try w/ url only
	ret = visitorCls.visitUrls( urlid = urlid, visitInterval = visitInterval)
	assert ret == RETURN_SUCCESS
	#try w/ searchid only
	ret = visitorCls.visitUrls( searchid = searchid, visitInterval = visitInterval)
	assert ret == RETURN_SUCCESS
	#try w/ searchid and limit
	ret = visitorCls.visitUrls( searchid = searchid, visitInterval = visitInterval)
	assert ret == RETURN_SUCCESS
	#try w/ searchid only
	ret = visitorCls.visitUrls( searchid = searchid, visitInterval = visitInterval)
	assert ret == RETURN_SUCCESS	
	a=1


def testOpts():
	pass

	
if __name__ == '__main__':

	if len(sys.argv) >1:  #run from command line
		clsObj = MainCls()
		clsObj.main()	

	if len(sys.argv) ==1:  #run from wing for debugging
		#makes some test runs on search 2
		searchid = 2	
		clsObj=MainCls()
		clsObj.main(testArgs = "-k  ".split())  
	
		visitCls = Visitor()
		visitCls.visitUrls(searchid = None, urlid = None, limit = None, visitInterval = None)	
	
		clsObj = MainCls()                                #instansiates class containing the option parser and main routing commands
		#these do everything
		
		'''
		clsObj.main(testArgs = "-e -s 2    ".split())        #runs search on all engines
		clsObj.main(testArgs = '-v -s 2  -o'.split())     #visits all urls 
		clsObj.main(testArgs = '-p -s 2    '.split())        #parses all content per content-level criteria 
		'''
		
		#these do a quick and dirty run thru w/ only google, then 10 visit/parse operations
		clsObj.main(testArgs = "-e  -s 2 -g google ".split())    #runs search  on google
		clsObj.main(testArgs = '-v -s 2  -l 10 -o  '.split())     #visits urls found, to a limit of 10 (even if visited recently)
		clsObj.main(testArgs = '-p -s 2 -l 10      '.split())         #parses the urls to a limit of 10		
		
		cont = dbUtils.getContentForSearch(searchid = searchid)	
		urls = dbUtils.getUrlsForSearchWithGoodHtml(searchid = searchid)
		a=1
		
	

		
'''	#a few utilities
	dbUtils.cleanUpOrphanedContent()
	dbUtils.deleteUrlsForSearch(9)
	cont = dbUtils.getContentForSearch(searchid = searchid)
	urls = dbUtils.getUrlsForSearch(searchid = searchid)
	urls = dbUtils.getUrlsForSearchWithGoodHtml(searchid = searchid)		
	a=1
'''	
