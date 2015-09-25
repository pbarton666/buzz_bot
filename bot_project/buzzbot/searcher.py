# Standard libraries
from collections import deque
from urlparse import urlsplit
import datetime
import re
import socket
import types
import urllib
import urllib2

# Third-party libraries
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import openanything
import simplejson

# TurboGears libraries
from turbogears.identity import *
from turbogears import identity

import logging
logger = logging.getLogger("buzzbot.searcher")

DEBUG_ON= False
if not DEBUG_ON:
    import model
    # TODO move bot routines and utilities to real classes and functions
    import bot
    myBotRoutines = bot.BotRoutines()
    import botUtilities
    botUtilities = botUtilities.Utilities()

def permutation(lst):
    queue = [-1]
    lenlst = len(lst)
    while queue:
        i = queue[-1]+1
        if i == lenlst:
            queue.pop()
        elif i not in queue:
            queue[-1] = i
            if len(queue) == lenlst:
                yield [lst[j] for j in queue]
            queue.append(-1)
        else:
            queue[-1] = i

def combinations(n, k):
    #n is number of choices, k is the number of elements in each combination returned
    # returns
    current = range(1, k + 1)
    max = range(n - k + 1, n + 1)
    while current != max:
        for number in current:
            print 'combinations %2d'% (number),
        index = -1
        if current[index] != max[index]:
            current[index] = current[index] + 1
        else:
            for indices in range(-2, -k - 1, -1):
                if current[indices] != max[indices]:
                    current[indices] = current[indices] + 1
                    for other_indices in range(indices + 1, 0):
                        current[other_indices] = current[indices] + other_indices - indices
                    break
    return max

def getUserID():
    #gets the user id, substitutes a guest login id if none available (this happens if cookies
    #  are blocked)
    GUESTID = 3
    msg=""
    thisUserIDObj = identity.current.identity()

    #tg's identity module relies on cookies.  If the user has these blocked, the user is
    #  set to 'None', which confuses the routine.  In this case, we'll provide a 'guest' id
    #  and a notification
    if thisUserIDObj.user_id == None:
        setUser(GUESTID)
        thisUserIDObj = identity.current.identity()
        msg = "Note: you are logged in as guest because cookies are blocked on your browser."
    thisUser = thisUserIDObj.user_id
    thisUserGroup = thisUserIDObj.groups
    return dict(id=thisUser, groups=thisUserGroup, msg=msg)

def setUser(thisid):
    user =User.get(thisid)
    visit_key=tg.visit.current().key
    #VisitIdentity = tg.identity.soprovider.TG_VisitIdentity
    IdentityObject = tg.identity.soprovider.SqlObjectIdentity
    try:
        link =VisitIdentity.selectBy(visit_key)
    except :
        link = None
    if not link:
        link =VisitIdentity(visit_key=visit_key, user_id=user.id)
    else:
        link.user_id =user.id
    user_identity = IdentityObject(visit_key)
    identity.set_current_identity(user_identity)

def getLpidFromSearchID(searchid):
    #looks up the lpid given a searchid
    thislp = model.Listeningpost.selectBy(searchtorun=searchid)
    return thislp[0].id



class BaseSearcher(object):
    NON_EMPTY_STRING = re.compile('\w')
    def __init__(self, include=None, exclude=None, search_id=None, search=None, max_results=None, referer=None, key=None):
        """
        Instantiate a searcher.

        Keyword arguments:
        * `search_id`: Search record id to get.
        * `max_results`: Maximum number of results to return.
        * `referer`: Referer path to provide for search queries.
        * `key`: API key to send with search queries.
        """
        self.candidates = deque()
        self._position = 0
        self._search = None
        self._include = []
        self._exclude = []

        if search:
            self._search = search
        if search_id:
            self._search = model.Search.get(search_id)
        if self._search:
            self._include = self._search.urlsearchfor
            self._exclude = self._search.urleliminate
        if include:
            self._include = include
        if exclude:
            self._exclude = exclude

        self._max_results = max_results or 10
        self._referer = referer or "http://synovate.com/"
        self._key = key

        self._query = None

    @classmethod
    def _sanitize_string(self, string):
        return string.encode('latin1', 'replace')

    @classmethod
    def _split_delimited_string(self, string):
        """
        Return a list by splitting a delimited `string`. If the input is already a list, just return it.
        """
        return isinstance(string, types.StringType) and string.split(',') or string

    def next(self):
        """
        Perform a partial search and return a list of the next results.

        Subclasses must implement this.
        """
        raise NotImplemented()

    def search(self):
        """
        Perform search and return list of resulting URLs.

        Do not implement this, just ues the BaseSearcher's method.
        """
        while True:
            candidates = self.next()
            if not candidates or self._position >= self._max_results:
                break
        return self.candidates


