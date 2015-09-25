#This file contains various utility functions used by bot.py, mostly to keep
#  the crawling logic separate form processing

# Standard libraries
from time import gmtime, strftime
from urlparse import urlsplit
import datetime
import re
import string
import sys
import urllib2 

# Somewhere else
import scrubHTML
import stripAndConvertHTMLTags 

# TurboGears
from sqlobject.sqlbuilder import *

# Local
#from buzzbot import *
from buzzbot import model
from model import *

class Utilities():
    #here's a short list of words we won't bother looking up in the semantic dictionary as they are value-neutral
    throwAways = ['and', 'for', 'but', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'too']
    #words to screen from user searches
    sqlReserved = ['and', 'or', 'not']  
    #longest allowed URL; this is the same as the database spec
    maxChar= 2000 
    #the number of sentences on either side of the target word that we'll capture
    BRACKETING_SENTENCES = 1
    #set up a hash table to handle text substitution in order to get rid of strange tags and symbols
    hashTable = scrubHTML.makeHashTable()  

    def uniq(self, seq):
        set = {}
        map(set.__setitem__, seq, [])
        return set.keys()     
    
    def dedupcontent(self, searchid):
    #dedupes the content table based on the first 50 characters being the same   
        mycont = model.Content.selectBy(searchid=searchid).orderBy('cont')
        lastcont=""
        for c in mycont:
            if c.cont[:50] == lastcont[:50]:
                model.Content.delete(c.id)
            else: lastcont = c.cont
                 
            
    def deDupUrls(self, searchid = None, urlList = None):
        #De-dups the url table for a single searchid or from a list; it's straightforward with one twist:
        #  sometimes there are multiple flavors of a single url  .htm/.html/.shtml for instance
        todelete = []; goodurls = []; myurls =[]; myids  =[]
        
        #if we have a searchid, we're de-duping the database; otherwise we're working on a list
        #...in the case of the database, we'll conduct a query
        if searchid:
            searchOrder=[model.URLS.q.netloc, model.URLS.q.path, model.URLS.q.query]
            dbReturn = model.URLS.selectBy(search_id=searchid).orderBy(searchOrder) 
            #make lists of the urls and ids 
            for d in dbReturn:
                myurls.append(d.urltext)
                myids.append(d.id)
            
        else:  #...if we have an array we'll want a faux id list and will sort the urls
            #... oset up a placeholder list for the ids by duplicating the url array
            myurls.sort()
            myids=myurls
            
        #set initial 'last url' parameters    
        lastnetloc=""; lastpath=""; lastquery=''; lastid = -666
        
        #roll through, setting the delete flag when needed
        for u, id in zip (myurls, myids):
            scheme, netloc, path, query, fragment = urlsplit(u)
            #does this record match the last one?
            if netloc==lastnetloc and query==lastquery:
                #some duplicates will have slightly different extensions e.g. '.htm' and 'html'
                thisPathToCompare = path
                lastPathToCompare = lastpath
                if len(lastPathToCompare) > len(thisPathToCompare):
                    lastPathToComare = lastPathToCompare[0:len(thisPathToCompare)]
                else:    
                    thisPathToCompare = thisPathToCompare[0:len(lastPathToCompare)]
                if thisPathToCompare == lastPathToCompare:    
                    #We have a dup.  Flag the oldest one (smallest id) for deletion
                    if id < lastid:
                        todelete.append(id)
                    else: 
                        todelete.append(lastid)

                #the else clause is triggered if this record is different; here we 
                #  update the 'last' information  
                else:   
                    goodurls.append(u)
                    lastnetloc = netloc
                    lastpath = path
                    lastquery = query
                    lastid = id          
        #when we're done, delete the dups from the database and return nothing; 
        #otherwise, return a list of good urls
        if searchid:
            for d in todelete:
                model.URLS.delete(d)
            return
        else:
            return goodurls
        
    def goodUrl(self,url):
        #vets urls we'll select for our list
        #if url.find('blog')<=0: return dict(status = 'bad', reason='general')
        url = url.lower()
        if url.find('2004')>=0: return dict(status = 'bad', reason='old-2004')
        if url.find('2005')>=0: return dict(status = 'bad', reason='old-2005')
        if url.find('2006')>=0: return dict(status = 'bad', reason='old-2006')
        if url.find('2007')>=0: return dict(status = 'bad', reason='old-2007')
        if url.lower().find('roblogger')>=0: return dict(status = 'bad-problogger', reason='spam')  #problogger
        if url.find('ihelpyoublog')>=0: return dict(status = 'bad', reason='spam-problogger')  #problogger
        if url.find('archive')>=0: return dict(status = 'bad', reason='spam-problogger')  #problogger
        if url.find('blogtoolscollection')>=0: return dict(status = 'bad-problogger', reason='spam')  #problogger
        if url.find('wiki')>=0: return dict(status = 'bad', reason='general-wiki')  
        if url.find('amazon')>=0: return dict(status = 'bad', reason='general-amazon')  
        if url.find('tinyurl')>=0: return dict(status = 'bad', reason='general-tinyurl')  
        if url.find('photo')>=0: return dict(status = 'bad', reason='general-photo') 
        if url.find('music')>=0: return dict(status = 'bad', reason='generalmusic')
        if url.find('yootube')>=0: return dict(status = 'bad', reason='general-yootube')
        if url.find('napster')>=0: return dict(status = 'bad', reason='general-napster')
        if url.find('podshow')>=0: return dict(status = 'bad', reason='general-podshow')
        if url.find('games')>=0: return dict(status = 'bad', reason='general-games')
        if url.find('mevio')>=0: return dict(status = 'bad', reason='general-mevio')
        if url.find('vidio')>=0: return dict(status = 'bad', reason='general-video')
        if url.find('pod')>=0: return dict(status = 'bad', reason='general-pod')
        if url.find('chitika')>=0: return dict(status = 'bad', reason='advertising-chitika')
        if url.find('jpg')>=0: return dict(status = 'bad', reason='image-jpg')
        if url.find('png')>=0: return dict(status = 'bad', reason='image-png')
        if url.find('gif')>=0: return dict(status = 'bad', reason='image-gif')
        if url.find('bmp')>=0: return dict(status = 'bad', reason='image-bmp')
        if url.find('mpg')>=0: return dict(status = 'bad', reason='movie-mpg')
        if url.find('xml')>=0: return dict(status = 'bad', reason='format-xml')
        if url.find('doubleclick')>=0: return dict(status = 'bad', reason='advertising-doubleclick')
        if url.find('quantcast')>=0: return dict(status = 'bad', reason='advertising-quantcast')
        if url.find('omniture')>=0: return dict(status = 'bad', reason='advertising-omniture')
        if url.find('creativecommons')>=0: return dict(status = 'bad', reason='general-creativecommons')
        if url.find('google')>=0: return dict(status = 'bad', reason='google')

        return dict(status = 'good', reason='passed')     
    
    
    def isDup(self, newThing, oldList):
        #deduplicates a list
        dup=False; ix=0; done = False
        lowerNewThing = newThing.lower()
        while not dup and not done:
            if oldList[ix].lower() == lowerNewThing:
                dup = True
            ix = ix+1
            if ix >= len(oldList): done = True
        return dup 
    
    def analyzeContentBlock(self, content):
    
        #conduct an analysis on a single block of relevant content.  This will obviously get more sophisticated, but for now
        #  we'll look for positive and negative associations of each surrounding word using Harvard's semantic dictionary
    
        #Instantiate a translator object and tell it what to keep (we'll get rid of punctuation)
        tran= Translator(keep = string.ascii_lowercase)
    
        #look thru the words
        mywords = content.split()
        mywords.sort()
        poswords = 0; negwords=0; obscenewords = 0; lastword = "";lastrating=""
        for w in mywords: 
            if w <> lastword:
                #disregard really short words and those w/ & (likely html constants)
                if len(w) > 3 and w.find('&')<0:
                    w = w.lower()
                    w = tran(w)
                    polarity = ""
                    #find out what the dictionary has to say about the word
                    neghits = model.NegWords.selectBy(word  = w).count()
                    if neghits > 0: negwords = negwords+1; lastrating='neg'
                    poshits = model.PosWords.selectBy(word  = w).count()
                    if poshits > 0: poswords = poswords+1; lastrating = 'pos'
                    obscenehits = model.ObsceneWords.selectBy(word  = w).count()
                    if obscenehits > 0: obscenewords = obscenewords+1; lastrating = 'obs'
                    if neghits+obscenehits >0: polarity = 'negative'
                    if poshits>0: polarity = 'positive'
            else: #we have a duplicate word and don't need to look again
                if lastrating == 'neg': negwords = negwords+1
                if lastrating == 'pos': poswords = poswords+1
                if lastrating == 'obs': obscenewords = obscenewords+1
                
                 
        polarityscore = poswords - negwords - obscenewords  
        return polarityscore    
    
    def fixUrls(self, targetword, searchID=None, urlList = None, deDupDB = None): 
     #cleans up urls harvested from a search engine, stored in database or list
         #  -move site names found in the archive ('cache') into the url column and clear the query column;
         #     this will allow us to rejoin the url elements appropriately for the host site
         #  -get rid of stuff we don't want (google images, etc.)
         #  -get rid of client web site references (more specifically, www.<targetword>...)
         #  -checks the urls to make sure it isn't blacklisted for this search id
         #  -tests to ensure we don't already have the url stored for this search
         #  -de-duplicates the remaining urls (including ...html/...htm, etc.)
        
         
        myurls = []; myids = []; goodurls = []
        #if a searchID is provided, we'll vet urls in the database; otherwise we'll work a list    
        
        # if the searchid is not provided, we're working on an array; make a faux list of ids to go with it
        #  (this is needed as a placeholder in the loop logic)
        if not searchID: 
            myurls = urlList
            myids = myurls
       
        else:     #if the searchid *is* provided, we're going to work on the database    
            urls = model.URLS.selectBy(search_id=searchID)   
            blacklist = model.URLS.selectBy(search_id = searchID, is_blacklisted = True)
            #create a list of the urls
            for u in urls:
                myurls.append(u.urltext)
                myids.append(u.id)
                
        for u, i in zip(myurls, myids):  
            #if this is a quoted string, dump the quotes
            if u[0] =='"': u = url[1:-1]
            #find the url's constituent elements
            scheme, netloc, path, query, fragment = urlsplit(u)            
            #some urls are cached.  If so, parse out the original to find the real 
            #  (originating web site) address.  
            cleanquery = str(query)[1:-1]   #removes bracketing u""     
            splitQuery = cleanquery.split(':')          
            if splitQuery[0] == 'q=cache':  #this is a cached result
                plusPos = splitQuery[2].find('+')
                u = splitQuery[2][:plusPos-1]
                #parse the site names into constituent elements
                scheme, netloc, path, query, fragment = urlsplit('http://' + u)
                #enclose each returned string in ' ' 
                netloc = "'" + netloc + "'"
                path = "'" + self.fixSQLquotes(path) + "'"
                query = "'" + self.fixSQLquotes(query) + "'"
                fragment = "'" + self.fixSQLquotes(fragment) + "'" 
                #if we're working on the database, update the record w/ the 'uncached' version
                if not searchID:
                    #leave the scheme alone (that's the 'http' part) but replace the other url components
                    dbRowObject = model.URLS.get(urlID)
                    dbRowObject.set(netloc=netloc, query=query, path=path, fragment = fragment)
    
            #Get rid records we don't really want.  For now, eliminate the client web site and google.
            #  Additionally, we'll get rid of any blacklisted site.  In the next upgrade, we'll have the
            #  ability to black-list sites by search, LP, and globally (porn sites, etc) and all will
            #  be moved out to the database.
            goodRecord = True
            
            #note, there is a much better way to screen urls in searcher.py
            if self.goodUrl(netloc+path).get('status') == 'bad': goodRecord = False
            if netloc.find("www." + targetword + ".com") > 0 : goodRecord = False 
            
            #if we're vetting urls pulled from the database, we'll also screen for blacklisted ones
            if not searchID:
                for b in blacklist:
                    if b.netloc == netloc: goodRecord=False                
                #we'll delete the bad records here  
                if not goodRecord:
                    rowToDelete = model.URLS.delete(u.id)                  
                    print "dumping " + u.netloc
                    
            else:  #we're vetting an array, so we'll keep of the good-so-far urls
                if goodRecord:
                    goodurls.append(u)
                    
        #when we're done with the loop, de-dup if requested (if working on a database this can be slow, so
        #  the de-dup step is optional)
        if not searchID:   #always de-dup an array  
                return self.deDupUrls(None, goodurls)  #returns a de-duped list
        else: 
            if deDupDB: 
                self.dedupUrls(searchID, None)
                    
    def urlunsplit(self, scheme, netloc, url, query, fragment):
        #modified from the original to avoid strange http:/// addresses
        if netloc or (scheme and url[:2] != '//'):
            if url and url[:1] != '/': url = '/' + url
            url = '/' + (netloc or '') + url
        if scheme:
            url = scheme + ':' + url
        if query:
            url = url + '?' + query
        if fragment:
            url = url + '#' + fragment
        return url      
    
    def addNoDupes(self, myList):
        #this adds words/phrases from myAdd to a deduped list; casts numbers to strings in case they
        # crop up
        templist=[]
        #myList will contain comma-delimited words or phrases; parse these out and
        #  add each element to a temporary list
        for i in myList:
            parsedcontent = i.split(',')
            for p in parsedcontent:
                templist.append(str(p))
        #return a de-duped version of the temporary list        
        return(self.uniq(templist))    
    
    #***************text cleaning routines***********************
    
    def fixSQLquotes(self, rawString):
        #fixes strings intended for mySQL database, eliminating quotes, etc.  (\ is escape character)
        fix1 = rawString.replace("\'", "")
        fix2 = fix1.replace('\"', '')
        return fix2 
    

    
    def cleanSQLkeywords(self, mylist):
        #cleans sql keywords out of user-provided list of search terms
        retlist=[]
        for word in mylist:
            word = word.strip()
            #strip any quotes
            word = re.sub('"', '\"', word)
            word = re.sub("'", "\'", word)        
            if word not in self.sqlReserved and len(word) > 0:
                retlist.append(word)
        return(retlist)
 
    def stripHTMLtags(self, in_text):
        # Routine by Micah D. Cochran
        # convert in_text to a mutable object (e.g. list)
        s_list = list(in_text)
        i,j = 0,0
        
        #PAT# the index (i) can go out of bounds if the tag brackets are mis-matched; the list is 
        #  shortened within the while block, therefore not checked.  Sleazy fix with try block
        while i < len(s_list)-1:
                # iterate until a left-angle bracket is found
            try:
                if s_list[i] == '<':
                    while s_list[i] != '>':
                        # pop everything from the the left-angle bracket until the right-angle bracket
                        s_list.pop(i)  
                    # pops the right-angle bracket, too
                    s_list.pop(i)
                else:
                    i=i+1	
            except:
                pass
        # convert the list back into text
        join_char=''
        return join_char.join(s_list) 
    
    def stripHTMLunicodeEtc(self, myText):
        #substitutes ascii characters for HTML/unicode codes
        workingText = myText
        for i in  range(len(self.hashTable)):
            old, new = self.hashTable[i]
            try:
                workingText = workingText.replace(old, new)
            except:
                pass
        #for some reason we're missing some; use a meat ax to remove the rest    
        out=[]
        skipNext = False
        for i in range(len(workingText)):
            mychar = workingText[i]
            charOK = True    
            try: myord = ord(mychar)
            except TypeError:  #probably a unicode string
                charOK = False
            if myord > 122:  #on beyond zebra
                charOK = False
            if myord < 40:   #keyboard characters (upper case number keys) 
                charOK = False
            if myord ==92:    #this is \ used to escape new lines, tabs, etc.
                charOK = False
            if myord ==32:    #whitespace
                charOK =True
            if charOK and not skipNext:
                out.append (mychar)
        myReturn = "".join(out)        
        return myReturn    
    
    #*******************end of text cleaning routines
    
    def makeSQLsearchString(self, urlFind, urlEliminate, targetword):
        #Create a correct SQL search string that ANDs together all the url-level search criteria.
        #  this is used elsewhere to build SQLObject strings like:
        #   model.Content.Select(cont like %'Microsoft'% and cont like %'Gates'%)
        
        #start with the targetword
        sstr = ''
        if len(targetword)> 0: sstr = sstr + "cont like '%" + targetword + "%'"+ " and "
        
        #if we don't have any url or content criteria, strip off the trailing ' and '
        if len(urlFind)==0 and len(urlEliminate)== 0:  sstr = sstr[:-5]
        for u in urlFind:
            sstr = sstr + "cont like '%" + u.strip() + "%'" + " and "
            
        #if we don't have any elimination criteria, strip off the trailing ' and '
        if len(urlEliminate)== 0 and sstr[len(sstr)-5:] == " or ": sstr = sstr[:-4]
        for u in urlEliminate:
            sstr = sstr + " not cont like '%" + u.strip() + "%'" + " and "
            
        #strip off any final trailing ' and '
        if sstr[len(sstr)-5:] == " and ": sstr = sstr[:-5]
        return sstr
    
    def getTextSearchDelimiters(self):
        #provides beginning and end delimiters for valid text within a web site
        textDelimiters = []
        paragraphDelimiters = '<p', '</p>'
        blockQuoteDelimiters = '<blockquote>', '</blockquote>'
        textDelimiters.append(paragraphDelimiters)
        textDelimiters.append(blockQuoteDelimiters)
        return textDelimiters[:]
    
    def getPunctuationDelimiters(self):
        textDelimiters = []
        textDelimiters.append('.')
        textDelimiters.append('?')
        textDelimiters.append('/n')
        return textDelimiters[:] 
    
    def digUrlsOutOfPage(self,retObj):
        #finds all the urls in a web page
        urlsFound = []
        returnStatus = retObj.get('status')
        if returnStatus < 400:
            content = retObj.get('data') #grab the results    
            rawUrlsFound = re.findall('href="http://.*?"', content) #snag the links
            if len(rawUrlsFound) ==0: 
                rawUrlsFound = re.findall("http://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", content)
    
            for rawUrl in rawUrlsFound:  #clean the raw urls up
                betterUrl = rawUrl.replace('href=','')
                evenBetterUrl = betterUrl.replace('"','')
                #trap obviously bad urls (move this off to it's own routine eventually)
                cssFound =evenBetterUrl.find(".css") #this is a cascading style sheet
                if not cssFound>0: 
                    urlsFound.append(betterUrl) 
        return urlsFound
    
    def digUrlsOutOfText(self,content):
        #finds all the urls in a web page
        urlsFound = []
        rawUrlsFound = re.findall('href="http://.*?"', content) #snag the links
        if len(rawUrlsFound) ==0: 
            rawUrlsFound = re.findall("http://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", content)

        for rawUrl in rawUrlsFound:  #clean the raw urls up
            betterUrl = rawUrl.replace('href=','')
            evenBetterUrl = betterUrl.replace('"','')
            #trap obviously bad urls (move this off to it's own routine eventually)
            cssFound =evenBetterUrl.find(".css") #this is a cascading style sheet
            if not cssFound>0: 
                urlsFound.append(betterUrl) 
        return urlsFound
