'''
This module is a self contained routine to ransack Bing for results around a query.  The main entry point is class
SearchBing()::runSearchEngine.  Notes:
  - You'll want to substitute your own application key (self.key) if using it a lot
  - It depends on module b_openUrl.py (this wraps urllib2 functions)
  - The search takes two comman-delimited string variables (exclude and include)
  - The socket timeout is set to 2 seconds in __init__.  Nonetheless, it hangs for much longer than that if the internet
       connection is down.
  - The return is a list of urls (scrubbed for non-latin characters); the list is empty if a problem was encountered.
  - Errors and progress are logged to ./master.log by default.  Change in the log settings at the top of this module if desired.
'''

#standard modules
import urllib
import urllib2
import simplejson
import os
import string
import logging
import unittest
import string

#custom modules
from b_openUrl import ReadUrl
import projectSpecs


#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

class SearcherClass():
   '''
   Search using bing  api, pulling the maximum hits; presently this needs to be wrapped in another routine to increment
   the initial position or the result set returned and to aggregate results from multiple calls
      -  include and exclude are comma-deliminted strings
   '''

   def __init__(self, max_results=1000, results_per_query = 50, referer="http://dogma.com/", include=None, exclude=None, 
                key=None, position = 0, socket_timeout = 2,  **kwargs):
      
      #class variables are set upon instansiation (and are available to the instance)
      self.key = projectSpecs.bingSearchKey
      self._max_results = max_results
      self._include = include
      self._exclude = exclude
      self._referer = referer  #not used for bing, but retained for consistency w/ other searchers
      self._results_per_query = results_per_query
      self._returnedUrls =[]
      self._set_logger()
      self._socket_timeout = socket_timeout
      self._sources = "web"  #could also be "news", "image", "relatedsearch" and others (comma delimited)
      self.engineName = "google"
 
 
   def run_search_engine(self, include, exclude, position):
      '''
      Main entry point for this class.  It creates a query string based on search criteria and position (this is the Xth result to report)
        then runs the query on the search engine
        
      The return will be a list (maybe an empty one) of the urls found.  
      '''  
      
      query = u""
      if include:
         for phrase in include.split(","):
            if len(phrase)>0:
               query += u" \"%s\"" % str(phrase).strip()
      if exclude:         
         for phrase in exclude.split(","):
            if len(phrase)>0:
               query += u" -\"%s\"" % str(phrase).strip()   
      self._query = query    
      if query: 
         self._queryReturn = self._get_results(position)

      return self._queryReturn

   def _get_results(self, position):
      self._returnedUrls = []
      #composes a search query and sends the associated http request
      if position >= self._max_results:
         return self._returnedUrls
      reader = ReadUrl()
      
      #build a friendly parameter string, construct the URL and request header, pass along to opener routine      
      params = urllib.urlencode({'Appid' : self.key, "query" : self._query, 'sources' : self._sources, 
                                 'Web.Count' : self._results_per_query, 'Web.Offset': position})
      url = 'http://api.search.live.net/json.aspx?%s' %(params)
      #the request header is a list of (key, value) tuples and can be of any length (or a null string if none)
      requestHeader = ''   
       
      #open the url; if we have string version of the return, convert it to a dict
      try:
         return_obj = reader.openUrl(url = url, socket_timeout = self._socket_timeout, header = requestHeader)
      except:
         msg = "Bing Searcher couldn't get return object for url, but didn't catch the error: %s. "%url
         logging.debug(msg)
         return self._returnedUrls
      
      #if we have an exception (most likely a UrlReadError from the reader) the connection's probably down.
      if isinstance(return_obj, Exception):
         msg = "Bing Searcher didn't get a return.  The server is probably down."
         return self._returnedUrls
      
      #Try to convert the return to a dict; if we can't we're done
      try:
         self._urlContents = simplejson.loads(return_obj)
      except:   
         msg = "Bing Searcher coultn't convert the return to a dict; it's possibly malformed"
         logging.info(msg)
         return self._returnedUrls
         
      #make sure we have a SerchResonse item in the return object
      try:
         search_response = self._urlContents['SearchResponse']
      except:
         msg = "Bing searcher failed to return a SearchResponse object"
         logging.debug(msg)
         return self._returnedUrls
      
      #if we have errors, log them and return an error
      try:
         if 'Errors' in self._urlContents['SearchResponse']:
               resp = self._urlContents['SearchResponse']
               errors_list = [elem['Message'] for elem in resp['Errors']]
               error_text = ','.join(errors_list)
               logging.info("Bing Error: %s" %error_text)
               return self._returnedUrls
      except:  #no errors: so far, so good
         pass
         
      #go through the catch and load the urls into a list, using simplejson to parse the return into a dict
      try:
         for element in self._urlContents['SearchResponse']['Web']['Results']:
            result = self._normalizeString(element.get('Url'))
            if result:
               self._returnedUrls.append(result)                          
            
         logging.debug("BingSearcher finished: found %s matches" % len( self._returnedUrls))
      
      #if we ran into any unanticipated issues, we'll just log them and return the initial (empty) list   
      except Exception , e: 
         logging.debug("BingSearcher had problem parsing results %s" %e)
         pass
         
      return self._returnedUrls


   def _normalizeString(self, inputString):
      #replaces non-latin characters with latin ones; if it's not fixable, we'll return None
      try:
         inputString.encode('latin1', 'replace')
         return inputString
      except:      
         msg = "the string %s is too funky to be redeemed" %inputString
         logging.debug(msg)
         return None
      
   def all_perms(self, mylist):
      '''Borrowed from http://snippets.dzone.com/posts/show/753
      
      '''

       
      if len(mylist) <=1:
         yield mylist
      else:
         for perm in self.all_perms(mylist[1:]):
            for i in range(len(perm)+1):
               yield perm[:i] +mylist[0:1] + perm[i:]
      

   def _set_logger(self):
      #this sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
      #  at the top of this module.
      LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
      log_filename = LOGDIR + '/' + LOG_NAME
      logging.basicConfig(level=LOG_LEVEL,
                          format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S',
                          filename=log_filename,
                          filemode='w')
   
   def _createPermutations(self, csvString):
      #input is a csv string, return is a list of csv strings representing all permutations of the elements
      
      #create a list of the elements of the input...first making sure we have a valid string
      myreturn = []
      
      if csvString:
         testList = []
         for phrase in csvString.split(","):
            testList.append(str(phrase).strip())
         
         #each return is a list so convert back to a csv form 
         permutati0nGenerator = self.all_perms(testList)
         
         for retlist in permutati0nGenerator:
            myreturn.append(', '.join (retlist))
            
      return myreturn      
      
   def getMaxResults(self, include = None, exclude = None, testMode = None):
      #Runs all the search engine to get max results with include and exclude (comma delimited) strings; to maximize the return, we'll use
      #   all the permutations of the include list

      max_results = 1000        #max allowed is 1000
      results_per_query = 50    #max allowed is 50
      socket_timeout = 2        #arbitrary, but seems to work
      position = 0              #the results index (first is 0)
      results = []              #default results return is an empty list
      done = False
      
      if testMode:
         max_results = 100
         
      #instansiate the searcher object
      bsearch = SearcherClass(include = include, exclude = exclude, max_results = max_results, 
                             results_per_query = results_per_query, socket_timeout = socket_timeout)
      
      #run the search engine for every permutation of the search terms
      includePermutations = self._createPermutations(include)
      for include in includePermutations:

         #run the search engine iteratively until we've exhausted our max_results and results_per_query specs
         while not done:
            engineReturn = bsearch.run_search_engine(include = include, exclude = exclude, position = position)
      
            #add the urls to results; if this search is a bust (no results) we're done
            if len(engineReturn) > 0:
               for url in engineReturn:
                  results.append(url)
            else: 
               done = True
               
            #reset the position; if we've exceed the max_results then we're done
            position = position + len(engineReturn)
            if position > max_results:
               done = True
      return results