class GoogleSearcher(BaseSearcher):
    """
    Search via Google. See documentation for `BaseSearcher`.
    """

    def __init__(self, max_results=64, referer="http://google.com/", **kwargs):
        BaseSearcher.__init__(self, max_results=max_results, referer=referer, **kwargs)
        # TODO Do we really need permutations? If so, then need to make self._queries list.
        self._query = self._query_for(include=self._include, exclude=self._exclude)

    @classmethod
    def _query_for(self, include, exclude):
        query = u""
        for phrase in self._split_delimited_string(include):
            if self.NON_EMPTY_STRING.match(phrase):
                query += u" \"%s\"" % phrase
        for phrase in self._split_delimited_string(exclude):
            if self.NON_EMPTY_STRING.match(phrase):
                query += u" -\"%s\"" % phrase
        return query

    def next(self):
        if self._position >= self._max_results:
            return None
        params = urllib.urlencode({'q': self._query, 'v': '1.0', 'rsz': 'large', 'start': self._position})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?%s' % (params)
        logger.debug("GoogleSearcher: retrieving %s" % (url))
        req = urllib2.Request(url)
        req.add_header('Referer', self._referer)
        try:
            self._response = urllib2.urlopen(req)
            self._body = self._response.read()
        except Exception, e:
            logger.error("GoogleSearcher: %s" % e)
            return []
        self._doc = simplejson.loads(self._body)
        if self._doc['responseStatus'] != 200:
            return None
        candidates = []
        for element in self._doc['responseData']['results']:
            result = self._sanitize_string(element['url'])
            candidates.append(result)
            self.candidates.append(result)
        self._position += len(self._doc['responseData']['results'])
        logger.debug("GoogleSearcher: found %s matches" % len(candidates))
        return candidates



class YahooSearcher(BaseSearcher):
    """
    Search via Yahoo. See documentation for `BaseSearcher`.
    """

    def __init__(self, max_results=100, referer="http://yahoo.com/", key="tjF4bq7V34G2HmcBVfiZqVur_LEM04ze1THb_actrW9M60yWJfAG.ptPLg--", **kwargs):
        BaseSearcher.__init__(self, max_results=max_results, referer=referer, key=key, **kwargs)
        # TODO Do we really need permutations? If so, then need to make self._queries list.
        self._query = self._query_for(include=self._include, exclude=self._exclude)

    @classmethod
    def _query_for(self, include, exclude):
        query = u""
        for phrase in self._split_delimited_string(include):
            if self.NON_EMPTY_STRING.match(phrase):
                query += u" \"%s\"" % phrase
        for phrase in self._split_delimited_string(exclude):
            if self.NON_EMPTY_STRING.match(phrase):
                query += u" -\"%s\"" % phrase
        return query

    def next(self):
        if self._position >= self._max_results:
            return None
        results_per_page = self._max_results < 100 and self._max_results or 100
        params = urllib.urlencode({'query': self._query, 'appid': self._key, 'start': self._position, 'results': results_per_page, 'output': 'json'})
        url = 'http://search.yahooapis.com/WebSearchService/V1/webSearch?%s' % (params)
        logger.debug("YahooSearcher: retrieving %s" % (url))
        req = urllib2.Request(url)
        req.add_header('Referer', self._referer)
        try:
            self._response = urllib2.urlopen(req)
            self._body = self._response.read()
        except Exception, e:
            logger.error("YahooSearcher: %s" % e)
            return []
        self._doc = simplejson.loads(self._body)
        candidates = []
        for element in self._doc['ResultSet']['Result']:
            result = self._sanitize_string(element['Url'])
            candidates.append(result)
            self.candidates.append(result)
        self._position += len(candidates)
        logger.debug("YahooSearcher: found %s matches" % len(candidates))
        return candidates



