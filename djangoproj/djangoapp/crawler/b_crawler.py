#!/usr/bin/env python

from __future__ import with_statement
import logging    

# Library path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Standard libraries
import atexit
import random
import re
import socket
import threading
import time
import traceback
import weakref
import xmlrpclib
import Queue
import SimpleXMLRPCServer
#import multiprocessing

# Import third-party libraries
import turbogears

# Custom libraries

#import buzzbot.searcher
#import buzzbot.visitor
#import buzzbot.model
#import buzzbot.bot
#import buzzbot.botUtilities
import buzzbot
try:
    from buzzbot import *
    print "importing all buzzbot modules"
except:
    from buzzbot import cpu_core_counter
    from buzzbot import searcher
    from buzzbot import visitor
    from buzzbot import model
    from buzzbot import bot
    from buzzbot import botUtilities
    from buzzbot import commands
    myBotRoutines = bot.BotRoutines()
    myBotUtilities = botUtilities.Utilities()
    print "importing some buzzbot modules"
try:
    myBotRoutines = buzzbot.bot.BotRoutines()
    myBotUtilities = buzzbot.botUtilities.Utilities()

except:
    pass

#I haven't quite grokked the differences in namespaces between the dev and production box
#  this insures the visitor module is available
try:
    import bot
    import botUtilities
    import visitor
    myBotRoutines = bot.BotRoutines()
    myBotUtilities = botUtilities.Utilities()
except:
    pass



DEBUG_RUN_SERIALLY = False

import logging

class CrawlerBase(object):
    """
    Methods provided to CrawlerClient and CrawlerServer.
    """
    def host(self):
        """
        Return the connection host.
        """
        return turbogears.config.get("crawler.socket_host", "localhost")
    
    def port(self):
        """
        Return the connection port.
        """
        return int(turbogears.config.get("crawler.socket_port", 50015))

    def logger(self):
	import logging
	name = 'crawler'
	fname = '/var/log/buzz/crawler.log'
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO) 	
	handler = logging.handlers.RotatingFileHandler(
		      fname, maxBytes=100000, backupCount=5)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	logger.addHandler(handler)  
        return logger    
    
cb = CrawlerBase()
logger = cb.logger()
    
def has_fork():
    """
    Does this OS have the `fork` system call?
    """
    return "fork" in os.__dict__

class CrawlerServerFunctions(object):
    """
    Set of functions exposed by the CrawlerServer to the CrawlerClient.
    In English:  the crawler server is a simple xmlrpc server.  We have a proxy server
    attached to the smlrpc server that we're passing these methods to.  Things are a little strange
    because not everything can get passed between the proxy and the real server.  For instance,
    you can easily pass xml or html, but not objects (they could be repr-ed or pickled, of course)
    
    So, for instance, we can ask the proxy server to "enqueue" a request.  This involves passing
    the proxy server a dict holding the search_id and other stuff like a deletion flag.  The 
    proxy is supposed to relay that to the real server, which is supposed to process it.  The
    processing involves doing the search, visit, scoring processes/threads and reporting the results
    
    """
    def enqueue(self, item):
        """
        Enqueue the item into the Crawler.
        """
        #print "enqueue method of class CrawlerServerFunctions called"
        # NOTE: The XML-RPC proxy can't accept a bare **kwargs, so it's passed in as a `dict`.
        global server
        server.crawler.enqueue(**item)
    def stop(self):
        """
        Stop the Crawler.
        """
        global server
        server.keep_running = False
    def prepare_results(self):
        """
        Prepare scored results.
        """
        global server
        server.crawler.prepare_results()
    def results_for(self, search_id):
        """
        Return list of scored results for the `search_id`.
        """
        global server
        return server.crawler.results_for(search_id)
    
    def evaluate(self, code):
        """
        Return the result of eval'ing the string of `code`.
        """
        global server
        if self.allow_dangerous_operations():
            return eval(code)
        else:
            raise SecurityError("Dangerous operations not allowed on server")
        
    def execute(self, code):
        """
        Pass `code` to Python's `exec`.
        """
        global server
        if self.allow_dangerous_operations():
            exec code
        else:
            raise SecurityError("Dangerous operations not allowed on server")
        
    def allow_dangerous_operations(self):
        """
        Does this server allow dangerous operations? Returns true if the
        `DANGEROUS` environmental variable has a value.
        """
        global server
        if os.environ.has_key('DANGEROUS'):
            return True
        else:
            return False
    def ping(self):
        """
        Respond with true, to indicate server is alive.
        """
        print "pinging crawlerServiceFunctions.ping"
        return server.crawler.ping()
    
    def dogma(self):
        return "hello from crawlerServiceFunctions.dogma"
    
    def dogmaFromServer(self):
        return server.crawler.dogma()
    
class proxyServerError(StandardError):
    pass


class SecurityError(StandardError):
    pass
class WrapperError(StandardError):
    pass



        


