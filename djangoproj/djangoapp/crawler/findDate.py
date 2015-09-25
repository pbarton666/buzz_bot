'''Tools to guess a blog's posting date without knowing the blog site's layout, using BeautifulSoup.  
    FindDateInSoup::findDate_main(<BS object>, <ancestorDepth = integer> returns a datetime object or None

   It begins from the BS object passed in and works its way up the parse tree until it finds a date or it reaches an imposed
   limit on the "ancestorDepth", or how many levels up it can search.
   
   This approach has issues - particulary speed.  Each BS object encapsulates all subordinate objects so as we move up the tree 
   the string to search grows geometrically.  Also, the same (previously unfruitful) text is searched again at each level.
   
   I've played with the idea of extracting a previously-searched element to prevent revisition, but this has the problem of 'fratricide' - 
   if two relevant content chunks appear in the same post, the process of searching for the date can extract the others.  Revisit this 
   because it probably makes sense to simply reparse the url every time we look for a date as reparsing can be much faster.
      
'''
#standard modules    
import re
from datetime import datetime
import os
import logging

#parsing modules
from BeautifulSoup import BeautifulSoup
import philparser
parser = philparser.DateParser()

#log settings
LOG_NAME = "master.log"
LOG_LEVEL = logging.DEBUG

class FindDateInSoup():

    def __init__(self, ancestorDepth=100):
        self.depth = ancestorDepth
        self.parser = parser
        self._set_logger()

    def invoke_date_parser(self, txt):
        #invokes our date parser to figure out whether there's a date in this chunk of code.
        try:
            dateFound = self.parser.grabDate(txt)
            return dateFound
        except:
            msg = "parser had a problem with %s"%str(txt)
            return msg

        
    def NOTUSEDfindDate_mainMethod3(self, parseObj, objContents=None):
        '''
          This strips the content out of the content object then uses string methods to pass chunks of the original html
          to the date parser.  We'll start from the location of the content in the html and work up until we find a date.
          '''
        chunkToParse =800 #size of the piece to send to the date parser
        mydate = None
        try:
            #make a string version of the BS objects contents
            #objContents =''
            #for t in parseObj.findAllPrevious():    
            #    objContents = objContents+unicode(t)
            #find this in the original html    
            last = objContents.find(unicode(parseObj))   
            done = False
            while not done:
                #chop the html into chunks; this keeps parser from barfing, also date is probably close to content
                first = max(0, last - chunkToParse)
                ret = self.invoke_date_parser(objContents[first:last])
                #reset 'last' to provide a bit of overlap; this in case we chopped a good date in half
                last = first + 20 
                #we'll return the last date found (most proximate to the  content bit)
                if len(ret) > 0:
                    mydate = ret[len(ret)-1]
                    print "found %s"%(str(mydate))
                    return mydate
                
                if first == 0:
                    done = True
   
        #If we've encoundered an issue, we no longer have a parsable object (doesn't matter why), so give up    
        except: 
            return mydate        
        
    def NOTUSEDfindDate_mainMethod2(self, obj, objContents=None):
        '''
          Trys to find a valid date in the parse tree.  This method walks up the parse tree, deleting any
          branch that does not yield a date.  This works fine if we don't care about the parse tree.  I can't seem
          to be able to deep copy it, so any deletion on Copy A affects Copy B.  Re-parsing for every content bit is too
          expensive.
          '''
        chunkToParse =400 #size of the piece to send to the date parser
        mydate = None
        targetObj = obj
        curDepth = 0
        #
        while curDepth <= self.depth:  
            try:
                oldObj = targetObj
                targetObj = targetObj.findPrevious()                 
                #kill the old object and all its kids
                try:
                    kids = oldObj.childGenerator()
                    for k in kids:
                        k.extract()
                    oldObj.extract()      
                except:
                    pass

                objContents =""

                for t in targetObj:    
                    objContents = "%s %s"%(objContents, t)
                    
                if len(objContents) > 6:  #don't bother parsing really small pieces smaller than '1/1/01'      
                    ret = self.invoke_date_parser(objContents[:chunkToParse])
                    if len(ret) > 0:
                        mydate = ret[0]
                        return mydate

                        
                curDepth +=1   
                
            #If we've encoundered an issue, we no longer have a parsable object (doesn't matter why), so give up    
            except: 
                return mydate        
        
    def findDate_main(self, obj, objContents=None):
        '''
          Trys to find a valid date in the parse tree.  I haven't figured out a fool-proof way to do this given the diversity
          of blog architectures out there.  
          '''
        chunkToParse =400 #size of the piece to send to the date parser
        mydate = None
        targetObj = obj
        curDepth = 0
        #
        while curDepth <= self.depth:  
            try:
                oldObj = targetObj
                targetObj = targetObj.findPrevious()   
                #oldObj.extract()
                objContents =""
                '''
		 The parent object (objContents) is an "instance" object - basicly an iterator object that spawns navigable strings.
		 We'll concantenate it into a string, then pick off chunks to send to the date parser for analysis (this keeps the
		 parser from barfing on big strings; also the date is most likely to be at the top so we don't need to analyze the whole.
		'''
                for t in targetObj:    
                    objContents = "%s %s"%(objContents, t)
                
                #the parser is a bit inefficient, so we'll do a couple first order checks before we pass this along
                intInside = re.compile("\d").search(objContents, 1)  #searches for one instance of any integer; None type if not found
                if len(objContents) > 6 and intInside:       #also screen out chunks smaller than '1/1/01'      
                    ret = self.invoke_date_parser(objContents[:chunkToParse])
                    if len(ret) > 0:
                        mydate = ret[0]
                        return mydate
                curDepth +=1   
                
            #If we've encoundered an issue, we no longer have a parsable object (doesn't matter why), so give up    
            except: 
                return mydate

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

