

import re

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
   @param text The HTML (or XML) source text.
   @return The plain text, as a Unicode string, if necessary.
   from Fredrik Lundh
   2008-01-03: input only unicode characters string.
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print "Value Error"
            pass
      else:
         # named entity
         # reescape the reserved characters.
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
         except KeyError:
            print "keyerror"
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)


if __name__=='__main__':
   tfile = open ('/home/pat1/workspace/djangoproj/djangoapp/LeoD/ReportDocs/test.txt', 'r')
   text = tfile.readlines()
   html_string='Blackout in a can; on some shelves despite ban'
   html_string = text[1]


   hexentityMassage = [(re.compile('&#x([^;]+);'),
   lambda m: '&#%d;' % int(m.group(1), 16))]
   
   import BeautifulSoup
   
   for h in text:
      html_string = h
      html_string1 = h
      soup = BeautifulSoup.BeautifulSoup(html_string,
                           convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES,
                           markupMassage=hexentityMassage)
      print 'before: ' + h + '\n' + 'after:  ' + str(soup)
      
      soup = BeautifulSoup.BeautifulSOAP(html_string,
                           convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES,
                           markupMassage=hexentityMassage)
      print 'SOAP before: ' + h + '\n' + 'after:  ' + str(soup)      
      print ' '
      pass
   
   
   #ctext = unescape(text)
   print ctext