class TestBingSearch(unittest.TestCase):
   def __init__(self):
      self.max_results = 16  
      self.results_per_query = 8 
      self.socket_timeout = 2
      self.position = 1
      
   def runTests(self):
      #not much to test here - it works or it doesn't, but we'll throw a few searches at it to see if it will blow up; we should
      #  be able to tell if it doesn't return a list object (empty is OK)
      clsObj = SearcherClass(_max_results = self.max_results, _results_per_query =  self.results_per_query,
                            _socket_timeout = self.socket_timeout)
      
      #some exclude and include strings
      include = "dogma, dog, black";  exclude = "cat, mouse"
      
      
      #runs the getMaxResults in test mode
      results =  clsObj.getMaxResults(include = include, exclude = exclude, testMode = None)     
      
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      assert isinstance (results, list)
      include = "5345, and, or, maybe, somewhat";  exclude = "cat, mouse"
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      assert isinstance (results, list)
      #exclude string only
      include = ""; exclude = "karma"
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      #include string only
      include = "karma"; exclude = ""
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)    
      
   def testPermutations(self):
      #Test our permutation generators (they return all permutations of an input)
      clsObj = SearcherClass(_max_results = self.max_results, _results_per_query =  self.results_per_query,
                      _socket_timeout = self.socket_timeout)  
      
      #The first one takes a list
      testList = ['dogma', 'karma', 'fang']
      permutati0nGenerator = clsObj.all_perms(testList)
      for p in permutati0nGenerator:
         assert len(p) == len(testList)
         
      #the second one takes a csv string
      testList = 'dogma, karma, fang'  
      permutati0nGenerator = clsObj._createPermutations(testList)
      for p in permutati0nGenerator:
         assert len(p) == len(testList)
         
      a=1   
         
if __name__ == '__main__':
   
   #these commands run the routine using the main init specs
   '''   
      searcher = SearcherClass()
      include = "karma, dogma"
      exclude = "run over"
      results = searcher.getMaxResults(include = include, exclude = exclude)
      a=1
   '''

   #These run the tests   
   test = TestBingSearch()
   test.testPermutations()
   test.runTests()
   clsObj = SearcherClass()
   
 