def buildTestHtml():    
    #Builds a faux html string for testing.  NB, for the links to be found they need to have one or more of the qualifying words
    #  e.g., 'blog' (these are found in the linkSpecs import).  This is used by the captureContent tests, as well.
    testHtml=[]
    testHtml.append("<html>")
    testHtml.append("<meta dog='Dogma' cookies='always'>")
    testHtml.append("<body>")    
    testHtml.append("<div> level 1.0 ")
    testHtml.append("       <div>level 1.0.1 </div>") #test2 starts looking for a date based on content found here; sibling has no date, but sibling's kids do
    testHtml.append("       <div>level 1.0.2 ")
    testHtml.append("          dogma karma fang")    
    testHtml.append("          <div>level 1.0.2.1 January 1, 2010</div>")
    testHtml.append("           dogma fang")    
    testHtml.append("          <div>level 1.0.2.2 April 1, 2010</div>")  #test1 starts here; sibling has date, which we want to find
    testHtml.append("       </div>")
    testHtml.append("</div>")
    #
    testHtml.append("<div> level 2.0 May 1, 2010")
    testHtml.append("   <div> level 2.1 ")
    testHtml.append("          dogma")    
    testHtml.append("        <div> level 2.1.1  ")
    testHtml.append("            <div>level 2.1.1.1  ")  #test 3 starts here; great-grandparent has date
    testHtml.append("            <a href='http://wwww.dogmablog.com'> </a>")   
    testHtml.append("            <a href='http://wwww.karmablog.com'> </a>")
    testHtml.append("            </div>")
    testHtml.append("        </div>")
    testHtml.append("   </div>")
    testHtml.append("</div>")
    #
    testHtml.append("<div> level 3.0 ")
    testHtml.append("   <div> level 3.1 ")
    testHtml.append("        <div> leve.1.1  ")
    testHtml.append("            <div>level 3.1.1.1  ")  #test 4 starts here;  some distant relative has date
    testHtml.append("            </div>")
    testHtml.append("        </div>")
    testHtml.append("   </div>")
    testHtml.append("   <div> level 3.2 ")
    testHtml.append("        <div> level 3.2.1  ")
    testHtml.append("            <div>level 3.2.1.1  June 1, 2010") 
    testHtml.append("            </div>")
    testHtml.append("        </div>")
    testHtml.append("   </div>")
    testHtml.append("</div>") 
    testHtml.append("</html>")
    testHtml.append("</body>") 
    html = "".join(testHtml)
    return html

def test_module1(html = None):

    #runs tests on the faux html generated with buildTestHtml (above).    
    html = buildTestHtml()
    searchDepth = 5
    soup = BeautifulSoup(html)
    findObj = FindDateInSoup(searchDepth)  

    pobj = soup.findAll(text = re.compile("level 1.0.2.2"))[0]  #test1 = sibling has date should return date from sibing object
    dateReturned = findObj.findDate_main(pobj)
    assert dateReturned == datetime(2010,1,1)            #"January 1, 2010"  

    pobj = soup.findAll(text = re.compile("level 1.0.1"))[0]    #test2: sib has no date, but sib's kids do
    dateReturned = findObj.findDate_main(pobj)
    assert dateReturned == datetime(2010,1,1)            #"January 1, 2010" 

    pobj = soup.findAll(text = re.compile("level 2.1.1.1"))[0]  #test3: great-grandparent has the date
    dateReturned = findObj.findDate_main(pobj)
    assert dateReturned == datetime(2010,5,1)              #"May 1, 2010" 

    pobj = soup.findAll(text = re.compile("level 3.1.1.1") )[0]  #test4: a distant relative has the date
    dateReturned = findObj.findDate_main(pobj)
    assert dateReturned == datetime(2010,6,1)              #"June 1, 2010"

def test_module2():   
    #search for dates in fragments found in the wild
    searchDepth = 5
    findObj = FindDateInSoup(searchDepth) 
    txt = u' \n <h2 class="date-header">Saturday, January 02, 2010</h2> \n  Begin .post  \n <div class="post">\n<h3 class="post-title">\n         Going for two and the win\n    </h3>\n<div class="post-body">\n<p>\n</p><div style'
    dateReturned = findObj.invoke_date_parser(txt)
    assert dateReturned[0] == datetime(2010,1,2)

    
    
if __name__=='__main__':

    test_module2()
    test_module1()