class TechnoratiSearcher(BaseSearcher):
    """
    Search via Technorati. See documentation for `BaseSearcher`.
    """

    def __init__(self, max_results=100, referer="http://api.technorati.com/", key="de1ae02365787a36717618b4814cf7ea", **kwargs):
        BaseSearcher.__init__(self, max_results=max_results, referer=referer, key=key, **kwargs)
        # TODO Do we really need permutations? If so, then need to make self._queries list.
        self._query = self._query_for(include=self._include, exclude=self._exclude)

    @classmethod
    def _query_for(self, include, exclude):
        query = u""
        for phrase in self._split_delimited_string(include):
            if self.NON_EMPTY_STRING.match(phrase):
                query += u" \"%s\"" % phrase
        # TODO Is there really no way to make Technorati exclude words?!
        #for phrase in self._split_delimited_string(exclude):
        #    if self.NON_EMPTY_STRING.match(phrase):
        #        query += u" -\"%s\"" % phrase
        return query

    def next(self):
        if self._position >= self._max_results:
            return None
        results_per_page = self._max_results < 100 and self._max_results or 100
        params = {
            "key": self._key,
            "query": self._query,
            "format": "xml",
            "language": "en",
            "authority": "a4",
            "start": self._position,
            "limit": results_per_page,
        }
        url = "http://api.technorati.com/search?%s" % urllib.urlencode(params)
        logger.debug("TechnoratiSearcher: retrieving %s" % (url))
        req = urllib2.Request(url)
        try:
            self._response = urllib2.urlopen(req)
            self._body = self._response.read()
        except Exception, e:
            logger.error("TechnoratiSearcher: %s" % e)
            return []
        self._doc = BeautifulStoneSoup(self._body)
        candidates = []
        nodes = self._doc.findAll("item")
        for node in nodes:
            # `permalink` is the blog entry, `url` is the blog's homepage
            result = self._sanitize_string(node.find("permalink").contents[0])
            candidates.append(result)
            self.candidates.append(result)
        self._position += len(candidates)

        logger.debug("TechnoratiSearcher: found %s matches" % len(candidates))
        return candidates



class MultiSearcher(BaseSearcher):
    """
    Searches using multiple searcher engines.
    """

    searcher_classes = [
        GoogleSearcher,
        YahooSearcher,
        TechnoratiSearcher,
    ]

    def __init__(self, searcher_classes=[], **kwargs):
        self.candidates = deque()
        self._searchers = []
        self._kwargs = kwargs
        for searcher_class in (searcher_classes or self.searcher_classes):
            self._searchers.append(searcher_class(**self._kwargs))
        self._active_searchers = []
        self._active_searchers.extend(self._searchers)

    def next(self):
        results = []
        for searcher in self._active_searchers:
            searcher_results = searcher.next()
            if searcher_results:
                results.extend(searcher_results)
                self.candidates.extend(searcher_results)
            else:
                self._active_searchers.remove(searcher)
        if results:
            return results
        else:
            return None

    def search(self):
        while True:
            results = self.next()
            if results:
                continue
            else:
                logger.debug("MultiSearcher done")
                break
        return self.candidates



