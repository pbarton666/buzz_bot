'''
Simple class for accessing and reading a url; returns the contents or A a UrlReadError ... essentialy it just pads out
   the standard urllib2 request, open, and read functions to try to keep them from breaking ungracefully.  Since there are so many
   things to go wrong external to this routine (web sites down, no connection to the internet, etc.), the errors are 
   trapped and logged, but not really handled - the idea being that if we return *anything* it's probably the content we're after.
   
   The UrlReadError is of type Exception.  We'll pass it out as the returned object.  Calling routines can choose to raise it, test 
      to see if it's an exception e.g.,   isException = isinstance(returnedObject, Exception)

Usage:
url_return = readUrl(<url as string>, <socket timeout as int>, (optional) headers as list of (value, key) tuples
Example:
url_return = readURL('http://python.org',2, [('referer', 'http://pes.org')].contents,

'''
import urllib2
import socket
import os
import logging
import unittest

LOG_NAME = "master.log"
LOG_LEVEL = logging.INFO

class UrlReadError(Exception):
   #a generic error for catching url-related errors
   def __init__(self, value):
      self.parameter = value
   def __str__(self):
      return repr(self.parameter)

class ReadUrl(object):
   def __init__(self, url=None, socket_timeout=None, header=[]):
      #set a logger to work within an instance of this class
      import logging
      self._set_logger()
      self._socket_timeout = socket_timeout or 2
      self.contents = None
      #self.openURL( url, self._socket_timeout)
      self.header = header

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
      
   def _normalizeString(self, inputString):
      #replaces non-latin characters with latin ones; if it's not fixable, we'll return None
      try:
         inputString.encode('latin1', 'replace')
         return inputString
      except:      
         msg = "the string %s is too funky to be redeemed" %inputString
         logging.debug(msg)
         return UrlReadError(msg)      
      
   def openUrl(self, url, socket_timeout, header = []):
      #tries to open url in question, returns either the result or None
      try:
         #sets the timeout for the returns
         socket.setdefaulttimeout(self._socket_timeout)  
         #build a request object (this can be supplemented later with header data - originator, bot flag, etc.)
         req_obj = urllib2.Request(url)
         #if a header has been provided, add it; this assumes the input is a list of (key,value) pairs
         for h in header:
            key, val = h
            req_obj.add_header(key, val)
         #send the request out
         self._return_object = urllib2.urlopen(req_obj) 
      
      #we're not actually handling these exceptions, but we'll log them separately.
      except urllib2.HTTPError :  #bad request, or server rejected it
         msg = "the server at %s rejected our request: " %url
         logging.debug(msg)
         #raise UrlReadError(msg)  
      except urllib2.URLError:  #either the network is down or the server doesn't exist
         msg = "the server at %s can't be reached: " %url
         logging.info(msg)
         #raise UrlReadError(msg)  
      except Exception, e:  #we probably timed out 
         msg = "attempt to read %s failed: %s" %(url, str(e))
         logging.info(msg)
         #raise  UrlReadError(msg)  
      
      else:  #we've got *something*, so we'll read it and assign the results to the class variable .contents
         try: 
            self.contents = self._return_object.read()
            if len(self.contents) > 0:
               return self.contents
            else:
               msg = "We got null content from url %s " %url
               logging.info(msg)
               return UrlReadError(msg)
            return
         except:
            msg = "We got something, but couldn't read it, from url %s" %url
            logging.info(msg)
            return UrlReadError(msg)  

class TestOpenUrl(unittest.TestCase):
   def __init__(self):
      pass
   def runTests(self):
      reader = ReadUrl()
      #openUrl ought to return either an exception or a string
      assert isinstance(reader.openUrl('http://python.org', 2),str) or isinstance(reader.openUrl('http://python.org', 2), Exception)
      #an obviously bogus url should return an exception
      assert isinstance(reader.openUrl("http://dogmathedog.xxx",2), Exception)      
      
if __name__ == '__main__':
   test = TestOpenUrl()
   test.runTests()