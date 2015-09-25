# -*- coding: utf-8 -*-

# Standard libraries
from time import gmtime, strftime
from urlparse import urlsplit
import datetime
import re
import socket
import string
import sys
import urllib2

# TurboGears
from sqlobject.sqlbuilder import *

# Somewhere else
import scrubHTML
import stripAndConvertHTMLTags

# Local
from buzzbot import *
from buzzbot.model import *

from buzzbot import model
from buzzbot import botUtilities
botUtilities = botUtilities.Utilities()



class Translator:
    #this from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303342  
    #very handy string parser  called thus:  clean = Translator(keep = string.ascii_lowercase)
    allchars = string.maketrans('','')
    def __init__(self, frm='', to='', delete='', keep=None):
        if len(to) == 1:
            to = to * len(frm)
        self.trans = string.maketrans(frm, to)
        if keep is None:
            self.delete = delete
        else:
            self.delete = self.allchars.translate(self.allchars, keep.translate(self.allchars, delete))
    def __call__(self, s):
        return s.translate(self.trans, self.delete)  
    


class BotRoutines():
    
    def runLP(self,**kwargs):
        #This is the workhorse routine for gathering content from the web.  It takes
        #  an lpID , runs the queries, evaluates, and stores results.
    
        #**************************grab the LP specs*****************************
        thisUser = int(kwargs.get('userid'))
        thisStatus='owner'
        thisLPid = kwargs.get('extra_lpid')  
     
        
        #here we decide whether to blow out the existing urls and content; we'll put
        #  this in the interface
        deleteLPurls = False
        deleteLPcontent = False
        
        #an LP can have one or more searches; we'll find them now
        mySearches = model.LPSearch.selectBy(lp_id = thisLPid)
        #get the specs for this LP
        thisLP = Listeningpost.get(int(thisLPid))
        
        #if the user hasn't selected any searches quit
        if mySearches.count() == 0: 
            return
        #go through the searches, picking out the criteria
        targetwordraw = []; searchstringraw=[]; eliminationwordsraw = []; urlsearchforraw = []
        urleliminateraw = []; maxurlsraw = []; maxcontentraw = []; targetwordraw =[]
        for s in mySearches:
            #grab the search object
            thisSearch = model.Search.get(int(s.search_id))
            #add the criteria to the appropriate list
            targetwordraw.append(thisSearch.targetword)
            searchstringraw.append(thisSearch.searchstring)
            eliminationwordsraw.append(thisSearch.eliminationwords)
            urlsearchforraw.append(thisSearch.urlsearchfor)
            urleliminateraw.append(thisSearch.urleliminate)
            targetwordraw.append(thisSearch.targetword)
            maxurlsraw.append(thisSearch.maxurls)
            maxcontentraw.append(thisSearch.maxcontent)
            
        #create a de-duped master list of the search criteria    
        targetword = botUtilities.addNoDupes(targetwordraw)
        searchstring=botUtilities.addNoDupes(searchstringraw)
        eliminationwords = botUtilities.addNoDupes(eliminationwordsraw)
        urlsearchfor = botUtilities.addNoDupes(urlsearchforraw)
        urleliminate = botUtilities.addNoDupes(urleliminateraw)  
        targetword = botUtilities.addNoDupes(targetwordraw)
        #the searches might have a max number of urls or content blocks; for the LP we'll
        #  use the least restrictive (max)
        maxContent = max(maxcontentraw)
        maxurls = max(maxurlsraw)
        maxUrls = int(thisSearch.maxurls)
        
        #see if the user wants to keep the previous URLs 
        #
        freezeurllist = thisLP.freezeurllist
       
        #debug
        freezeurllist = False    
        
        if thisLP.keepcontent:
            deleteURLS = False
        else: delteURLS = True    
    
        #determine whether or not to get new urls for this search 
        doharvestSiteNames = True
        if freezeurllist:
            doharvestSiteNames = False    
       
    #**************************perform operations based on the specs************************** 
    # note: I'm hoping to set up some AJAX code to flash in results to make it more visually 
    #  interesting.  So, instead of serially processing the steps, we'll do them in several passes
            
        #delete URLs if asked
        if deleteURLS:
            model.URLS.deleteBy(lpid = int(thisLPid))
    
        myDelimiters=getTextSearchDelimiters()
    
        #pick up some new URLs if we need them
        if doharvestSiteNames:   
            #Get initial URLs over which to search.  Method developSearchString can take an
            #  additional argument to designate a search engine other than Google.  Logic is 
            #  currently set up only for Google, though.
            engine = 'Google'
            #developSearchString returns a single search string to encapsulate search criteria; \
            rawSearchStr = self.developSearchString (urlsearchfor, urleliminate, engine, maxUrls)
            #...while getInitSearchArray returns an array of requests to capture multiple pages of hits   
            iUrl = self.getInitSearchArr(rawSearchStr, engine, maxUrls) 
            #we'll iterate over each page of returned hits
            for url in iUrl:
                urlsFound = self.harvestSiteNames(url,rawSearchStr)
                #clean these up (pass in raw urls and target word array, get back array of urls)
                goodUrls = botUtilities.fixUrls(targetword, None, urlsFound )
                
                #go thur the good urls, one at a time  callOpenAnything(url)
                for u in goodUrls:
                    #snag content from this url
                    #mydict = self.grabContentFromSingleUrl(targetword, self.BRACKETING_SENTENCES, self.maxChar, myurl, myDelimiters)
                    mydict = self.getContentWithFeedparser(url, targetword)    #self, url, targetword=None                    
                    
                    thiscontent = mydict.get('cont')  #a list of content containing target word
                    etag = mydict.get('etag')  #the etag (date stamp) from the site
                    #clean it up a bit by applying content-level filter(s)
                    cleancont = self.applyContentLevelFilter(thiscontent, eliminationwords, selectstring)
                    #calculate a list of scores for this block
                    contscores, poswords, negwords = self.analyzeSingleContentBlock(cleancont)
                    urlscore = sum(contscores)
                    #
                    #At this point, we have everything we need to know concerning our url, content, and analysis               
                    #so...update the databases, watching for duplicates and figure out how to flash it out.
                    self.updateSingleContentBlock(myurl, cleancont, lpid, etag, thisUser, contscores)           
    
    def applyContentLevelFilter(self, content, toEliminate, toFind):
        #This analyzes the content to assay 'fit' to user specs
        returnList=[]
        #contentEliminate and contentFind are comma-delimited strings.  First, we'll
        #  parse them and coherse to lists (else single words won't work)
        contentEliminate = toEliminate.split(',')
        if type(contentEliminate) == 'str': elimList = [contentEliminate]
        contentFind = toFind.split(',')
        if type(contentFind) == 'str': contentFind = [contentFind]
        #trim the leading/trailing white spaces
        for c in contentEliminate:
            c.strip()
        for c in contentFind:
            c.strip()        
                
        #Decide acceptance criteria: we'll accept if toFind is null (user doesn't care) or
        #  toFind is not null and we've found a key word. Any instance of toEliminate rejects
        if len(toFind) > 0: needGood = True 
        else: needGood=False
    
        #process the content        
        for c in content:
            thisCont = c.lower()
            anyBad = False 
            #see if we have any 'elimination' words
            
            for word in contentEliminate:
                if string.find(thisCont, word.lower())>=0 and len(word)>0:
                    anyBad = True
                    
            #now check if we have at least one sought-after word
            anyGood=True  #we'll assume we've got a good word unless we need to assume otherwise
            if not anyBad and needGood:
                anyGood = False
                for word in contentFind:
                    if string.find(thisCont, word.lower())>=0:
                        anyGood = True
            #if we like content,add it to the return list
            if not anyBad and anyGood:
                returnList.append(c)
                
        #return all the content we like        
        return returnList
    
    def updateSingleContentBlock(self, myurl, cont, lpid, etag, userid, contscores):
        #this checks the database for duplicated url or content
        
        #query db for matching urls
        oldurlrows = model.URLS.selectBy(netloc = netloc, url=url, lpid = lpid)
        now = datetime.now()
    
        #add the current url provisionally (otherwise key constraint fails)
        scheme, netloc, url, query, fragment = botUtilities.urlunsplit(myurl)
        newurl = model.URLS(scheme = scheme, netloc=netloc, path=path, etag= etag,
                                   query = query, fragment=fragment, urltext=myurl,
                                   lpid = int(lpid), datefound=now, userid = int(userid))     
        needToAddUrl = True
        #if we already have the url, we'll next check the etag to see if it's new
        for h in oldurlrows:
            oldurlid = int(h.id)
            if hits.etag <> etag:
                #we *may* have seen this guy before (some sites omit etags)
                oldscheme, oldnetloc, oldpath, oldquery, oldfragment = urlsplit(h.urltext)
                scheme, netloc, path, query, fragment = urlsplit(myurl)
                if netloc==oldnetloc and netloc==oldnetloc:
                    thisPathToCompare = path
                    lastPathToCompare = old
                    if len(lastPathToCompare) > len(thisPathToCompare):
                        lastPathToComare = lastPathToCompare[0:len(thisPathToCompare)]
                    else:    
                        thisPathToCompare = thisPathToCompare[0:len(lastPathToCompare)]
                    #by comparing the short versions we can tell if we have a dup    
                    if thisPathToCompare <> lastPathToCompare: 
                        #we have a duplicate url so add any new content to the old one   
                        oldcontrows = model.Content.selectBy(lpid=lpid, urlid = oldurlid)
                        #this syntax is a bit strange, but useful; the two lists are iterated together
                        for n, s in zip (newcont, contscores):
                            dupcont = False
                            if s == None: 
                                s=0
                            for o in oldcontrows:
                                oldcont = oldcontrows.cont
                                if n ==oldcont:
                                    dupcont = True
                                    needToAddUrl=False #we know the url is a dup
                            #OK.  The url is a dup *and* this content is new, so add the content
                            # to the content table, tagging it with the old url's info
                            dltaPolarity=0
                            if not dupcont:          
                                #add the content to the content table ...
                                model.Content(urlid=oldurlid, cont= n, urltext = myurl,
                                              dateaccessed=now, lpid = int(lpid), polarity = s)
                                #keep track to any changes in the url's polarity
                                dltaPolarity += s
                                #...and remember it
                                oldUrlAugmented = h
        #if we've couldn't add the content to an existing url add it to the new one
        if needToAddUrl:
            urlPolarity = 0
            for n, s in zip (newcont, contscores):
                if s == None: 
                    s=0
                model.Content(urlid=newurl.id, cont= n, urltext = newurl.urltext,
                                dateaccessed=now, lpid = int(lpid), polarity = s)
                urlPolarity +=s
            newurl.set(polarity = urlPolarity)    
        #...otherwise dump our provisional url from its table        
        else: 
            model.URLS.delete(newurl)
            #update the url polarity score of the url we've added to
            oldUrlAugmented.set(polarity = oldUrlAugmented.polarity+dltaPolarity)
    
    def analyzeSingleContentBlock(self, mycont):
        tran= Translator(keep = string.ascii_lowercase)
        contentIx = 0
        wordIx = 0
        mywords = mycont.split()
        for c in mywords: 
            #look thru the words
            poswords = poshits = 0
            negwords = neghits = 0
            obscenewords = obscenehits = 0
            for w in mywords: 
                #disregard really short words and those w/ & (likely html constants)
                if len(w) > 3 and w.find('&')<0:
                    w = w.lower()
                    w = tran(w)
                    polarity = ""
                    #find out what the dictionary has to say about the word
                    neghits = model.NegWords.selectBy(word  = w).count()
                    if neghits > 0: negwords = negwords+1
                    poshits = model.PosWords.selectBy(word  = w).count()
                    if poshits > 0: poswords = poswords+1
                    obscenehits = model.ObsceneWords.selectBy(word  = w).count()
                    if obscenehits > 0: obscenewords = obscenewords+1
                    if neghits+obscenehits >0: polarity = 'negative'
                    if poshits>0: polarity = 'positive'
     
            polarityscore = poshits - neghits - 2*obscenehits            
            return (polarityscore, poswords, negwords)
    
    
    def testRunSearchOnDatabase(self):
        mykwargs = dict(extra_lpid=1, userid = 1)
        self.runSearchOnDatabase(1, mykwargs)
    

    
    
    def updateLPfromKwargs(self, thisLP, **kwargs):
        #saves an LP object to existing if available, or to a new one
        try:
            print thisLP
            lp = model.Listeningpost.get(thisLP)
        except:
            newlp = model.Listeningpost() #creates a new lp returning a select() object
            lp = model.Listeningpost.get(newlp.id) # this is the row object which we can set
        
        #clear the lp-search table 
        LPSearch.deleteBy(lp_id = thisLP)
        
        #Parse out the incoming kwargs; the return from the form includes a tuple of (key, value) 
        #  tuples for all the checked boxes.  These come in the form of {ck_1: u'on} to indicate
        #  which searches the user chose
        items = kwargs.items()
        for i in items:
            boxname, state = i         
            #parse the tuple (state will always be 'on' as only checked values returned)
            if boxname[:3] == 'ck_':
                searchNum = int(boxname[3:])
                LPSearch(lp_id = lp.id, search_id = searchNum)     
            
        #set placeholders for the check boxes (only checked ones come thru as kwargs)
        is_client_worthy = is_public = update_nightly = False
        
        #Parse out the kwargs that are lp database fields
        name = kwargs.get('name')          
        if 'description' in kwargs: description = kwargs.get('description')
        if 'is_client_worthy' in kwargs: is_client_worthy =  True
        if 'is_public' in kwargs: is_public = True
        if 'update_nightly' in kwargs: update_nightly= True  
        if 'targetword' in kwargs: targetword=kwargs.get('targetword')
    
        #Save/update the lp
        lp.set(name =name, description = description, is_client_worthy = is_client_worthy,
           is_public = is_public, update_nightly = update_nightly, targetword = targetword)
        
        #return the lp object
        return lp
    
    def createSearchFromLPspec(self, thisLP, deleteExisting, **kwargs):
        #this does a mash up of the searches associated with this lp to create 
        #  and associates the newly-created master search with this lp
    
        #update the LP
        lp = self.updateLPfromKwargs(thisLP, **kwargs)
    
        thisUser = int(kwargs.get('userid'))
        targetword = lp.targetword
        lowertargetword = targetword.lower()
         
        existingSearchToRun = lp.searchtorun
        
        #find all the search criteria for all the searches
        mysearches = model.LPSearch.selectBy(lp_id=thisLP)
        urlFind=[]; urlEliminate=[]; contentFind=[]; contentEliminate=[]
        #split out the words/phrases to test for sql keywords that will blow up the db
        for snum in mysearches:
            sid = snum.search_id
            try:  #make sure we have this search available
                s = model.Search.get(sid)
                urlFind=urlFind + botUtilities.cleanSQLkeywords (s.urlsearchfor.split(','))
                urlEliminate=urlEliminate + botUtilities.cleanSQLkeywords (s.urleliminate.split(','))
                contentFind=contentFind + botUtilities.cleanSQLkeywords (s.searchstring.split(','))
                contentEliminate=contentEliminate + botUtilities.cleanSQLkeywords (s.eliminationwords.split(','))
            except: 
                pass
        #add everything back together to make master strings
        join_char=','
        urlsearch = join_char.join(urlFind)
        urlelim = join_char.join(urlEliminate)
        contsearch = join_char.join(contentFind)
        contelim = join_char.join(contentEliminate)

        #if the user didn't provide any target word, we'll supply one if possible
        if len(lowertargetword)==0:
            #lower case of first word of url string
            if len(urlFind)>0:
                lowertargetword=urlFind[0].lower() 
        if len(lowertargetword)==0:
            #lower case of first word of content string
            if len(contentFind)>0:
                lowertargetword=contentFind[0].lower()
        
        #delete the existing search if asked
        if deleteExisting and lp > 0:
            model.Content.deleteBy(id = existingSearchToRun)
            model.Contsearch.deleteBy(search =existingSearchToRun)
            if existingSearchToRun>0: 
                model.Search.deleteBy(id = existingSearchToRun)
            searchObj = model.Search(userid = thisUser)
        else: 
            try:  #check if there's already a search dedicated to this LP
                searchObj = model.Search.get(existingSearchToRun)
            except: #if there's not, we'll create one
                searchObj = model.Search(userid = thisUser)
        
        #add the 'search', flagging it as an lp
        searchObj.set(name = lp.name, description=lp.description,
                     targetword=targetword, islp = True,
                     urlsearchfor = urlsearch, urleliminate = urlelim,
                     searchstring = contsearch, eliminationwords = contelim)
    
        #update the lp with the search id
        lp.set(searchtorun = searchObj.id)
    
        #return the search id
        return searchObj.id
    
    
    def runLPOnDatabase(self, thisLP, maxUrls, deleteExisting, **kwargs):
        #this runs a search on the results contained in our database
        #the main difference between this and the runSearchOnDatabase method is that this one
        #  consolidates the search attributes across the different searches specified for this LP       
    
        #this creates a 'search' by amalgomating all the individual searches
        thisLPsearch = self.createSearchFromLPspec(thisLP, deleteExisting, **kwargs)
        self.runSearchOnDatabase(thisLPsearch, maxUrls, **kwargs)
    
    def runSearchOnDatabase(self, searchID, maxUrls, **kwargs):
        if 1==1: #this just allows collapse of data acquisition code (for coder's sanity)
            #this runs a single search on the results contained in our database      
         
            #**************************grab the search specs**************************
            s=model.Search.get(searchID)
    
            maxContent = int(s.maxcontent)
       
            #see if the user wants to keep the previous URLs 
            #
            deleteContent = s.freezeurllist
            if kwargs.get('extra_deleteExisting'):
                deleteContent = True
            else: deleteContent = False    
        
            #parse the search fields; provide null list if empty; strip sql key words ('and', etc) 
            urlFind=[]; urlEliminate=[]; contentFind=[]; contentEliminate=[]
            if len(s.urlsearchfor)>0: urlFind = botUtilities.cleanSQLkeywords (s.urlsearchfor.split(',')  )
            if len(s.urleliminate)>0: urlEliminate = botUtilities.cleanSQLkeywords (s.urleliminate.split(',') )        
            if len(s.searchstring)>0: contentFind = botUtilities.cleanSQLkeywords (s.searchstring.split(',') )
            if len(s.eliminationwords)>0: contentEliminate =  botUtilities.cleanSQLkeywords (s.eliminationwords.split(',')   )
            
            thisUser = kwargs.get('userid')
            thisLpid = kwargs.get('extra_lpid')
            
            #this is the mandatory word that will anchor the text window
            targetword = s.targetword
            lowertargetword = targetword.lower()
            #if the user didn't provide a target word, we'll supply one if possible
            if len(lowertargetword)==0:
                #lower case of first word of url string
                if len(urlFind)>0:
                    lowertargetword=urlFind[0].lower() 
            if len(lowertargetword)==0:
                #lower case of first word of content string
                if len(contentFind)>0:
                    lowertargetword=contentFind[0].lower()
                             
            
        #**************************perform operations based on the specs************************** 
    
        #delete content associated with this search id if asked
        if deleteContent and searchID>0:
            model.Content.deleteBy(searchid = searchID) 
            model.Contsearch.deleteBy(search = searchID)
       
        #find content in our database that matches the user's request; this will include our target
        # word and selection/elimination criteria
        #
        sstr = botUtilities.makeSQLsearchString(urlFind, urlEliminate, lowertargetword)
        #the search results will comprise our url-level screening.  We'll want to chunk this into content
        #  bits and analyze each of these
        if len(sstr)==0: return
        urlLevelCont = model.Content.select(sstr) 
        #now, grab content blocks based on the content-specific criteria 
        contentBlocks = self.snagContentFromDB(urlLevelCont, searchID, lowertargetword, maxUrls, contentEliminate, contentFind)
        #add to datebase
        for c in contentBlocks:  
            finishedString, originatingContID, thisDateAccessed, thisUrltext, thisUrlid= c
            try:
                if model.Content.selectBy(cont=finishedString).count()==0: #see if we already have it
                    model.Content(urlid=thisUrlid, cont= finishedString, urltext = thisUrltext,
                                  dateaccessed=thisDateAccessed, searchid = int(searchID), lpid = int(thisLpid))
                    print 'adding content ' + finishedString[:20] +'... from ' + thisUrltext
            except:	
                pass    
                            
            #update the database so we know we've already looked at this content block for this search    
            try:
                #see if we already have it
                if model.Contsearch.selectBy(cont = originatingContID, search = searchID).count()==0:
                    model.Contsearch(cont = originatingContID, search = searchID)
            except: 
                pass    
    
    def snagContentFromDB(self, urlLevelCont, searchID, lowertargetword, maxUrls, contentEliminate, contentFind):
        #this will grab content based on either the searchID or lpid and assumes the one with
        # a negative value is 'turned off'
        urlix = 0
        #get the text delimers (., etc)    
        myDelimiters=botUtilities.getPunctuationDelimiters() 
        urlct = urlLevelCont.count()
        contToAdd = []
        if maxUrls > urlct-1: maxUrls = urlct-1
        while urlix <= maxUrls:
            c=urlLevelCont[urlix]
            thisContID = c.id
            thisDateAccessed = c.dateaccessed
            thisUrltext = c.urltext
            thisUrlid = c.urlid
            if urlix<=maxUrls:
                foundAnyContent = False
                #make sure we haven't already parsed out this content block for this search criteria
                if searchID > 0:
                    parsedTest = model.Contsearch.selectBy(cont = c.id, search = searchID).count()==0
                else:
                    parsedTest = model.Contsearch.selectBy(cont = c.id, search = lpid).count()==0   
                if parsedTest:    
                    content = c.cont
                    #parse out the content block into sentences/clauses; first remember the punctuation
                    punctuation=[]
                    for cn in content:
                        if cn in myDelimiters:
                            punctuation.append(cn) 
                    #provide an extra elipisis element        
                    punctuation.append('...') 
                    #substitute a new line character for each delimiter
                    cleanedContent=content
                    for d in myDelimiters:
                        cleanedContent = cleanedContent.replace(d, '\n')
                    #escape out quotes so we don't confuse mySQL (insert a \); 
                    cleanedContent = re.sub('"', '\"', cleanedContent)
                    cleanedContent = re.sub("'", "\'", cleanedContent)
                    #parse out the sentences 
                    mySentences = cleanedContent.split('\n')
                    #we'll keep every sentence containing our magic word and <BRACKETING_SENTENCES> 
                    #  on either side of it
                    keptSentences = []
                    needElipsis = False
                    for i in range(len(mySentences)):
                        keptSentences.append(False)
                    #update the truth table based on the contents    
                    for sent in range(len(mySentences)):
                        lowerSent = mySentences[sent].lower()
                        if lowerSent.find(lowertargetword) >=0: 
                            keptSentences[sent]=True
                            #add the line before if it makes sense
                            if sent > self.BRACKETING_SENTENCES: keptSentences[sent-self.BRACKETING_SENTENCES] =True
                            #add the line after if it makes sense
                            if sent < len(mySentences)-self.BRACKETING_SENTENCES: keptSentences[sent+self.BRACKETING_SENTENCES] = True
        
                    #add back the punctuation
                    if len(mySentences)>0:
                        finishedString =''                            
                        for s in range(len(keptSentences)):
                            if keptSentences[s]:
                                if s<len(punctuation):
                                    finishedString = finishedString + mySentences[s] + punctuation[s] + "  " 
                                else: finishedString = finishedString + mySentences[s] +" "       
                            else: #add elipsis if this is a skipped sentence, not the first one,
                                  #and at least one more good sentence follows.
                                if s < len(keptSentences)-1 and s > 1:
                                    moreFollow = False
                                    for ss in range(s+1, len(keptSentences)):
                                        if keptSentences[ss]:
                                            needElipsis=True
                                            
                        #remove leading/trailing spaces
                        finishedString = finishedString.strip()                                            
                        #check for length to ensure fit to db
                        if len(finishedString) > self.maxChar:
                            finishedString = finishedString[:self.maxChar]  
                            
                        #apply our content-level screening criteria
                        isgood =  self.evaluateContentFitSingleBlock(contentEliminate, contentFind, finishedString)                        
                        #add the content fragment to our database if we like it                                  
                        if len(finishedString) > 20 and isgood:  #don't bother getting really short snippets
                            foundAnyContent = True
                            contentInfo = (finishedString, thisContID, thisDateAccessed, thisUrltext, thisUrlid)
                            contToAdd.append(contentInfo)
            urlix = urlix+1  #bottom of while loop; increment the index    
        return contToAdd
        
    def runSearch(self, thisSearch, **kwargs):
        #This is the workhorse routine for gathering content from the web.  It takes
        #  a search ID , runs the queries, evaluates, and stores results.
    
        #these are some switches for debugging; in production all are True
        debug = True
        debugGrabContent = True
        debugCleanContent = True
        debugAnalyzeContent = False
        debugScoreURL     = False
    
        doharvestSiteNames = True
        readSites = True
        analyzeWords=True        
     
        #**************************grab the search specs**************************
        searchID = thisSearch
        s=model.Search.get(searchID)
        
        #This might be a test search requested by the edit_search view.  If so
        #  we'll go for the first 50 hits; otherwise we'll find the maximum specified
        maxUrls = int(s.maxurls)
        #get the max content blocks
        maxContent = int(s.maxcontent)

        #this is the mandatory word that will anchor the text window
        targetword = s.targetword
        
        #see if the user wants to keep the previous URLs 
        #
        freezeurllist = s.freezeurllist
        deleteURLS = False
        if kwargs.get('extra_deleteExisting'):
            deleteUrls = True
            
        if debug:
            deleteURLS=False
    
        #determine whether or not to get new urls for this search 
        doharvestSiteNames = True
        if freezeurllist:
            doharvestSiteNames = False    
     
        #parse the search fields; provide null list if empty    
        if not s.urlsearchfor: 
            urlFind = [] 
        else: urlFind = s.urlsearchfor.split(',')  
        
        if not s.urleliminate: 
            urlEliminate =  [] 
        else: urlEliminate = s.urleliminate.split(',') 
        
        if not s.searchstring: 
            contentFind =  [] 
        else: contentFind = s.searchstring.split(',') 
        
        if not s.eliminationwords: 
            contentEliminate = [] 
        else: contentEliminate = s.eliminationwords.split(',')   
        
        thisUser = kwargs.get('userid')
        thisLpid = kwargs.get('extra_lpid')
        
    #**************************perform operations based on the specs************************** 
    
    #delete URLs if asked
        if deleteURLS and search_id>0:
            model.URLS.deleteBy(search_id = searchID)
    
        #pick up some new URLs if we need them
        if doharvestSiteNames:   
            #Get initial URLs over which to search.  Method developSearchString can take an
            #  additional argument to designate a search engine other than Google.  Logic is 
            #  currently set up only for Google, though.
            engine = 'Google'
            #developSearchString returns a single search string to encapsulate search criteria ...
            rawSearchStr = self.developSearchString(urlFind, urlEliminate, engine, maxUrls)
            #...while getInitSearchArray returns an array of requests to capture multiple pages of hits
            iUrl = self.getInitSearchArr(rawSearchStr, engine, maxUrls) 
            
            if len(contentFind + urlFind)>0:
                #send out the bot to grab promising URLs
                urlsFound = self.harvestSiteNames(iUrl,rawSearchStr)
                if len(urlsFound)>0:
                    self.dumpSitesToDataBase(urlsFound, True, thisSearch, thisUser) #second parameter clears existing content
                    #the raw url list is pretty messy relative to our needs; this routine cleans it up   
                    botUtilities.fixUrls(targetword, searchID, None)             
                    
        wipeContent = True        
        if readSites:
            if debugGrabContent:
                self.grabContent(targetword, BRACKETING_SENTENCES, wipeContent, self.maxChar, searchID, thisLpid)
            if debugCleanContent:    
                self.evaluateContentFitEntireSearch(contentEliminate + urlEliminate, contentFind + urlFind, searchID)
            #dumpContentToDataBase(urlsFound, True, thisSearch, thisUser)
            if debugAnalyzeContent:
                self.analyzeContentForEntireSearch(targetword, searchID)
            if debugScoreURL:    
                self.rollUpScoresByURLEntireSearch(searchID)
    
    def evaluateContentFitEntireSearch(self, contentEliminate, contentFind, search):
        #This analyzes the content to assay 'fit' to user specs; this could
        # get a lot better but for now we'll reject a content block  if it 
        # contains any elimination words or fails to have at least one 'find'
        # word
        content = model.Content.selectBy(searchid = search) 
        for c in content:
            isgood = self.evaluateContentFitSingleBlock(contentEliminate, contentFind, c.cont)
            if not isgood:  model.Content.delete(c.id)
    
    def evaluateContentFitSingleBlock(self, contentEliminate, contentFind, myCont):
        #This analyzes the content to assay 'fit' to user specs; this could
        # get a lot better but for now we'll reject a content block  if it 
        # contains any elimination words or fails to have at least one 'find'
        # word
            thisCont = myCont.lower()
            anyBad = False 
            #see if we have any 'elimination' words
            for word in contentEliminate:
                if string.find(thisCont, word.lower())>=0:
                    anyBad = True
            #now check if we have at least one sought-after word
            if not anyBad:
                if len(contentFind)==0:
                    anyGood=True  #we'll assume it passes if there are no content criteria
                else:    
                    anyGood = False
                for word in contentFind:
                    if string.find(thisCont, word.lower())>=0:
                        anyGood = True
            #if the content is good return true otherwise false            
            if not anyBad and anyGood:
                return True
            else: return False
      
                    
        
        
    def testIsValidURL(self, url):
        # TODO Should this be deleted? It's probably an orphan.
        #This routine pings the url to see if the site is valid  This spares us the prospect of raising
        #  errors in the bowels of httplib or urllib2.  This doesn't do a complete shakedown - urllib2 
        #  already handles "page not found", etc. errors.  Also, it just screens http: and https schemes;
        #  we're already filtering out .css sheets, ftp sites, etc.
        HTTP_PORT = 80
        HTTPS_PORT = 443
        httpFlavor, host, restOfAddress, query, fragment = urlsplit(url)
    
        #pick the right port
        if httpFlavor =='http':
            PORT = HTTP_PORT
        else:  PORT = HTTPS_PORT	
    
        s = None
        myRes = None
    
        try:  #trap the get address info error; this happens with really bad addresses like asfasf.synovate.com
            myRes = socket.getaddrinfo(host, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
        except socket.gaierror, msg: 
            myRes = None
            print 'invalid url: ' + host
            #raise 'continue'  #this syntax is a work-around to a Python parser error
            pass
        
        if myRes <> None:
            for res in socket.getaddrinfo(host, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
                af, socktype, proto, canonname, sa = res
                try:  #trap the broken socket types of errors
                    s = socket.socket(af, socktype, proto)
                except socket.error, msg:
                    s = None
                    continue
                try:
                    s.connect(sa)  #finally make sure we can actualy connect to the thing
                except socket.error, msg:
                    s.close()
                    s = None
                    continue
                break
            if s is None:
                print 'could not open socket to '+ host
                pass  #sys.exit(1)
            else: print 'successfully opened socket to ' + host
        else: 
            print 'invalid url: ' + host	
        if myRes == None or s == None:
            return False
        else: return True
    
    def getInitSearchArr(self, rawSearchStr, engine, maxUrls):
        #provides sites to search initially along with search syntax.  We'll want to go in and figure
        #  out how to get "deep" results with yahoo and othes.  For now we'll go to google's max
        
        initSearch=[] #an array in which we can store some tuple
        #grab 100 hits at a time (google's max)
        if maxUrls>100: 
            skipBy = 100
        else: 
            skipBy = maxUrls    
        if engine=='Google':
            for i in range(0, maxUrls, skipBy):
                mystr =   'www.google.com', '/search' + rawSearchStr + '&start='+ str(i)+'&sa=N'
                initSearch.append(mystr)
                
        #Logic for non-google engines but not tested for multiple queries
        if engine == 'Yahoo':         
            mystr =  'search.yahoo.com', '/search?p=#keyword#&fr=yfp-t-501&toggle=1&cop=mss&ei=UTF-8'
            initSearch.append(mystr)
        if engine == 'Snap':    
            mystr =  'snap.com', '/classicsearch.php?query=#keyword#'   
            initSearch.append(mystr)
        if engine == "Ask":    
            mystr='ask.com', '/web?q=#keyword#&search=&qsrc=0&o=0&l=dir'  
            initSearch.append(mystr)
    
        return initSearch[:]
    
    def developSearchString(self, urlFind, urlEliminate,  engine, maxUrls):                                 
        #Develop search string based on provided "look for" and "exclusion" terms.  
        #This works for Google now.  We'll want to refine it later to be able to use different
        #permutations and ordering of terms to better 'shake the tree'.    
        include =[]
        exclude =[]
        if engine == 'Google':
            tofind = urlFind 
            toeliminate =urlEliminate 
            for f in tofind:
                #clean up any inadvertant extra white space between words
                f=f.strip()
                f=re.sub('  ', ' ', f)  
                f=re.sub('  ', ' ', f)
                #put a - in place of any white space
                f=re.sub(' ', '-', f)  
                if len(f) > 0: 
                    if f.find('-'): #if we have a -, we need quotes
                        include.append('%22' + f + '%22')
                    else: include.append(f)    
            for e in toeliminate:
                #clean up any inadvertant extra white space between words
                e = e.strip()
                e=re.sub('  ', ' ', e)  
                e=re.sub('  ', ' ', e)
                #put a dash in place of any white space
                e=re.sub(' ', '-', e) 
                if len(e)>0:
                    if f.find('-'):
                        exclude.append('%22' + e + '%22')
                    else: exclude.append(d)    
            #concantenate the segments and translate to google-ese; create null string if none
            #...do the includes
            if len(tofind) > 0:
                allIncludes = '+'.join(include)
                #myIncludes = '?as_q=' + allIncludes
                myIncludes =  allIncludes
            else: myIncludes = ""
            #...and the excludes
            if len(toeliminate) > 0:
                allExcludes = '+-' + '+-'.join(exclude)  #makes string "+-exclude[0]+-exclude[1] ..." 
                #myExcludes = '&as_epq=&as_oq=&as_eq=' + allExcludes
                myExcludes = allExcludes
            else: myExcludes = ""  
             #set the number of hits to request (google max is 100)
            if maxUrls > 100:
                num = '100'
            else:
                num = str(maxUrls)
            #set the search string
            searchString = '/search?h1=en'+ '&as_qdr=all' + '&q=' + myIncludes + myExcludes + '&num=' + num
            
        return searchString
    

        
    def harvestSiteNames(self, urls,rawSearchStr):
        
        #This function sends a bot to ping the search engines
        urlsFound = [] #we'll stash the results here
        for s in urls:
            #this is a bit sleazy, but if there's only one url passed, 'urls' comes in as a tuple
            # otherwise it comes in as a list of tuples; we want to operate on a tuple object
            if type(urls)==tuple:
                site = urls
            else: site = s    
            
            #grab information from the site[] array; site[0] has the root url; 
            # site[1] has the specific search syntax.  'keyword' will typically be the client name
            searchString = rawSearchStr
            #build the url for the query; convert to str type to avoid unicode u'<whatever>'
            urlRequested = str('http://' + site[0] + '/' + searchString)       
            
            #UPDATED to feedparser.  use openanything to capture the content; it encapsulates urllib2 and provides polite error handling
            #returnedPage = self.callOpenAnything(urlRequested)
            returnedPage=getContentWithFeedparser(urlRequested)
            #if the return code is in 400 series (invalid/bad request) or 500 series (server error) don't bother 
            returnStatus = returnedPage.get('status')
            if returnStatus < 400:
                #content = returnedPage.get('data') #grab the results    
                content = returnedPage.get('cont')
                rawUrlsFound = returnedPage.get('links')
                #rawUrlsFound = re.findall('href="http://.*?"', content) #snag the links
                for rawUrl in rawUrlsFound:  #clean the raw urls up
                    betterUrl = rawUrl.replace('href=','')
                    evenBetterUrl = betterUrl.replace('"','')
                    #trap obviously bad urls (move this off to it's own routine eventually)
                    cssFound =evenBetterUrl.find(".css") #this is a cascading style sheet
                    if not cssFound>0: 
                        urlsFound.append(betterUrl) 
            else: print returnedPage.get('url')	 
        #deDupedUrls = botUtilities.uniq(urlsFound) #get rid of the duplicates 
        return urlsFound
                                 
    
    def grabContent(self, targetword, bracketing_sentences, wipeContent, maxChar, searchID, lpid):
        #Goes on line, searching sites in the database looking for content containing a single word
        lowertargetword = targetword.lower()
        
        #first, kill 'content' for this search if requested
        if wipeContent and searchID > 0:  #we won't delete any content w/ id = 0 (this is admin cache)
            model.Content.deleteBy(searchid = searchID)
    
        #find the delimiters that mark the beginning and end of blocks of text data
        myDelimiters=botUtilities.getTextSearchDelimiters()   
        myurls = model.URLS.selectBy(search_id=searchID)
        for u in myurls:
            doneWithSite = False
            urlRequested= str(u.urltext)
            urlID = u.id
            #clean up the raw URL
            urlRequested = urlRequested.replace("'","")
            #ping the site w/ a light-weight routine and a short timeout.  Malformed URLs, etc. will throw errors here
            #  instead of in the bowels of the socket routines.
            socket.setdefaulttimeout(2)  
            print("pinging "+urlRequested)
            if self.testIsValidURL(urlRequested): 
                searchstr = urlRequested
                #check if we've queried the site before (we'll have non-null etag and/or lastmodified field)
                #  this isn't working right - can't pass in a tuple.  fix later
                searchstr = urlRequested   
                try :
                    #returnedPage = self.callOpenAnything(searchstr)
                    returnedPage = getContentWithFeedparser(searchstr)
                    #look at the return status to figure out what to do
                    returnStatus = returnedPage.get('status')
                    if returnStatus ==304: doneWithSite = True # we've checked and there's no new content
                    #sadly, some sites trap and encapsulate 'no hit' queries returning a status of 200 ('ok')
                    #  we'll look for the number '404' and words 'not found' as a surrogate
                    #content = returnedPage.get('data') #grab the results
                    content = returnedPage.get('cont') #grab the results
                    if content.find('404') > 0 or content.find('Not Found')>0: doneWithSite =True                
                except:
                    returnStatus = 400 #set a fake, 'transaction failed' return code if it times out 
                    doneWithSite =True  
                if returnStatus <400 and not doneWithSite: #there's meaningful content  
                    print("...site answered")
                    lowerContent = content.lower()
                    shouldBeGood = False
                    if lowerContent.find(lowertargetword):
                        print(' ...*should* have good content')
                        shouldBeGood = True
                    newEtag = returnedPage.get('etag') 
                    #add etag to our database
                    if not newEtag == None:
                        try:
                            rowObj = model.URLS.get(u.id)
                            rowObj.set(etag = newEtag)
                        except:
                            pass
                    myGMTtime = datetime.now()
                    foundAnyContent = False
                    for delimiter in myDelimiters:
                        lookForBegin= delimiter[0]
                        lookForEnd = delimiter[1]
                        starts = [match.start() for match in re.finditer(re.escape(lookForBegin), content)]
                        myPithyStrings = []
                        
                        for s in starts:
                            #snag the content of this block of text                            
                            end = content.find(lookForEnd, s+1) + len(lookForEnd)
                            thisBlock = content[s:end]
                            cleanBlock = botUtilities.stripHTMLtags(thisBlock) 
                            #scrub the funky characters &nbsp, untranslated unicode, etc.
                            reallyCleanBlock = botUtilities.stripHTMLunicodeEtc(cleanBlock)
                            #make an array of the punctuation (we can add it back in later)
                            if shouldBeGood:
                                a=0
                            punctuation=[]
                            for i in range(len(reallyCleanBlock)):
                                if reallyCleanBlock[i]=='.' or reallyCleanBlock[i] =='!' or reallyCleanBlock[i] == '?':
                                    punctuation.append(reallyCleanBlock[i])
                            #provide an extra element        
                            punctuation.append('...')    
                            #parse the block into sentences (delimited by '.', '?', '!')
                            parsedContent = re.sub('[.!?]', '\n', reallyCleanBlock)
                            #escape out quotes so we don't confuse mySQL (insert a \); 
                            #I can't figure out how to just send one \ because Python uses the same escape character.
                            parsedContent = re.sub('"', '\"', parsedContent)
                            parsedContent = re.sub("'", "\'", parsedContent)
                            mySentences = parsedContent.split('\n')
                            #we'll keep every sentence containing our magic word and <bracketing_sentences> 
                            #  on either side of it
                            #create a null truth table:
                            keptSentences = []
                            needElipsis = False
                            for i in range(len(mySentences)):
                                keptSentences.append(False)
                            #update the truth table based on the contents    
                            for sent in range(len(mySentences)):
                                lowerSent = mySentences[sent].lower()
                                if lowerSent.find(lowertargetword) >=0: 
                                    keptSentences[sent]=True
                                    #add the line before if it makes sense
                                    if sent > bracketing_sentences: keptSentences[sent-bracketing_sentences] =True
                                    #add the line after if it makes sense
                                    if sent < len(mySentences)-bracketing_sentences: keptSentences[sent+bracketing_sentences] = True
                                    
                            #if we've dug anything up, sent a polite string to the database        
                            if len(mySentences)>0:
                                finishedString =''                            
                                for s in range(len(keptSentences)):
                                    if keptSentences[s]:
                                        if s<len(punctuation):
                                            finishedString = finishedString + mySentences[s] + punctuation[s] + " " 
                                        else: finishedString = finishedString + mySentences[s] +" "       
                                    else: #add elipsis if this is a skipped sentence, not the first one,
                                          #and at least one more good sentence follows.
                                        if s < len(keptSentences)-1 and s > 1:
                                            moreFollow = False
                                            for ss in range(s+1, len(keptSentences)):
                                                if keptSentences[ss]:
                                                    needElipsis=True
                                        
                                #check for length to ensure fit to db
                                if len(finishedString) > maxChar:
                                    finishedString = finishedString[:maxChar]  
                                #remove leading/trailing spaces
                                finishedString = finishedString.strip()
                                    
                               #add it to the database if we don't have a null block (i.e. 
                               #  our product was mentioned at least once)                                    
                                if len(finishedString) > 20:  #don't bother getting really short snippets
                                    foundAnyContent = True
                                    try:
                                        model.Content(urlid=urlID, cont= finishedString, urltext = u.urltext,
                                                      dateaccessed=myGMTtime, searchid = int(searchID), lpid = int(lpid))
                                        print 'adding content ' + finishedString[:20] +'... from ' + u.urltext
                                    except:	
                                        goodContent=False
                                        pass
                            
                    #Check if we have *any* content mentioning our product (we may not).  If we have none,
                    #  check the database to see if have any stored content from this site.  If we've never  
                    #  picked up content, delete the URL.
                    if  foundAnyContent:
                        print("...found content")                       
                    else:   
                        print("...deleting for lack of content")
                        if shouldBeGood:
                            print "Houston, we have a problem."
                            a=0
                        rowObj = model.URLS.get(u.id)
                        rowObj.set(deleteme=True)
                #end of valid return code block            
                else:  
                    print("...deleting due to return status of "+str(returnStatus))
                    rowObj = model.URLS.get(u.id)
                    rowObj.set(deleteme=True)                
            else: #null return from url ping
                rowObj = model.URLS.get(u.id)
                rowObj.set(deleteme=True)
                print("...deleting due to failure of initial ping")
                
        #delete the bummer sites        
        if int(lpid) > 0: model.URLS.deleteBy(deleteme=True)
     
    def analyzeContentForEntireSearch(self, targetword, search):
    
        #conduct an analysis on each block of relevant content.  This will obviously get more sophisticated, but for now
        #  we'll look for positive and negative associations of each surrounding word using Harvard's semantic dictionary
        #Instantiate a translator object and tell it what to keep (we'll get rid of punctuation)
        tran= Translator(keep = string.ascii_lowercase)
    
        #load content table
        mycont = model.Content.selectBy(searchid=search)
        for c in mycont: 
            contID = c.id
            urlID = c.urlid
            content= c.cont
            date= c.dateaccessed
            polarityscore, poswords, negwords = self.analyzeSingleContentBlock(content)           
            rowObj = model.Content.get(c.id)
            rowObj.set(polarity=polarityscore)
   
    def rollUpScoresByURLEntireSearch(self, searchID):
        #this routine assigns a polarity score to each URL by rolling the the scores
        #  found for each block of content
    
        myurls = model.URLS.selectBy(search_id = searchID)
        #this instansiates a string.translate wrapper class (above)
        trans = Translator(keep = string.digits)
        transWord = Translator(keep = string.ascii_lowercase)
    
        #Set the polarity score for each URL (aggregating all content)
        for u in myurls:
            #the next line creates a lower case string from the tuple (yes, the tuple) 
            #returned from the DB
            myId = u.id
            mycontent = model.Content.selectBy(urlid=str(myId))
            polarityscore = 0
            for c in mycontent:
                polarityscore = polarityscore + c.polarity
            rowObj = model.URLS.get(myId)
            rowObj.set(polarity=polarityscore)
    
    def dumpSitesToDataBase(self, sites, clearContents, thisSearch, thisUser):
        #adds list of sites to database intact; we can go through and filter these later
        search_id = int(thisSearch)
        userid=thisUser    
    
        if clearContents and search_id>0: #protects admin searches
            model.URLS.deleteBy(search_id=int(searchID)) 
           
            
        for i in range(len(sites)):
            urlText = sites[i]
            #trim the URL to exclude bracketing quotes (original format is "'<url>'")
            urlText = urlText[1:-1]
            #parse the site names into constituent elements
            scheme, netloc, path, query, fragment = urlsplit(urlText)
            #enclose each returned string in ' ' 
            scheme = "'" + scheme + "'"
            netloc = "'" + netloc + "'"
            path = "'" + botUtilities.fixSQLquotes(path) + "'"
            query = "'" + botUtilities.fixSQLquotes(query) + "'"
            fragment = "'" + botUtilities.fixSQLquotes(fragment) + "'"
            urltext = "'" + botUtilities.fixSQLquotes(urlText) + "'"
            datefound = datetime.now()
            goodContent = True
    
            #Ensure URL is less than 500 characters (reasonable max, I think)
            if len(urltext) < 500:
                #put this in a try block; sometimes a stange character slips in and makes the
                #  database barf
                try:
                    myURL = model.URLS(scheme = scheme, netloc=netloc, path=path,
                                   query = query, fragment=fragment, urltext=urltext,
                                   search_id = search_id, datefound=datefound, userid = userid)
                except :	
                    pass
           




    def visitScoreStoreSingleURL(self, searchid, u, scoreContent, deleteme):
        #This is a 'light' version of runLP.  It's designed to quickly test a a user's
        #  search specification by:
        #    1.  grabbing content from the urls specified for a search
        #    2.  screening it agains the search criteria
        #    3.  adding the content to the content database
        #It does not score the content

        #grab the search object
        thisSearch = model.Search.get(searchid)  
        thisUser = thisSearch.userid
       
        #myDelimiters=botUtilities.getTextSearchDelimiters()
        
        now = datetime.now()
        #snag content from this url
        #mydict = self.grabContentFromSingleUrl(
        #    thisSearch.targetword, self.BRACKETING_SENTENCES, 
        #    self.maxChar, u.urltext, myDelimiters)
        mydict = self.getContentWithFeedparser(u.urltext, thisSearch.targetword)    #self, url, targetword=None 
        thiscontent = mydict.get('cont')  #a list of content containing target word
        etag = mydict.get('etag')  #the etag (date stamp) from the site
        #clean it up a bit by applying content-level filter(s)
        cleancont = self.applyContentLevelFilter(thiscontent, thisSearch.eliminationwords, thisSearch.searchstring)
        #add the content
        if len(cleancont)>0:
            try:
                if scoreContent:
                    for c in cleancont:
                        polarity, poswords, negwords = self.analyzeSingleContentBlock(c)
                        model.Content(urlid=u.id, cont= c, urltext = u.urltext, userid = thisUser,
                            dateaccessed=now, searchid = searchid, polarity = polarity,
                            poswords = poswords, negwords = negwords, deleteme = deleteme)  
                    return 'good'    
                else:
                    for c in cleancont:
                        model.Content(urlid=u.id, cont= c, urltext = u.urltext,
                            dateaccessed=now, searchid = searchid, userid = thisUser, deleteme = deleteme)     
                    return 'bad'
            except:
                return 'bad'
    
           
    def getContentWithFeedparser(self, url, targetword=None):
        #gets the content from a single url using feedparser.py.  If targetword is included as an
        #  argument, it returns a list of content snippets (a bit on each side of the target word).  
        #  Otherwise it returns a list of intact content blocks.  In either case, it returns a
        #  dict(content = cont, etag = etag, datestamps = entrydatestamp, links = links).
        
        #Alas and alak, feedparser doesn't get content from many normal (html) web pages.  The entries
        #  list simply comes back empty.  In this case we'll parse it the old fashion, "pat" way.
        
        import feedparser
        #set some defaults to ensure there's something (even None or a null list) to return
        links=[];   cont = []; datestamps = []; datablocks = []; entrydatestamp = None; etag = None; entries = []; snippetlist = []; 
        snippetdates = []; pagedatestamp = (1900, 1, 1, 12, 0, 0, 0, 0, 0)
        #set up a faux dictionary in case feedparser has an issue
        mypage = dict(links= links, content= cont, entries = entries, etag=etag, update_parsed = entrydatestamp)
        #grab the content with feedparser.  One issue I've found is that some sites are *huge*
        try:
            print "feedparser now parsing " + url
            mypage = feedparser.parse(url)    #invokes the parser

        except: #if feedparser barfed, return the null object
            return mypage
        
        rawcontent = mypage.get('raw_input')
        #if there's no raw data, feedparser parsed successfully
        if not rawcontent:  
            entrylist = mypage.get("entries")   #grabs the list of entries, each of which is a dict
            feedmeta = mypage.get("feed")     #grabs the feed meta data dict
            status = mypage.get("status")     #the return code (200 is good, 400 is server error, etc.)
            etag = mypage.get("etag")
            pagedatestamp = feedmeta.get("update_parsed")    # a tuple (year, mon, day, hour, min, sec, x, x, x)
            goodxml = mypage.get("bozo")      #binary assessment of well-formed xml on page; if 1 the bad page
            #read each entry in the blog
            if entrylist:
                snippetdates = []
                for entry in entrylist:
                    entrydatestamp = entry.get("update_parsed")
                    linklist = entry.get("links")            #a list of dict items with link info
                    contentlist = entry.get("content")       #yes, another list of dict items containing - you guessed it - the content
                    #create a list of the links
                    if linklist:
                        for link in linklist:
                            links.append(link.get("href"))        #the canonical url  (feedparser makes its best guess)
                        #...and a list of the content
                        if contentlist:
                            for c in contentlist:
                                rawcont = c.get("value")              #the content -  a bit messy vis-a-vis tags
                                conttype = c.get("type")              #this is the type of content e.g., text, xhtml
                                parseme = False
                                
                                if len(rawcont) > 0:  #make sure the content isn't null
                                
                                    if targetword:    #if we have specified targetword, we might parse out the block
                                        if rawcont.find(targetword) > 0:  #we'll do a quick check to see if we have it in the content
                                            parseme = True
                                    else: parseme = True  #if no target word specified, go ahead and parse teh content
                                
                                if parseme:    
                                    #we'll clean up the raw catch a bit (get rid of funky characters, tags, etc.)
                                    cleancont = botUtilities.stripHTMLtags(rawcont)
                                    supercleancont = botUtilities.stripHTMLunicodeEtc(cleancont)
                                    cont.append(supercleancont)
                                    datestamps.append(entrydatestamp)
                                    #now parse out the strip out the snippets containing the content of interest
                                    snippetlist = []; snippetdates=[]
                                    for c, d in zip(cont, datestamps):
                                        #we get a dict of etag, cont; cont is a list of the text snippets
                                        thiscontent = self.grabContentBlocksFromText(c, targetword).get('cont')
                                        for snippet in thiscontent:
                                            snippetlist.append(snippet)
                                            snippetdates.append(d) 
                                                
            return dict(cont = snippetlist, etag = etag, datestamps = snippetdates, links = links)

        else:  #if feedparser returned 'rawcontent', it wasn't happy, so we'll handle the data differently
            myreturn = self.grabContentBlocksFromText(rawcontent, targetword)   
            snippetlist = myreturn.get('cont')
            etag = myreturn.get('etag')
            links = botUtilities.digUrlsOutOfText(rawcontent)
            return dict(cont = snippetlist, etag = etag, datestamps = pagedatestamp, links = links)

    
    # TODO Replace this with Visitor
    def visitUrlsFeedParser(self, searchid, scoreContent, deleteme, maxUrls = None):
        #This is a 'light' version of runLP.  It's designed to quickly test a a user's
        #  search specification by:
        #    1.  grabbing content from the urls specified for a search
        #    2.  screening it agains the search criteria
        #    3.  adding the content to the content database
        #

        #grab the search object
        thisSearch = model.Search.get(searchid)  
        thisUser = thisSearch.userid
        targetword = thisSearch.targetword
       
        #myDelimiters=botUtilities.getTextSearchDelimiters()
        botUtilities.deDupUrls(searchid)  #de-duplicates the urls
        
        botUtilities.fixUrls(thisSearch.targetword, searchid)    #gets rid of urls we don't want
        urls = model.URLS.selectBy(search_id = searchid)
        results = []
        if maxUrls:
            urls = urls[0:maxUrls]  #this works even if maxUrls > len(urls)
        for u in urls:
            now = datetime.now()
            #myurl = str(u.urltext)
            #mytarget = str(thisSearch.targetword)
            #myurl = 'http://en.wikipedia.org/wiki/Microsoft'
            #snag content from this url
            mydict = self.getContentWithFeedparser(u.urltext, targetword)
            #mydict = self.grabContentFromSingleUrl(
            #    thisSearch.targetword, self.BRACKETING_SENTENCES, 
            #    self.maxChar, u.urltext, myDelimiters)
            thiscontent = mydict.get('cont')  #a list of content containing target word
            etag = mydict.get('etag')  #the etag (date stamp) from the site
            #clean it up a bit by applying content-level filter(s)
            cleancont = self.applyContentLevelFilter(thiscontent, thisSearch.eliminationwords, thisSearch.searchstring)
            #add the content
            for c in cleancont:
                attributes = dict(urlid=u.id, cont= c, urltext = u.urltext, userid = thisUser,
                    dateaccessed=now, searchid = searchid, deleteme = deleteme)
                # TODO why is this scoring content again?
                content = model.Content(**attributes)
                if scoreContent:
                    self.addScoreToContent(content)
                results.append(content)
        return results
                    
    def addScoreToContent(self, content):
        if int(content.polarity) == 666:
            polarity = self.analyzeSingleContentBlock(content.cont)
            polarityscore, poswords, negwords = polarity
            content.polarity = int(polarityscore)
            content.poswords = poswords
            content.negwords = negwords
                    
    def grabContentBlocksFromText(self, content, targetword=None):
        #this routine takes a block of text, scrubs the html tags, finds snippets around the target word;
        #  it does not analyze the content - this is handled in a separate step.
        if targetword:  lowertargetword = targetword.lower()
        #clean up the catch
        cleanBlock = botUtilities.stripHTMLtags(content) 
        #scrub the funky characters &nbsp, untranslated unicode, etc.
        reallyCleanBlock = botUtilities.stripHTMLunicodeEtc(cleanBlock)
        #make an array of the punctuation (we can add it back in later)   
        punctuation=[]
        #set a null list to hold the return
        returnContent=[]
        #parse the content into sentences (delimited by '.', '?', '!'); grab the punctuation separately
        for i in range(len(reallyCleanBlock)):
            if reallyCleanBlock[i]=='.' or reallyCleanBlock[i] =='!' or reallyCleanBlock[i] == '?':
                punctuation.append(reallyCleanBlock[i])
        parsedContent = re.sub('[.!?]', '\n', reallyCleanBlock)   
        mySentences = parsedContent.split('\n')
        lastSentence = len(mySentences)-1
        
        if not targetword:
            #if we don't have a target word, we'll re-assemble and return the whole block of text
            for s in mySentences:
                cleanSentence= s.strip()
                    #sometimes there is no trailing punctuation mark, which causes the punctuation
                     #  list to go out of range; this isn't mission critical, so we'll just give it
                     #  a period if there's an issue.
                try:
                    punct = punctuation[s]
                except: 
                    punct = "."
                    thisBlock = thisBlock + cleanSentence + punct + "  "
    
            thisBlock = thisBlock.strip() #gets rid of trailing spaces
            if len(thisBlock) > 0 and len(thisBlock) < self.maxChar:  #makes sure it fits database
                returnContent.append(thisBlock)            
     
           #the return contains a faux etag (for compatibility with older code)
            newEtag = ''
            return dict(etag = newEtag, cont = returnContent)             
            
        else:        
        
            #We *do* have a target word, so loop through the sentences looking for the target word
            done = False
            pointer = 0
            while not done:
                lowerSent = mySentences[pointer].lower()
                targetFound = False
                if lowerSent.find(lowertargetword) >=0: 
                    #Ok.  This sentence has the target word.  Compose a block of the surrounding
                    #  text, as appropriate (stay within the range of the sentence list).
                    targetFound = True
                    if pointer > botUtilities.BRACKETING_SENTENCES: 
                        first = pointer - botUtilities.BRACKETING_SENTENCES 
                    else: first = pointer
                    if pointer + botUtilities.BRACKETING_SENTENCES <= lastSentence:
                        last = pointer + botUtilities.BRACKETING_SENTENCES
                    else: last = lastSentence
                    thisBlock = ''
                    for s in range (first, last+1):  #this looks strange, but the syntax grabs the last element
                        #get rid of really short sentences; they might be enumerated lists "1.",
                        #  elipses "..." or repeated punctuation "!!!!"
                        cleanSentence = mySentences[s].strip()
                        #sometimes there is no trailing punctuation mark, which causes the punctuation
                        #  list to go out of range; this isn't mission critical, so we'll just give it
                        #  a period if there's an issue.
                        try:
                            punct = punctuation[s]
                        except: 
                            punct = "."
                        if len(cleanSentence) > 5:
                            thisBlock = thisBlock + cleanSentence + punct + "  "
    
                    thisBlock = thisBlock.strip() #gets rid of trailing spaces
                    if len(thisBlock) > 0 and len(thisBlock) < botUtilities.maxChar:  #makes sure it fits database
                        returnContent.append(thisBlock)
                #set the pointer to the next sentence (ensure no overlap), test for completion
                if targetFound: 
                    pointer = last + 1
                else: 
                    pointer = pointer + 1
                if pointer > lastSentence: done = True
    
            #the return contains a faux etag (for compatibility with older code)
            newEtag = ''
            return dict(etag = newEtag, cont = returnContent)  
    
    def addUrlsFromDeque(self, searchid, deleteme, deq):
        #adds urls to database from a deque object
        now = datetime.now()
        for d in deq:
            scheme, netloc, path, query, fragment = urlsplit(d)
            model.URLS(scheme = scheme, netloc=netloc, path=path, 
                                   query = query, fragment=fragment, urltext=d,
                                   datefound=now,  search_id = searchid, deleteme = deleteme)              
    
if __name__ == '__main__':
    debug = False
    if debug:
        myBotRoutines = BotRoutines()
        #myBotRoutines.testFeedParser()
        retdicts=[]
        urls =[]
        urls.append("http://gizmodo.com/5039860/gates-and-seinfeld-to-answer-apples-pc-vs-mac-ads")
        urls.append("http://www.geekologie.com/2008/08/microsoft_recruits_gates_seinf.php")
        urls.append("http://www.businessweek.com/the_thread/brandnewday/archives/2008/09/microsoft_gates.html?campaign_id=rss_blog_brandnewday")
        urls.append("http://www.macobserver.com/article/2005/05/03.2.shtml")
        urls.append("http://news.softpedia.com/news/Microsoft-039-s-Apple-Get-a-Mac-Killer-Is-Live-93028.shtml")
    
        
        for url in urls:
            retdict = myBotRoutines.getContentWithFeedparser(url, "microsoft")    #self, url, targetword=None
            print "now parsing: " + url
            retdicts.append(retdict)
    pass

