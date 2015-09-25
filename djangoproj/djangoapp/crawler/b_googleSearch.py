'''
This module is a self contained routine to ransack Google for results around a query.  The main entry point is class
SearcherClass()::runSearchEngine.  Notes:
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
import string

#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

class SearcherClass():
   '''
   Search using google api, pulling the maximum hits; presently this needs to be wrapped in another routine to increment
   the initial position or the result set returned and to aggregate results from multiple calls
      -  include and exclude are comma-deliminted strings
   '''

   def __init__(self, max_results=64, results_per_query = 8, referer="http://google.com/", include=None, exclude=None, 
                key=None, position = 0, socket_timeout = 2,  **kwargs):
     
      
      #class variables are set upon instansiation (and are available to the instance)
      self._max_results = max_results
      self._include = include
      self._exclude = exclude
      self._referer = referer
      self._returnedUrls =[]
      self._set_logger()
      self._socket_timeout = socket_timeout
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
      #composes a search query to google and sends the associated http request
      if position >= self._max_results:
         return []
      reader = ReadUrl()
      #build a google-friendly parameter string, construct the URL and request header, pass along to opener routine
      params = urllib.urlencode({'q': self._query, 'v': '1.0', 'rsz': 'large', 'start': position})
      url = 'http://ajax.googleapis.com/ajax/services/search/web?%s' % (params)
      requestHeader = [("Referer", self._referer)]     
      self._urlContents = reader.openUrl(url = url, socket_timeout = self._socket_timeout, header = requestHeader)

      #go through the catch and load the urls into a list, first making sure we have *something* to look at
      if self._urlContents:
         try:
            #if we have urls, then use simplejson to parse them out into a dict w/ keys responseDatra
            self._doc = simplejson.loads(self._urlContents)
            
            #...and add a cleaned up version of them (i.e., no funky characters) to a list
            self._returnedUrls = []
            for element in self._doc['responseData']['results']:
               result = self._normalizeString(element['url'])
               if result:
                  self._returnedUrls.append(result)               
               
            logging.debug("GoogleSearcher finished: found %s matches" % len( self._returnedUrls))
         
         #if we ran into any issues, we'll just log them.  The return is just the initial (empty) list   
         except Exception , e: 
            logging.debug("GoogleSearcher had problem counting results %s" %e)
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
      
   def getMaxResults(self, include = None, exclude = None):
      '''
      runs all the google search engine to its max results with include and exclude (comma delimited) strings
      '''
      #these values are the max allowed by google
      max_results = 1000  
      results_per_query = 50 
      socket_timeout = 2
      gsearch = SearcherClass(include = include, exclude = exclude, max_results = max_results, 
                             results_per_query = results_per_query, socket_timeout = socket_timeout)
      
      position = 0
      results = []
      done = False
      while not done:
         #run the search engine
         engineReturn = gsearch.run_search_engine(include = include, exclude = exclude, position = position)
   
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


class TestGoogleSearch(unittest.TestCase):
   def __init__(self):
      self.max_results = 64  
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
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      assert isinstance (results, list)
      include = "5345, and, or, maybe, somewhat";  exclude = "cat, mouse"
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      assert isinstance (results, list)
      #exclude string only
      include = ""; exclude = "karma"
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)
      assert isinstance (results, list)
      #include string only
      include = "karma"; exclude = ""
      results = clsObj.run_search_engine(include = include, exclude = exclude, position = self.position)      
      assert isinstance (results, list)
       
if __name__ == '__main__':
   '''
   These put the google searcher through its paces
   searcher = SearcherClass()
   include = "karma, dogma"
   results = searcher._run_all_Google(include = include)
   '''
   
   #These run the tests
   test = TestGoogleSearch()
   test.runTests()
 