class SearchRunner(object):
    """
    Wrapper that does all work needed for running searches.
    """
    def __init__(self, **kwargs):
        """
        Instantiate.

        Keyword arguments:
        * `search_id`: Required!
        * All others same as `MultiSearcher`.
        """
        self._search_id = kwargs.get('search_id')
        self._search = model.Search.get(self._search_id)
        self._max_results = kwargs.get('max_results', None)
        self._delete_existing = kwargs.get('delete_existing', False)
        searcher_kwargs = dict(
            search_id = self._search_id,
            max_results = self._max_results
        )
        self._searcher = MultiSearcher(**searcher_kwargs)
    def __iter__(self):
        """
        Return URLS records found by the search.
        """
        # Delete existing results
        if self._delete_existing:
            model.Contsearch.deleteBy(search = self._search_id)
            model.Content.deleteBy(searchid = self._search_id, deleteme = self._delete_existing)
            model.URLS.deleteBy(search_id=self._search_id, deleteme = self._delete_existing)

        # Perform search
        candidates = self._searcher.search()
        myBotRoutines.addUrlsFromDeque(self._search_id, self._delete_existing, candidates)

        # Cleanup results
        # TODO prevent searchers from creating unwanted URLs in the first place
        botUtilities.deDupUrls(self._search_id)
        botUtilities.fixUrls(self._search.targetword, self._search_id)

        # Return results
        # TODO why are we storing URLS objects? does anything use them?
        urls_records = model.URLS.selectBy(search_id = self._search_id)
        if self._max_results:
            urls_records = urls_records[:self._max_results]
        for urls_record in urls_records:
            yield urls_record
    def search(self):
        """
        Return list of URLS records found by the search.
        """
        return list(self)



class Search(object):
    #this class searches specifically Google, returning code fragments.
    def __init__(self, term, max_results=14):
        #this is executed when the class is called.  It doesn't work as expected
        #  because Google apparently limits results to pages, 7 results each.

        #it's called by invoking an instance of this class, passing in a search term e.g.,
        #myreturn = instanceOfSearch("searchTerm")

        self.term = term
        self.max_results = max_results
        self.candidates = deque()
        sstr = urllib.urlencode([('q', self.term),('start', '')])
        self._url = (
            'http://ajax.googleapis.com/' +
            'ajax/services/search/web?v=1.0&' +
            urllib.urlencode([('q', self.term),
                              ('start', '')]))
        a=0

    def iterateMe(self):
        self.__iter__()

    def _fill(self, start):
        """Fill the queue with fresh search results."""
        #results is a dict of responseData, responseDetails, responseStatus
        #responseData is a dict of cursor, results
        #      results (key of response data) is a list of search returns...
        #         each of which is a dict consisting of:
        #          GsearchResultClass, visibleUrl, titleNoFormatting, title, url, cacheUrl
        #          unescapedUrl, content
        #          ...the unescapedURL is what we want

        url = self._url + str(start)
        results = simplejson.loads(openanything.fetch(url)['data'])
        if results['responseStatus'] != 200:
            raise Exception('Google Error: %s' % results['responseStatus'])
        try:
            data = results['responseData']
            if not data['results']:
                return
            for r in data['results']:
                self.candidates.append(
                    (r['unescapedUrl'], r['titleNoFormatting'], r['content']))
            return len(data['results'])
        except KeyError, ex:
            raise Exception('Google Error: unexpected response (%r)' % ex)

    def filter(self, url, title, excerpt):
        return True

    def __iter__(self):
        i, max = 0, self.max_results
        while i < max:
            if not self.candidates:
                if not self._fill(i):
                    return
            candidate = self.candidates.popleft()
            if self.filter(*candidate):
                i += 1
                yield self.candidates.popleft()

    def __repr__(self):
        return 'buzzbot.search.Search(%r)' % self.term

def _make_re(text):
    word_bounded = re.split(r"\b%s\b", text) # for word in text.split()
    return re.compile('(%s)' % '|'.join(word_bounded))
    #return "dogma" #re.compile('(%s)' % '|'.join(word_bounded))

class BuzzSearch(Search):
    BAD_URL_GENERAL = _make_re(
        'blog wiki amazon tinyurl photo music yootube '
        'napster podshow games mevio vidio pod')

    BAD_URL_SPAM = _make_re(
        'robloger ihelpyoublog archive blogtoolscollection')

    BAD_URL_OLD = _make_re('2004 2005 2006 2007')

    def filter(self, url, title, excerpt):
        #this filter is pretty clever, but misapplied to the URLs;
        #  we'll keep it around to crib later

        #url = url.lower()
        #if self.BAD_URL_GENERAL.search(url):
        #    return False
        #if self.BAD_URL_SPAM.search(url):
        #    return False
        #if self.BAD_URL_OLD.search(url):
        #    return False
        return True

