'''
This class has routines for visiting gathering content from a url, file, or object.  The main access point is:

  CaptureContent::capture_main(name, streamType, include, exclude, minLength=100, andOr = "or", socket_timeout=None)
  
     name:            a fully specified file name (when streamType is 'f'), a url (streamType 'u'), or a file-like object containing
                      valid html (streamType 'o')
     include:         a list of terms that must appear in extracted content (andOr ['and'|'or'] provides the logic rule
     exclude:         a list of terms that cannot appear in extracted content (an 'or' rule is applied)
     socket_timeout:  time (seconds) to give a url to respond.

     Return is a dict of (content, metaData, links, dates).  The links are vetted per criteria in the projectSpecs import (terms like
        'blog'). The content and date lists go together i.e. content[0] is associated with dates[0].  The metaData is the header info
        from the url visited.
      
  CaptureContent::polishContent crudly filters the content to get rid of quotes (for the db), newlines, etc.  It needs work.    
   '''

#standard modules
import sys
import os
import codecs
import re
from datetime import datetime
import logging
from HTMLParser import HTMLParseError
import string

#parsing and text processing modules
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulSOAP
#from django.utils.encoding import smart_str, smart_unicode

#custom routines for opening urls, writing to the database, and extracting the dates from blog posts
import b_openUrl as opener
import findDate as dateFinder
import projectSpecs as projectSpecs #placeholder location for url accept/reject criteria

#instansiate imported classes
ancestorDepth = 20   #layers of nested, hierarchal url parse tree to use searching for dates
findObj = dateFinder.FindDateInSoup(ancestorDepth)
readUrl = opener.ReadUrl()

#a null datetime object for use as placeholder
NULLDATE = projectSpecs.NULLDATE

#logging specs
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG


class DataError(Exception):
   #a generic error for catching url-related errors
   def __init__(self, value):
      self.parameter = value
   def __str__(self):
      return repr(self.parameter)