class CrawlerServer(CrawlerBase):
    def __init__(self, items_completed=True, concurrency_library=None, run_as_cron = False):
        """
        Instantiate a server that hosts a Crawler.
        """

        
        #added option to change the xmlrpc port if the crawler is running as an independent
        #  process, as in the case of a nightly cron job
        
        logger.debug( "crawler.CrawlerServer.__init__ xmlrpc server initiated on  %s:%s"  % (str(self.host()), str(self.port())  ))   

        self.service = SimpleXMLRPCServer.SimpleXMLRPCServer(addr=(self.host(), self.port()), logRequests=False, allow_none=True)
        self.service.register_instance(CrawlerServerFunctions())
        #keep_running = True turns it on; keep_running = False shuts it down)
        self.keep_running = True
        #this instansiates a crawler process manager and its processes
        logger.debug("crawler.CrawlerServer.__init__ instansiating a crawler process server")
        self.crawler = Crawler(items_completed=items_completed, concurrency_library=concurrency_library)
        logger.debug("crawler.CrawlerServer.__init__ Success in instansiating a crawler process server")
        
    def start(self):
        """
        Start the server.
        """
        logger.debug( "starting the crawler process server")
        self.crawler.start()
        while self.keep_running:
            self.service.handle_request()
        self.stop()
        logger.debug("crawler_runner (crawler/proxy thread) stopped")
    def stop(self):
        """
        Stop the server.
        """
        self.keep_running = False
        self.crawler.stop()

class ResilentXmlRpcServerProxy(object):
    """
    Provides a wrapper around the XmlRpc proxy that retries the connection.
    """
    def __init__(self, proxy, timeout_seconds=5.0, pause_seconds=0.25):

        #logger.debug("ResilentXmlRpcServerProxy __init--")
        self.proxy = proxy
        #logger.debug("proxy is of type %s" % type (proxy))
        self.timeout_seconds = timeout_seconds
        self.pause_seconds = pause_seconds
        
    def __getattr__(self, name):

        DEBUG = False
        if DEBUG: print "GA: %s" % name
        proxy = self.proxy
        def wrapper(*args):
            init_time = time.time()
            deadline = init_time + self.timeout_seconds
            while deadline > time.time():
                try:
                    #logger.debug("returning function %s from the xmlrpc proxy wrapper with args: %s" %( name, repr(args) ))
                    return proxy.__getattr__(name)(*args)
                except Exception, e:
                    if DEBUG: print "WA: retry"
                    logger.error("xmlrpc server returned error: %s" %e)
                    time.sleep(self.pause_seconds)
                #if this process is too slow, give it a bit more priority (nice is the priority -20 = highest +20 = lowest   )
                #if time.time() > init_time + 3:
                    ##TODO:  fix this niceness thing ;it's a good idea, but too quickly sets *something* to -20 which freezes the system
                    #try:
                        #nice = os.nice(0)
                        #os.nice(nice-1)
                        #newnice = os.nice(0)
                        #print "changed nice from %i to %i" %(nice, newnice)
                    #except:
                    #    pass
                    
            logger.info("gave up trying to connect to the XML-RPC server")     
            raise TimeoutError("Couldn't connect to XML-RPC server, no response after %s seconds" % str(self.timeout_seconds))
        
        
        return wrapper



class CrawlerClient(CrawlerBase):
    """
    Client that connects to the CrawlerServer.
    """
    def __init__(self, run_as_cron = False):
        """
        Instantiate a client.
        """
        #note, don't use a logger in __init__ unless its installed in __init__
        
        self.raw_service = xmlrpclib.ServerProxy(uri="http://%s:%s/" % (self.host(), self.port()), allow_none=True)
        self.service = ResilentXmlRpcServerProxy(proxy=self.raw_service)
        
    def enqueue(self, **item):
        """
        Enqueue an item for crawling. The `item` is a dict with the same
        parameters accepted by `Crawler.enqueue`.
        """
        str(item['search_id'])
        logger.debug( "crawler client method enqueue called for item: %s" % str(item['search_id']) )
        # NOTE: The XML-RPC proxy can't accept a bare **kwargs, so pass them as a `dict`.
        testme = self.service.enqueue(item)
        return self.service.enqueue(item)
    def stop(self):
        """
        Stop the CrawlerServer.
        """
        print "stopping the xmlrpc server proxy"
        try:
            self.raw_service.stop()
        except:    
            pass
        return self.raw_service.stop()
    def dogma(self):
        #print "hello from CrawlerClient.dogma"
        pass
    
    def evaluate(self, code):
        """
        Return the result of evaluating the code on the server.
        """
        #print "evaluating " + code
        return self.service.evaluate(code)
    def execute(self, code):
        """
        Pass `code` to Python's `exec`.
        """
        self.service.execute(code)
    def prepare_results(self):
        """
        Prepare scored results.
        """
        #logger.debug( "initiating CrawlerClient prepare results process")
        self.service.prepare_results()
    def results_for(self, search_id):
        """
        Return list of scored results for the `search_id`.
        """
        #logger.debug( "initiating CrawlerClient results for search id %s" %str(search_id))
        return self.service.results_for(search_id)
    
    def ping(self):
        """
        Is the server responding?
        """
        try:
            print "pinging crawler client"
            return self.raw_service.ping()
        except:
            return False