class RunGeneralSearch(object):
    #this is intended to expand the repertoire of search results beyond what the google
    #  api will provide by going to other blog-oriented sites.  It works like this:
    #     compose the a search string to the site's specs
    #     for each page of results
    #        find the urls returned
    #        for each url
    #           screen for duplicates, then add to the database, flagging as a 'seed' url
    #           visit the site, grab content, check for duplicates, then add to database
    #we can enhance this later by recursing thru the urls, checking sites linked, etc.

    #it's called by invoking an instance of this class, passing in a search term e.g.,
        #myreturn = instanceOfRunGoogleSearch("searchNum", sitename)
    MAX_PAGES = 10

    def __init__(self, searchNum):
        if not DEBUG_ON:
            #grab the search specifics from the database
            searchobj = model.Search.get(searchNum)
            searchstr = searchobj.urlsearchfor
            elimstr = searchobj.urleliminate
            if not searchstr:
                urlFind = []
            else:
                urlFind = searchstr.split(',')
            if not searchobj.urleliminate:
                urlEliminate =  []
            else: urlEliminate = elimstr.split(',')
            if type(urlEliminate) ==str:
                urlEliminate = [urlEliminate]
            if type(urlFind)==str:
                urlFind = [urlFind]
        else: #debug search parameters
            searchstr = "gates, microsoft, apple"
            elimstr = "aardvark, zebra"
            urlFind = searchstr.split(',')
            urlEliminate = elimstr.split(',')

        #add a plus sign to signal these terms for elimination
        for i in range(0, len(urlFind)):
            urlFind[i]='+'+urlFind[i].strip()

        #add a plus-minus sign to signal these terms for elimination
        for i in range(0, len(urlEliminate)):
            urlEliminate[i]='+-'+urlEliminate[i].strip()

        #get all the permutations if there just a few search terms
        self._terms = []
        if len(urlFind) <= 1:  #this implies a single search term
            self._terms.append(urlFind  + urlEliminate)
        else:
            searchPermutations =   permutation(urlFind)
            for u in searchPermutations:
                self._terms.append(u  + urlEliminate)

        self.candidates = deque()

    def _createSearchUrls(self, sitename):
        #creates a bunch of search engine queries, one for each page of results and one for
        #  each permutation of search terms; these differ per the search engine's "dialect".
        #  This is used to find new urls (it won't visit existing urls).
        searchUrls = []
        #get the short site name (this is the second-from-last element of the site name)
        sitenameComponents = sitename.split('.')
        shortSitename = sitenameComponents[len(sitenameComponents)-2]
        #clean up the list of search terms
        if sitename == 'www.technorati.com':
            #sample query:  http://www.technorati.com/search/cubs%2BAND%2Bthe%2BAND%2Btornado?authority=a4&language=en&page=4
            for p in range(1, self.MAX_PAGES+1):  #for each page of results
                for termlist in self._terms:             #for each permutation of terms
                    termstr = []
                    for t in termlist:                      #clean and concantenate the search terms
                        t= t.replace('-','NOT')
                        t= t.replace(" ", "%20")
                        termstr.append(t)
                    searchstr = ''
                    for ts in termstr:
                        searchstr = searchstr + ts
                mystr =[]                            #build up the search string
                mystr.append("http://" + sitename + "/search/")
                mystr.append(searchstr)
                mystr.append("?authority=a4&language=en&page=" + str(p))
                thisUrl = ""
                for m in mystr:
                    thisUrl = thisUrl + m
                searchUrls.append(thisUrl)           #...and add it to our list



        #add other search engines here
        return searchUrls

    def _fill(self, searchid, sitename):
        """Pings search engine for new urls, then finds content."""
        #to avoid banging on the search engine too, we'll visit each site found before returning
        #grab the lpid and userid
        thislp = getLpidFromSearchID(searchid)
        userinfo = getUserID()
        thisuser = userinfo['id']
        #get the short site name (this is the second-from-last element of the site name)
        sitenameComponents = sitename.split('.')
        shortSitename = sitenameComponents[len(sitenameComponents)-2]
        sitelist = self._createSearchUrls(sitename)
        scoreContent = True
        deleteme = False
        socket.setdefaulttimeout(5)
        candidates = []
        searchDBobj = model.Search.get(searchid)
        targetword = searchDBobj.targetword
        
        
        #*************************
        for s in sitelist:
            trials = 0
            fetchOk = False
            try:
                #myRetObj = openanything.fetch(s)
                myRetObj = myBotRoutines.getContentWithFeedparser(s)
                fetchOk = True
            except:
                print "timed out fetching: " + s
                pass
            if fetchOk:
                #results = myRetObj['data']
                results = myRetObj['cont']
                if myRetObj['status'] == 200:
                    #rawurls = myBotRoutines.digUrlsOutOfPage(myRetObj) 
                    rawurls = myRetObj.links
                    #do a first-order screen to eliminate known bad urls, internal links and dups
                    for u in rawurls:
                        isgood = True
                        u=u.replace('"', '')
                        if u.find(shortSitename) >=0:
                            isgood = False  #screens for internal links
                            rejectedBecause = "internal link"
                        else:
                            urlscreen =  myBotRoutines.goodUrl(u)
                            if urlscreen.get('status') <> 'bad':
                                if model.URLS.selectBy(search_id =searchid, urltext = u).count() > 0:
                                    isgood = False
                                    rejectedBecause = "duplicate url"
                            else:
                                rejectedBecause = urlscreen.get('reason')
                                isgood=False
                        if not isgood:
                            print "rejected: " + rejectedBecause + " " + u
                            a=0
                        if isgood:
                            scheme, netloc, path, query, fragment = urlsplit(u)
                            now = datetime.datetime.now()
                            #add the url to the database and the return array
                            url = model.URLS(scheme = scheme, netloc=netloc, path=path, search_id = searchid,
                                                        query = query, fragment=fragment, urltext=u,
                                                        lpid = thislp, datefound=now, userid = thisuser)

                            #grab content from the url
                            myret = myBotRoutines.visitScoreStoreSingleURL(searchid, url, scoreContent, deleteme)               
                            
                            #if we have not added any content for this url, delete it
                            if myret == 'bad':
                                model.URLS.delete(url.id)
                            else:
                                candidates.append(u)

        return self.candidates


    def __iter__(self):

        if not self.candidates:
            if not self._fill():
                return
        candidate = self.candidates.popleft()
        yield self.candidates.popleft()

    def __repr__(self):
        return 'buzzbot.search.Search(%r)' % self._terms