class CaptureContent():    

   def __init__(self):
      self._set_logger()

   def capture_main(self, name, streamType, include, exclude, minLength=100, andOr = "or", socket_timeout=None):
      '''
       Capture the data for one fo a number of streamTypes:
         'f': name is a fully-specified filename (path + file)
         'u': a url to be opened and read
         'o': a text object
         Return a dict of the catch {content, metadata, links}
      
      '''
      try:
         rawData = self.acquire_data(name, streamType, socket_timeout)
      except:
         raise
      #parse the data
      soup = self.makeAndCleanSoup(rawData)
      if not isinstance(soup, Exception):
         #print "start " + str(datetime.now())
         metaData = self.captureMetaData(soup)
         #print "meta done " +str(datetime.now())
         links = self.captureLinks(soup)
         #print "links done " +str(datetime.now())
         contentAsSoupObjects = self.captureContent(soup, include, exclude, minLength, andOr)
         #These 'soupObjects' are navibable strings produced  by beautiful soup; they're convenient for the date parsing routine.  We'll
         #  pass both these and a unicode version to the calling routine
         polishedCont = self.polishContent(contentAsSoupObjects)
        # print "content done " +str(datetime.now())
         results = {'contentAsSoupObjects': contentAsSoupObjects, 'polishedCont': polishedCont, 'metaData': metaData, 'links':links}
         return results   
   
   def polishContent(self, content):
      #Cleans up the 'navigible string' version of the content into a report-worthy version
      contAsString = []
      for c in content:
         contAsString.append(unicode(c))
      retCont = []
      for c in contAsString:       
         unic = c
         unic = unic.replace('\n', ' ')  #newline
         unic = unic.replace('\t', ' ')  #tab
         unic = unic.replace('"', '``')  #quotes  TODO:  figure out a way to put into database w/o these substitutions
         unic = unic.replace("'", "`")
         unic = string.strip(string.join(string.split(unic)))  #this removes extra spaces
         retCont.append(unic)
      return retCont
   
   def captureDates(self, content):        
      '''
      Tries to match a date up with a content bit using the dateParser.
      '''
      #First parse out the good parts of the soup object to pass along.
      text = unicode(soup.body)
      retDates=[]
      for c in content:
         myDate = findObj.findDate_main(c, text)
         if myDate:
            retDates.append(myDate)   
         else:
            retDates.append(NULLDATE)  
         a=0   
        
      return retDates   
    
   def captureMetaData(self, soup):   
      #grab tags and other metadata from the header; BS creates a "attrs" property, which is a dict of the 
      #  metadata it parsed out.  There may be more than one meta tag, and they may be empty.  We'll return a list
      #  of (key, value) tuples if we can.
      myMeta = []
      try:
         myMeta = soup.meta.attrs
      except:
         pass
      return myMeta
        

   def captureLinks(self, soup, minLength = 100):   
      '''Grab the links.  We'll do a little filtering here with criteria stashed in b_dbSpecs for now.  We'll want to move these out to the database.  Presently
         these criteria screen for the following:
             - "#" indicates a bookmark to another point in the page - we don't want these 
             - we'll screen out anything that doesn't have "blog" in url (eliminates most advertising, videos, etc.)  
             - "=" usually is a submit/post button
             - anything obviously old (contains 2005 - 2008)
      '''   
      ##TODO: move the filtration criteria from the specs file out to a database

      rawLinks = soup.findAll("a")  #returns all the <a > tags
      links = []

      #build a list of qualified links
      for lnk in rawLinks:
         goodUrl = False
         if lnk.has_key('href'):
            #need to coherse the url to unicode, else the ascii codec barfs on anything it thinks is unicode
            href = unicode(lnk['href'])
            #a list of mandatory terms (placeholder is "blog"); any non-match makes goodUrl False
            for mandatoryWord in projectSpecs.linkInclude:
               if mandatoryWord in href.lower(): 
                  goodUrl = True
               else: 
                  goodUrl = False 

               #a list of excluded words; the presence of any makes goodUrl False    
            if goodUrl:
               for excludeWord in projectSpecs.linkExclude:
                  if excludeWord in href.lower(): 
                     goodUrl = False

            if goodUrl:               
               links.append(href)

         #remove them from the parse tree (we're not doing anything more here, and it confuses the content search)
         lnk.extract()

      #return a list of any links found (it's empty if none found)  
      return links
   
   def _addToListCountDups(self, masterList, candidates):
      '''
      Kludge to develop a list that screens out duplicates.   Also, it keeps track of the number of times a candidate
      was a duplicate of something on the list.  The idea is that if we have three sources of candidates, and we attempted
      to add the same thing three times, we know that item exists in all the sources (a sleazy "and" test).
      
      Assumes the masterList is a list of tuples(integer, anything)
      
      It returns an updated list
      '''
      #typecast candidates to a list (there might be just one - a string, maybe)
      if not isinstance(candidates, list): candidates = [candidates]
      
      retList = []
      #our working list starts out as the masterList, but gets updated with every new candidate object
      workingList = masterList
      for c in candidates:
         retList = []
         isDup = False
         for m in workingList:
            count, item = m
            if c == item:  
               #this is a duplicate - increment the counter 
               isDup = True
               retList.append((count + 1, item))
            else:
               retList.append(m)
         #if our text is not a duplicate, add the candidate object      
         if not isDup:      
               retList.append((1, c))
         workingList = retList      
      return retList

   def captureContent(self, soup, include, exclude=None, minLength=100, andOr="or"):   
      '''We'll capture all the content matching our criteria to a master list.  
      '''
      allInclude = []
      include = include.split(',')
      if exclude:
         exclude = exclude.split(',')
      else:
         exclude = []
         
      #Create a master list of (count, content) for the captured text.  "Count" is how many of the terms in
      #  "include" returned the same bit of content.
      for i in include:
         txtfound = soup.findAll(text = re.compile(i, re.I)) #re.I makes it case-insensitive
         for t in txtfound: 
            #t=string.strip(string.join(string.split(t))) #eliminates extra spaces but sadly converts to text
            if len(t) >= minLength:
               #this qualifies based on content and length, now see if it's already in the list
               allInclude = self._addToListCountDups(allInclude, t)
               
      #Create a new list of only content to pass downstream for further filtering.  If we have an "and" flag, the content
      #  bit has to have a count equal to the number of "include" terms; with an "or" flag, all are passed along
      listForNextFilter = []
      for a in allInclude:
         count, content = a
         if andOr == "and":
            if count==len(include):
               listForNextFilter.append(content)
         else:  
            listForNextFilter.append(content)
            
      #now, drop any with mention of excluded words
      allIncludeFiltered=[]
      for a in listForNextFilter:
         good = True
         try:
            #for some reason [u''] 
            for e in exclude:
               if len(e) > 0:  #need this in case exclude is null i.e., [u''] 
                  if e.lower() in a.lower(): 
                     good = False
         except: #prevents null list from crashing
            pass
         if good: 
            allIncludeFiltered.append(a)    

      return allIncludeFiltered  

   def makeAndCleanSoup(self, rawData):
      #Invokes BeautifulSoup to parse the data.  If this fails, it tries BeaurifulSOAP.  It then strips out obviously unusable material
      try:
         soup = BeautifulSoup(rawData)
      except HTMLParseError, e:
         raise
      except Exception:
         try:
            soup = BeautifulSOAP(rawData)
         except:
            return DataError("couldn't parse the data with Beautiful<anything>")

      #get rid of any javascript and style
      for badtag in ['script', 'style', 'rdf', 'form','/font']:
         junk = soup.findAll(badtag) 
         for j in junk:
            j.extract()

      return soup  


   def read_file(self, filename):
      try:
         #the codecs.open routine handles unicode where the ordinary open routine does not
         rawData = codecs.open(filename, "r", "utf-8").read()
         return rawData
      except:
         return DataError("couldn't open file %s" %filename)   
   
   def acquire_data(self, name, streamType, socket_timeout = None):
      #Reads different data sources.  Currently files, html and file-like data objects, could be enhanced to access info via sockets, passive feeds, etc.
      try:
         if streamType == 'f':     #file
            html = self.read_file(name)
         elif streamType == 'u':   #url
            html = readUrl.openUrl(name, socket_timeout or 2)
         elif streamType == 'o':   #object
            html = name
         else: 
            raise DataError("unknown stream type %s"%streamType)
         return html
      except:
         raise
   
   def _set_logger(self):
      #this sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
      #  at the top of this module.)
      LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
      log_filename = LOGDIR + '/' + LOG_NAME
      logging.basicConfig(level=LOG_LEVEL,
                          format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S',
                          filename=log_filename,
                       filemode='w')