class Crawler(object):
    
    '''sentinal to flag workers to stop'''
    STOP = 'STOP'
    def __init__(self, items_completed=True, searchers_count=None, visitors_count=None, 
        scorers_count=None, concurrency_library=None):       
        self.debug = False
        self.debug_run_serially = DEBUG_RUN_SERIALLY
	cb = CrawlerBase()
	self.logger = cb.logger()
	
        #get the concurrency library
        ##TODO: set this in the turbogears.config files
        self._concurrency_library = concurrency_library
        #import the library
        exec "import %s" % self._concurrency_library
        #this returns the *object* representing the concurrency library
        self._concurrency_library_module = eval("%s" % self._concurrency_library)
        #figure out how many CPUs we have to work with
        try: 
            self.cpu_core_count  = self._concurrency_library_module.cpu_count()  #works with multiprocessing
        except: 
            try:    self.cpu_core_count = cpu_core_counter.cpu_core_count() # works with threading and pyprocessing
            except: self.cpu_core_count  = 1    

        
        '''
        the manager herds the cats (processes), providing locks, semaphores and the such;
        it runs on its own process
        '''
        self.manager           = self._concurrency_library_module.Manager()
        self.lock              = self.manager.Lock()
        '''
        These objects are queues to be managed within - you guessed it - the manager; it runs on its own process.
        If we ever switch to a theading library, these would just be Queue.Queue() objects.
        '''
        self.items_to_search =  self.manager.Queue()
        self.items_to_visit=  self.manager.Queue()
        self.items_to_score=  self.manager.Queue()
        self.items_to_finalize=  self.manager.Queue()
        self.items_completed = None
        if items_completed:
            self.items_completed = self.manager.dict()
        
        '''
        the following is a bit convoluted but produces a dict (queue) with three items (searcher, visitor, scorer);
        Each of these three items is in itself a dict with the same two items (input, output).
        searcher =  queue.get('searcher') evaluates to: { input : AutoProxy[Queue], output : AutoProxy[Queue]
        myinput = searcher.get('input')   evaluates to:  AutoProxy[Queue] object
        '''      
        self.queue = {}
        self.queue['searcher'] = {}
        self.queue['searcher']['input']   = self.items_to_search
        self.queue['searcher']['output']  = self.items_to_visit
        self.queue['visitor'] = {}
        self.queue['visitor']['input']    = self.items_to_visit
        self.queue['visitor']['output']   = self.items_to_score
        self.queue['scorer'] = {}
        self.queue['scorer']['input']     = self.items_to_score
        self.queue['scorer']['output']    = self.items_to_finalize

        '''
        Figure out how many processes to spawn as a function of the CPUs available; the optimal number
        is at least partly a function of the real time performance desired - a smaller number provides
        faster response
        '''
        # Worker counts
        self.searchers_count  = searchers_count  or max(2, self.cpu_core_count) 
        #TODO:  experiment with the visitor counts
        self.visitors_count   = visitors_count   or min(5, self.cpu_core_count * 5) 
        self.scorers_count    = scorers_count    or min(2, self.cpu_core_count)
         
        # Workers pools
        self.searchers  = []
        self.visitors   = []
        self.scorers    = []   
            

    def __del__(self):
        #this is the destructor method called after object is killed, so we need to re-import logger

        try:
            print ("trying to stop crawler process manager")
            self.stop()
        except Exception, e:
            print ("crawler.Crawler failed to stop normally: %s" % e)
            pass
        finally:
            #logger.debug("destroyed")
            pass        
        
    def start(self, kind=None):
        """
        Start the crawler. It will begin processing any entries in the queues
        immediately.  This starts all types of processes, unless we ask it only to
        run one (kind = "searcher", say)
        """
       
        #this logic is to run the program serially for debugging purposes (independent
        #  processes are hideous to work with).
        if not DEBUG_RUN_SERIALLY:        
        
            if kind:
                logger.info ("crawler start method called for kind = "  + kind)
                ''' 
                the following statements use strange pythonic syntax to dig evaluate variables; compact
                but arcane.  
                   self__dict__ is a dict of object:value pair known to self (i.e., this class)
                   the term ['%ss' % kind] uses text formatting strings:  %s  is replaced with the value for kind
                   self.__dict__['%ss' % kind], then pulls the value for "kind" from the dictionary
                   ...
                   so, say "kind" is searcher
                   so, count = searcher_count  and workers = searcher
                   ...
                   this makes it work with any type of process.  but *who cares*?
                '''
                
                count   = self.__dict__['%ss_count' % kind]  #this is dict of all objects known to self
                workers = self.__dict__['%ss' % kind]
                for i in range(count):
                    worker = None
                    '''
                    Here, the "target" i.e., the thing executed by the process; this will be a search process, a
                    visitor processs, or whatever TBD by the process_wrapper routine.  The list of "workers" gets
                    the process appended to it.  The last step is to actually run the process(using the start method).
                    '''
                    if self._concurrency_library == "processing":
                        worker = self._concurrency_library_module.Process(target=self._processes_wrapper, args=[kind])
                    elif self._concurrency_library == "threading":
                        worker = self._concurrency_library_module.Thread(target=self._processes_wrapper, args=[kind])
                    elif self._concurrency_library == "multiprocessing":
                        worker = self._concurrency_library_module.Process(target=self._processes_wrapper, args=[kind])                    
                    else:
                        raise NotImplementedError("Unknown concurrency_library: %s" % self._concurrency_library)
                    workers.append(worker)
                    logger.info("starting %s process" % (kind))
                    worker.start()
                    logger.info("started as %s " % (worker.name))
                    a=1
                    a=2
            else:
                '''
                Recursively calls the logic above to initaite "worker processes" for the requested number of
                searchers, visitors, and scorers (invoked when no worker type is specified in the call).
                '''
                logger.info( "starting processes for all - searcher, visitor, and scorer")
                self.start("searcher")
                self.start("visitor")
                self.start("scorer")  
        else:
            logger.debug("running serially for debugging")
            
    def dogma(self):
        return "hello from Crawler.dogma"
    
    def testQueues(self):
        #having an issue with being able to add items to the queues
        pass

    def _processes_wrapper(self, kind):  #line 449
        """
        This routine serves as a container for the worker (searcher, visitor, scorer) processes.  The idea is
        that the calling routine can iterate over all processes using the same logic, because the statement
        in the calling routine can be agnostic as to exactly which proces it's calling.
        
        The calling routine has loaded up a set of queues, one each for the searchers, visitors, and scorers.  These
        queues are stored in a dict structure called queue.  The "queue" dict has three objects, each of which is another
        dict:  searcher, visitor, and scorer.  Each of these secondary objects has two entries: input and output (both Queues).
        
        The logic uses the input argument "kind" to find the correct input/output queue combination, and also to figure
        out which processing routine to pass control to.  For instance, if the "kind" argument is "searcher", it digs out
        the searcher input and output queues from the "queue" dict object.  Then, using the self._worker_name routine,
        discovers that it needs to pass control to the self._searcher_process method embedded in a Process object.  Then, by
        invoking the "target" method, it launches the process, passing along the specifications for this particular search
        and the right output queue (in this case "scorer" input queue dug out of the "queue" dict mentioned above)

        """

        #discern the name of the process to be invoked from the "kind" input argument
        tagline = "%s %s:" % (kind, self._worker_name())
        #creat an alias for the actual Process object
        target  = self.__getattribute__('%s_process' % kind)
        #create aliases for the correct input/output Queue objects to be used
        input   = self.queue[kind]['input']
        output  = self.queue[kind]['output']
	
	logger.debug("process wrapper processing a %s queue; currently " %kind)
	logger.debug("input queue is %s long; output queue is %s long" %(str(input.qsize()), str(output.qsize())))
 
        #self.debug_run_serially is used for debugging only
	logger.info("self.debug_run_serially is set to : %s" %str(self.debug_run_serially) )
	
        if not self.debug_run_serially: 
	    #iterate over the input queue ...
	    for item in iter(input.get, self.STOP):
		logger.debug("input dict to %s is: %s" %(kind, repr(item)))
		stop_requested = False
		##TODO:  implement graceful stop for runaway bots using search.stop_requested
		
		try:		    
		    search_id = item.get('search_id')
		    search = model.Search.get(int(search_id))
		    stop_requested = search.stoprequested
		except:
		    logger.error("process_wrapper failed to get search_id for handoff to %s" %kind)
		    logger.error(traceback.print_stack())
		
		if not stop_requested:               
		    #result = None
		    logger.info("launching process: %s" %kind)
		    result = target(item=item, output=output)
		    
		    if result:
			logger.debug("process %s found a result" %kind)
		    else:
			logger.debug("process %s result is None" %kind)
		    if not output:
			logger.debug("output is %s" %repr(output))
		    if result and output != None:
			output.put(result)
			if kind == 'scorer':
			    logger.info ("outputting %s to results_for" %result)
		    else:
			try:
			    logger.debug("couldn't place item in queue; this would clear queue")
			    #logger.debug(traceback.print_stack())
			    input.queue.clear()

			except:
			    pass                            
		else:
		    logger.debug("stop requested in processes_wrapper")


    def _worker_name(self):
        """
        Returns string name uniquely identifying this worker. Actual name will
        depend on the underlying concurrency library.
        """
        if self._concurrency_library == "processing":
            return self._concurrency_library_module.currentProcess().getName()
        elif self._concurrency_library == "threading":
            return self._concurrency_library_module.currentThread().getName()
        elif self._concurrency_library == "multiprocessing":
            return self._concurrency_library_module.current_process().name     
        else:
            raise NotImplementedError("Unknown concurrency_library: %s" % self._concurrency_library)

    def searcher_process(self, item, output=None):
        """
        This process is invoked by the _process_wrapper routine.  It runs the search engine queries via the 
        routine "searcher.SearcherRunner".  It's run as a self-contained process/thread.  It's important that
        any changes be thoroughly vetted because if it has problems, it will likely die silently.
        """
        #check to see if we're running serially for debugging
        if item.has_key('debug_run_serially'):  
            self.debug_run_serially=item.get('debug_run_serially')
            serial_return = []
            
        
        logger.info( "running searcher process for item %s"  % repr(item))
        #PB if user requested stop, don't bother 
        search = model.Search.get(item['search_id'])

        stop_requested = search.stoprequested
        #logger.debug("checked stoprequested")
        targetword = search.targetword
        #logger.debug("entering stoprequested loop")

        if not stop_requested:
            print "deploying searcher.SearchRunner"
            myresult = searcher.SearchRunner(
                #each "result" is a raw url returned from a search engine
                    delete_existing      = item['delete_existing'],
                    search_id            = item['search_id'],
                    max_results          = item['max_results'],
                    debug_run_serially   = self.debug_run_serially
                )
            logger.debug("myresult is  %s" % repr(myresult))
            
            
            for result in searcher.SearchRunner(
                #each "result" is a raw url returned from a search engine
                    delete_existing = item['delete_existing'],
                    search_id       = item['search_id'],
                    max_results     = item['max_results']):

		urlid = None

                logger.debug("searcher_process found: %s" % repr(result))
                
                ##TODO: move this processing logic outside the crawler
                #clean the url up (first-order validity checks, etc.) Below returns a list or nothing                  
                
                logger.debug("evaluating %s" %result)
                fixedUrl = myBotUtilities.fixUrls(targetword, urlList = [result])
                #logger.info("fixed url is %s" %fixedUrl)
		cleanResult = ""
                if len(fixedUrl)>0:   #cleanResult is null if the url failed our tests     
                    cleanResult= fixedUrl[0]
                    #logger.debug("checking if url %s is sponsor site %s" %(str(fixedUrl), str(targetword)))
                if myBotUtilities.isTargetWordSite(cleanResult, targetword): #sponsor site
                    cleanResult = ""
		    logger.debug("%s is from the sponsor site" % str(fixedUrl))
                if not myBotUtilities.goodUrl(cleanResult):  #known junk, videos, etc
                    cleanResult = ""   
		    logger.debug("%s is known junk" % str(fixedUrl))
		if len(cleanResult) > 0:

		#if we have this id for this search, we'll grab its id (content specs may have changed)
                    dupReturn =  myBotUtilities.isDupUrl(item['search_id'], cleanResult) #returns 0 or the ID of thedup                        
		    if dupReturn > 0:
			urlid = dupReturn
			logger.debug("we already have url %s" %str(fixedUrl))
		    else:
			try:
			    urlid = myBotUtilities.addUrl(item['search_id'], cleanResult)
			except:
			    logger.debug("tried but failed to have botUtilites add this url %s" %cleanResult)
		if urlid:	
		    logger.debug("attempting to output this url to visitor process queue: %s" %str(cleanResult))
		    subitem = dict(
				    delete_existing = item['delete_existing'],
				    search_id       = item['search_id'],
				    max_results     = item['max_results'],
				    url_id          = urlid,
				    parseFast       = item['parseFast'] or True
				   )
		    output.put(subitem)
		    logger.debug("visitor process queue fed searchid: %s and urlid: %s " %(str(item['search_id']), str(urlid)))
        
        if self.debug_run_serially:
            return serial_return


    def visitor_process(self, item, output=None):
        '''        
        This process is invoked by the _process_wrapper routine.  It runs the visitors (they read the web sites)
        engine queries via the 
        routine "visitor.Visitor".  It's run as a self-contained process/thread.  It's important that
        any changes be thoroughly vetted because if it has problems, it will likely die silently.
        logger.debug ("visitor process started")
        '''
	
	logger.debug("visitor_process invoked ... working on item: %s" %repr(item))
        return_dict = None; search = None
        
        #check to see if we're running serially for debugging
        if item.has_key('debug_run_serially'):  
            self.debug_run_serially=item.get('debug_run_serially')  
            serial_return=[]
        if item.has_key('parseFast'):
            parseFast = item.get('parseFast')
        else:
            parseFast = True
        logger.debug("trying to retrieve search " + str(item['search_id']))
	
        #make sure we can find the search in the database
        try:
            search = model.Search.get(item['search_id'])
            stop_requested = search.stoprequested
        except:
	    logger.error("crawler.visitor_process couldn't load search")
            pass
	
	if not search:
	    logger.error("visitor_process can't find a search")
        else: 
	    #we *do have a valid search
            logger.debug( "visitor process checking for URLs to visit")
	    visitorContent = None; url_record = None
	    try:
		url_record = model.URLS.get(item['url_id'])
	    except:
		pass
	    
            #visitor.Visitor returns a list object containing model.Content objects
	    logger.debug("pinging visitor.Visitor")
	    if url_record:
		visitorContent = visitor.Visitor(search, url_record,  parseFast)
	    
            if visitorContent:
		logger.debug("**enqueing a visitor.Visitor object")
		
                for content in visitorContent:
		    logger.debug("crawler.visitor_process viewing content: %s" %repr(content))
		    try:
			logger.info("we have content for search %s : content: %s" %(str(item['search_id']), str(content.id)))
			subitem = dict(
			    delete_existing = item['delete_existing'],
			    search_id       = item['search_id'],
			    max_results     = item['max_results'],
			    content_id      = content.id,
			    parseFast       = parseFast
			)
		    except:
			logger.warn("crawler.visitor_process couldn't parse the input dict")
			
		    #debug_run_serially is for debugging - allows serial processing
		    if self.debug_run_serially and subitem:
			serial_return.append(subitem)
		    #for production - passes this on to the scorer	
		    else:    			        
			try:
			    output.put(subitem)
			except:
			    logger.error("scorer not loaded for urlid %s, content %s" %(str(urlid), str(content.id)))
			return None

    
    def enqueue(self, search_id, max_results=8, delete_existing=False, queue_name="items_to_search", **kwargs):
        """
        Add a job to the crawler.

        Keyword arguments:
        * search_id: Crawl this search record.
        * max_results: Return approximately this many results. Default is to
          let the searcher decide how many to return.
        * delete_existing: Delete existing records for this search record?
          Defaults to False.
        * queue_name: Name of queue to use. Defaults to "items_to_search".
        """
        queue = self.__getattribute__(queue_name)
        item = kwargs
        item['search_id'] = search_id
        item['max_results'] = max_results
        item['delete_existing'] = delete_existing
        logger.debug("enqueued into `%s`: %s" % (queue_name, item))
        queue.put(item)

    def scorer_process(self, item, output=None):
        """
        Score a single item.
        """
       
        logger.info( "scorer process started")
	content = None; stop_requested = None; search = None
        try:
            search_id       = item['search_id']
            content_id      = item['content_id']
        except Exception, e:
            logger.error("bad item passed to crawler.scorer")
        
        try:
	    #these may be null or placeholder objects
            search = model.Search.get(item['search_id'])
	except:
	    logger.debug("scorer couldn't retrieve search")
	try:    
            content = model.Content.get(content_id)  #a search object (db record)
	except:
	    logger.info("scorer couldn't retrieve content")
	try:    
            stop_requested = search.stoprequested
	except:
	    logger.debug("scorer couldn't retrieve stop_requested")

	#TODO: implement the "stop_requested" feature to kill runaway bots

	if content:
	    try:
                myBotRoutines.addScoreToContent(content)
		logger.info("adding score to content %s" %content)
            except Exception, e:
            	logger.debug( "bot.addScoreToContent has a problem")
            	logger.error(traceback.format_exc(e))
		raise

        return item       
        
    def prepare_results(self):
        """
        load the scored results from the output of the scorer process (a Queue object
        called items_to_finalize) into a dict called items completed
        """
        while True:
            item = None
            try:
                item = self.items_to_finalize.get_nowait()
            except Queue.Empty:
                pass # Handle below
            if not item:
                #logger.debug("results_for: no items")
                break
            leaf = None
            self.lock.acquire()
            if self.items_completed.has_key(item['search_id']):
                leaf = self.items_completed[item['search_id']]
            else:
                #logger.debug("results_for: creating array for item:" % repr(item))
                leaf = []

            #logger.debug("results_for: appending Search#%s/Content#%s" % (item['search_id'], item['content_id']))
            try:
                leaf.append(item['content_id'])
                self.items_completed[item['search_id']] = leaf
                #logger.debug("leaf (items completed list) is %s" %repr(leaf))
            except: 
                pass
            self.lock.release()
            
    def results_for(self, search_id):
        """
        Calls the prepare_results method to unload the scorer output queue.  When 
        finished, it calls the destructor for items_completed
        """
        #logger.debug("results_for called")
        #logger.debug("prepare_results  search %s" %str(search_id))
        self.prepare_results()
        #logger.debug("prepare_results returned")
        #logger.debug("self.items_completed: %s" %repr(self.items_completed))
        if self.items_completed.has_key(search_id):
            results = self.items_completed[search_id]
            del self.items_completed[search_id]
            #logger.debug("results_for: returning results for Search#%s: %s" % (str(search_id), repr(results)))
            return results
        else:
            #logger.debug("results_for returned no results for Search#%s" % str(search_id))
            return []
        
    def ping(self):
        """
        Is the server alive? Yes, always because this is a local object.
        """
        return True

    def stop(self, kind=None):
        """
        This is a generic routine to stop processes.  If no "kind" argument is provided, it iterates over the 
        top block of logic for searcher, visitor and scorer process types.  The syntax is a bit convoluted here
        and noted in the comments
        """
        print ("crawler.Crawler.stop called")
	cb = CrawlerBase()
	logger = cb.logger()
        if kind:
            #this aliases the variable called <kind>s_count  e.g., count = searchers_count
            count = self.__dict__['%ss_count' % kind]
            #alias for the input queue associated with this process
            queue = self.queue[kind]['input']
            stopped = False
            
            #throws a "stop" sentinal into the queue
            for i in range(count):
                try:
		    logger.info("stopping queue %s" %kind)
		    #traceback()
                    queue.put(self.STOP)
                except Exception, e:
                    # Ignore if the queue is already stopped
                    pass
            """
            The next equation assigns an alias for the variable that represents the "kind" 
            of process we're going to stop.  If we passed in "scorer", the variable workers
            would be set to "scorers".
            """ 
            workers = self.__dict__['%ss' % kind]
            for worker in workers:
                try:
                    #tell it to stop accepting new work until done with what it's doing
                    worker.join()
                except Exception, e:
                    # Ignore if worker is already dead
                    pass
                
            #clear the stack of active workers    
            while len(workers) != 0:
		logger.debug("clearing worker stack in crawler.stop")
                workers.pop()
                stopped = True
            if stopped:
                try:
                    import logging
                    cb = CrawlerBase()
                    logger = cb.logger()
                    logger.info("stopped %i %s processes" % (count, kind))
                except:
                    # Logging and logger aren't available otherwise if stop() is called from destructor.
                    print ("Crawler: stopped %i %s processes" % (count, kind))
                pass
        else:
            """
            If this routine is called without a "kind" it recursively calls itself
            to stop each type of active process; this is sort of the main loop for the
            method.
            """
            self.stop("searcher")
            self.stop("visitor")
            self.stop("scorer") 