class RunBackgroudSearch(object):
    def __init__(self, mysites):
        mylps = model.Listeningpost.select()
        #mysites = ['technorati']
        for lp in mylps:
            searchNum = lp.searchtorun
            for sitename in mysites:
                searchInstance = RunGeneralSearch(searchNum)
                myiter = searchInstance._fill(searchNum, sitename)  

if __name__ == '__main__':
    # TODO These samples are broken, are they needed?
    """
    #searchInstance = RunGoogleSearch("dogma")
    #myiter = searchInstance.__iter__()
    searchid = 64
    #searchInstance = RunGoogleSearch(searchid)
    searchInstance = RunGeneralSearch(searchNum, sitename)
    #this invokes the search routine
    myiter = searchInstance._fill()
    #this accesses the deque (double-ended queue object, pronounced "deck") and adds urls to the db
    if not DEBUG_ON:
        myBotRoutines.addUrlsFromDeque(searchid, searchInstance.candidates)
        #myBotRoutines.visitUrlsLiteVersion(searchid, scoreContent)
        myBotRoutines.visutUrlsFeedParser(searchid, searchInstance.candidates)
    """

    # Start environment
    import buzzbot.commands
    buzzbot.commands.boot()

    # Run searcher
    ### searcher_class = YahooSearcher
    ### searcher_class = GoogleSearcher
    ### searcher_class = TechnoratiSearcher
    searcher_class = MultiSearcher
    ### searcher_class = MultiSearcher
    searcher = searcher_class(include="linus pauling", exclude="buy, pharmacy", max_results=8)
    results = searcher.search()
    print "Results:"
    for result in results:
        print "* %s" % result