def test_main_from_file(): 
   #acquire data from a file, test1.htm, in same directory as the module
   clsObj = CaptureContent()
   fn = "test1.htm"
   include = ["Coach Rod"]
   exclude = ["Notre Dame"]
   minLength = 100
   andOr = "and"
   curdir =  os.path.join(os.path.dirname(__file__), ).replace('\\','/')
   results = clsObj.capture_main(name = curdir +"/"+ fn, streamType = "f", include = include, 
                     exclude = exclude, minLength = minLength, andOr = andOr, socket_timeout=None)
   return results

def test_content_only_from_obj():   
   #acquire data from a test html page built in cleanHtme::buildTestHtml
   clsObj = CaptureContent()
   name = dateFinder.buildTestHtml()
   soup = BeautifulSoup(name)
   exclude = []
   minLength = 10
   
   #we should have one html object with both 'dogma' and 'karma', three with any of these
   andOr = "and"
   include = ["dogma", "karma"]
   content = clsObj.captureContent(soup, include, exclude, minLength=minLength, andOr=andOr)
   assert len(content) == 1
   andOr = "or"
   content = clsObj.captureContent(soup, include, exclude, minLength=minLength, andOr=andOr)
   assert len(content) == 3  
   
   #we should have three with 'dogma' only, and one if we exclude mentions of 'fang'
   include = ["dogma"]   
   content = clsObj.captureContent(soup, include, exclude, minLength=minLength, andOr=andOr)
   assert len(content) == 3   
   exclude = ['fang']
   content = clsObj.captureContent(soup, include, exclude, minLength=minLength, andOr=andOr)
   assert len(content) == 1 
   
   #make sure when run from the main routine, the expected information is returned
   results = clsObj.capture_main(name = name, streamType = "o", include = include, exclude = exclude, minLength = minLength, andOr = andOr)
   assert len(results['polishedCont'])==1
   assert len(results['contentAsSoupObjects'])==1
   assert len(results['metaData'])==2
   assert len(results['links'])==2
   
def test_main_with_obj():   
   #acquire data from a test html page built in cleanHtml::buildTestHtml
   clsObj = CaptureContent()
   name = dateFinder.buildTestHtml()
   soup = BeautifulSoup(name)
   exclude = []
   minLength = 10
   streamType = "o"
   #we should have one html object with both 'dogma' and 'karma', three with any of these
   andOr = "and"
   include = ["dogma", "karma"]
   clsObj.capture_main(name, streamType, include, exclude, minLength, andOr, socket_timeout=None)  
   a=1
   ##TODO:  return an object here and run some real test

   
def test_AddToListNoDups():
   #this just tests the "addToListNoDups" method against known data
   clsObj = CaptureContent()
   mylist = []
   mylist.append((1, "karma"))
   mylist.append((1, "dogma"))
   mylist.append((1, "fang"))
   mylist.append((1, "rosco"))
   mylist.append((1, "baron"))
   originalLen = len(mylist)
   #attempting to add a duplicate should result in the counter increasing, but the list length not
   mylist = clsObj._addToListCountDups(mylist, "karma")
   assert len(mylist) == originalLen
   count, cont = mylist[0]
   assert count ==2
   
   #attempting to add a new item should succeed and report a count of 1
   newitem = "some cat"
   mylist = clsObj._addToListCountDups(mylist, newitem)
   assert len(mylist) == originalLen+1
   count, cont = mylist[len(mylist)-1]
   assert cont == newitem
   assert count ==1
   
   #attempting to add a list with two new items and two old ones should increase length by 2
   newitem = ["karma", "dogma", "kirby", "buzz"]
   originalLen = len(mylist)
   mylist = clsObj._addToListCountDups(mylist, newitem)
   assert len(mylist) == originalLen+2  
   a=1
 
def runtests():  
      
   test_content_only_from_obj()     #uses test html found in findDate to ensure correct content capture
   test_AddToListNoDups()            #tests the "addToListNoDups" method against known data
   test_main_with_obj()            #tests the main capture routine against test html in findDate

if __name__ == '__main__':
   runtests()

   pass