class CrawlerRunner(object):
    """
    This is the main entry point for the crawler module.
    
    """
    _instance = None
    _instance_lock = threading.Lock()
    
    #grab the logger from the server base


    # TODO collapse container_location and concurrency_library to single value
    def __init__(self, concurrency_library=None, container_location=None, manager=True, run_as_cron = False, **kwargs):
        #note, don't use a logger in __init__ unless its installed in __init__

        self._concurrency_library = self._get_concurrency_library(concurrency_library)
        self._container_location = self._get_container_location(container_location)
        self._manager = self._container_location == "local" or manager
        self._lock = threading.Lock()
        #run_as_cron will spawn a completely new instance of the crawler, hosted on a different
        #  xmlrpc server than the  mainline web app  

        crawler_kwargs = dict(
            concurrency_library=self._concurrency_library
        )
        crawler_kwargs.update(kwargs) 
        self.crawler_kwargs = crawler_kwargs
        
        
        if self._container_location == "local":
            crawler_kwargs.update(run_as_cron = run_as_cron)
            self.crawler = Crawler( run_as_cron = run_as_cron, **crawler_kwargs)
        elif self._container_location == "remote":
            self.crawler = CrawlerClient(run_as_cron = run_as_cron)
        else:
            raise NotImplementedError("Unknown container_location: %s" % self._container_location)

    def __del__(self):
        """
        The destructor method for a CrawlerRunner object
        """

        self._crawler = None
        self._lock = None

    def run_visitor_serially(self, **kwargs):
 
        self.run_serially = True
        self.crawler = Crawler( run_as_cron = run_as_cron, **self.crawler_kwargs)
        item = kwargs
        item.update(debug_run_serially = True)

        visitReturn = self.crawler.visitor_process(kwargs)
        
        if visitReturn:   
            aFewMore = 3
            for j in range(0, min(len(visitReturn), aFewMore-1)):
                v = visitReturn[j]
                v.update(debug_run_serially = True)
                scoreReturn = self.crawler.scorer_process(v)        
        
    def run_serially(self, **kwargs):
        '''
        this is or debugging, and is used the same as enqueue.  Instead of directing processing to
        the process queues, it runs them serially i.e. the searcher routine hands off to the visitor
        routine then the scorer routine.  It's much slower, but allows access to the running code.
        '''
        
        self.run_serially = True
        self.crawler = Crawler(**self.crawler_kwargs)
        item = kwargs
        item.update(debug_run_serially = True)
        searchReturn = self.crawler.searcher_process(item)  #a list
        if searchReturn:
            #try one to see if it works generally
            s =searchReturn[0]
            s.update(debug_run_serially = True)
            s.update(parseFast = kwargs['parseFast'])
            visitReturn = self.crawler.visitor_process(s)
            
            if len(visitReturn) >0 :
                #visitReturn.update(debug_run_serially = True)
                v=visitReturn[0]
                v.update(debug_run_serially = True)
                scoreReturn = self.crawler.scorer_process(v)
            #try a few more
            aFewMore = 10
            if searchReturn:
                for i in range(0, min(len(searchReturn), aFewMore-1)):
                    s=searchReturn[i]
                    s.update(debug_run_serially = True)
                    visitReturn = self.crawler.visitor_process(s)

                    if visitReturn:   
                        
                        for j in range(0, min(len(visitReturn), aFewMore-1)):
                            v = visitReturn[j]
                            v.update(debug_run_serially = True)
                            scoreReturn = self.crawler.scorer_process(v)
                        
        
    def start(self):

        print "%s.start" % self
        if self._manager:
            """
            The next line signs up this object for garbage collection if (and only if)
            the program terminates normally.  If it crashes, or is stopped during debugging
            there may be an orphaned process.  If so, to process may need to be killed manually;
            use sudo netstat - tap to look for network connections (host/port specifications
            are set in CrawlerBase).
            """
            
            atexit.register(self.stop)  #sets up to kill be object upon normal termination
            if self._container_location == "remote":
                pass
                '''
                *** We'll start the crawler server from a terminal window - at least for debugging;  when
                the main (client) program shuts down ungracefully, it doesn't kill the server.  This
                means we have to kill it manually.
                
                killing_crawler = False
                try:
                    pause_seconds = 0.5
                    #pat - why are we trying to kill the xmlrpc proxy server?
                    killCrawler= False
                    if killCrawler:
                        while True:
                            logger.debug("stopping crawler (this is normal)")
                            logger.debug("for debugging, don't stop the server")
                            #self.crawler.stop() # Will throw exception when down to end loop
                            #logger.info("CrawlerRunner.start: killing stale remote crawler...")
                            killing_crawler = True
                            time.sleep(pause_seconds)
                except Exception, e:
                    if killing_crawler:
                        print "killing crawler"
                        logger.info("CrawlerRunner.start: killed stale remote crawler")
                    pass # Ignore because service may not be running already

                logger.info("CrawlerRunner.start: launching remote xmlrpc server in os")
                filename = re.sub("\.pyc$", ".py", __file__, 1)
                # TODO safely quote paths
                cmd = "'%s' --server --config '%s'" % (filename, commands.configuration)
                logger.info(cmd)
                #logger.debug("not starting the server from crawler - relying on externally-started one")
                os.system("%s &" % cmd)
                '''
                
            elif self._container_location == "local":
                logger.info("CrawlerRunner.start: launching local crawler")
                return self.crawler.start()
            else:
                raise NotImplementedError("Unknown container_location: %s" % self._container_location)
    def stop(self):

        print "%s.stop" % self
        if self._manager:
            with self._lock:
                if self.crawler:
                    try:
                        return self.crawler.stop()
                    except Exception, e:
                        print "CrawlerRunner.stop failed: %s" % e
    def enqueue(self, **item):
        #logger.debug("CrawlerRunner enqueueing item %s into a %s object" %(repr(item), type(self.crawler)))
        return self.crawler.enqueue(**item)
    def results_for(self, search_id):
        #logger.debug("CrawlerRunner.results_for for search %s" % str(search_id))
        return self.crawler.results_for(search_id)
    def ping(self):
        return self.crawler.ping()
    @classmethod
    def _get_concurrency_library(self, kind=None):
        if kind:
            return kind
        else:
            return turbogears.config.get("crawler.concurrency_library", has_fork() and "processing" or "threading")
    @classmethod
    def _get_container_location(self, kind=None):
        if kind:
            return kind
        else:
            return turbogears.config.get("crawler.container_location", has_fork() and "remote" or "local")
    @classmethod
    def get_instance(self):

        with self._instance_lock:
            if not self._instance:
                self._instance = self()
                self._instance.start()
            return self._instance


