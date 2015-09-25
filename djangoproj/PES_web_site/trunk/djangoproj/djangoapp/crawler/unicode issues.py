'''
I'm having trouble with unicode.  In a web page, this string exists:

   <a class="toggle" href="javascript:void(0)">\n<span class="zippy toggle-open">\xe2\x96\xbc&nbsp;</span>\n</a>
   
When I try to print it I get a UnicodeEncodeError.  This happens within the Wing IDE environment and also in a python shell from
a terminal window.  There's otherwise no problem handling it (making a copy of the containing object, etc.)

So, here's what I've tried:

 - opening the file with the urf-8 codec, which doesn't help
         html = codecs.open(curdir +"/"+ fn, "r", "utf-8").read()
 - updating the streamWriter object with the utf-8 codec, which doesn't help
         streamWriter = codecs.lookup('utf-8')[-1]
         sys.stdout = streamWriter(sys.stdout)
 - typecasting it to a string when printing (I think that's what happens, anyway), this works
         print "myline %s"%<text object>
 - using django's smartString, this also works
         from django.utils.encoding import smart_str
		 print smart_str(<text object>)
 - explicitly converting it to unicode, this also works
         cleantext = []
         for t in rawtext:
		     cleantext.append(unicode(t))
		 
 '''
from BeautifulSoup import BeautifulSoup, SoupStrainer, BeautifulSOAP
from django.utils.encoding import smart_str, smart_unicode

import codecs
import sys
streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)

import os
import b_openUrl as opener
import b_manageUrls as urlMgr

curdir =  os.path.join(os.path.dirname(__file__), ).replace('\\','/')
fn = "College Football Forum.html"
html = codecs.open(curdir +"/"+ fn, "r", "utf-8").read()
#html = codecs.open(curdir +"/"+ fn, "r").read()
soup = BeautifulSoup(html)
soup.currentTag
text = soup.fetch('a')
pos = 0
for t in text:
	try:
		print t
		print pos
	except:
		pass
a=1

a=1