class SearcherError(StandardError):
    pass
class TypeError(StandardError):
    pass
class TimeoutError(StandardError):
    """
    Raised when a timeout is reached.
    """
    pass

if __name__ == "__main__":

    import logging
    cb = CrawlerBase()
    logger = cb.logger()    
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--config", dest="configfile", help="Optional configuration file", metavar="FILE")
    parser.add_option("-c", "--client", action="store_true", dest="client", help="Start client")
    parser.add_option("-s", "--server", action="store_true", dest="server", help="Start server")
    #parser.add_option("-n", "--nightly", action="store_true", dest="run_as_cron", help="Run as cron")
    parser.add_option("-k", "--concurrency", dest="concurrency_library", help="threading OR processing OR multiprocessing", metavar="LIBRARY")
    (options, args) = parser.parse_args()

    #set up two possibilites for logging so contemporaneously-executing real-time
    #  and chron files won't step on each other.  Simultaneaty shouldn't be a problem with 
    #  the stuff running as processes because each is on its own thread
    
    cb = CrawlerBase()
    logger = cb.logger()   

    logger.debug("booting configfile")
    if options.configfile:
        commands.boot(options.configfile)
    else:
        logger.debug("booting commands")
        commands.boot()

    if options.client:
        logger.info("Starting client...")
        client = CrawlerClient(run_as_cron = run_as_cron)
        try:
            from ipdb import set_trace
        except:
            from pdb import set_trace
        #set_trace()
        # TODO figure out how to make session exit without exceptions
    else:
        logger.info("Starting server from crawler.__main__") 
        global server
        
        logger.debug("forcing concurrency library to be multiprocessing")
        server = CrawlerServer(concurrency_library='multiprocessing')
        #server = CrawlerServer(concurrency_library=options.concurrency_library)
        
        try:
            # pat - don't need to start the server here   server.start()
            server.start()
            pass
        except KeyboardInterrupt:
            logger.info("Shutting down crawler process server due to keyboard interrupt...")
            server.stop()
            logger.debug("crawler process server shut down succesfully")
            logger.info("Stopped server")
        

        
        