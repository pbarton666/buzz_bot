#!/usr/bin/env python

from __future__ import with_statement

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

# Import third-party libraries
import turbogears

# Custom libraries
from buzzbot import *
# TODO why isn't the above import sufficient?!
from buzzbot import model
from buzzbot import searcher
from buzzbot import visitor

myBotRoutines = bot.BotRoutines()

# Logging
import logging
logger = logging.getLogger("buzzbot.crawler")
hdlr = logging.FileHandler('crawler.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def has_fork():
    """
    Does this OS have the `fork` system call?
    """
    return "fork" in os.__dict__



class CrawlerServerFunctions(object):
    """
    Set of functions exposed by the CrawlerServer to the CrawlerClient.
    """
    def enqueue(self, item):
        """
        Enqueue the item into the Crawler.
        """
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
        return server.crawler.ping()



class SecurityError(StandardError):
    pass



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
        return int(turbogears.config.get("crawler.socket_port", 8052))



class CrawlerServer(CrawlerBase):
    def __init__(self, items_completed=True, concurrency_library=None):
        """
        Instantiate a server that hosts a Crawler.
        """
        self.service = SimpleXMLRPCServer.SimpleXMLRPCServer(addr=(self.host(), self.port()), logRequests=False, allow_none=True)
        self.service.register_instance(CrawlerServerFunctions())
        self.keep_running = True
        self.crawler = Crawler(items_completed=items_completed, concurrency_library=concurrency_library)
    def start(self):
        """
        Start the server.
        """
        self.crawler.start()
        while self.keep_running:
            self.service.handle_request()
        self.stop()
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
    def __init__(self, proxy, timeout_seconds=15.0, pause_seconds=0.25):
        self.proxy = proxy
        self.timeout_seconds = timeout_seconds
        self.pause_seconds = pause_seconds
    def __getattr__(self, name):
        DEBUG = False
        if DEBUG: print "GA: %s" % name
        proxy = self.proxy
        def wrapper(*args):
            if DEBUG: print "WR: %s%s" % (name, args)
            deadline = time.time() + self.timeout_seconds
            while deadline > time.time():
                try:
                    return proxy.__getattr__(name)(*args)
                except socket.error, e:
                    if DEBUG: print "WA: retry"
                    logger.debug("Waiting for XML-RPC server to respond...")
                    time.sleep(self.pause_seconds)
            raise TimeoutError("Couldn't connect to XML-RPC server, no response after %0.2f seconds" % self.timeout_seconds)
        return wrapper



class CrawlerClient(CrawlerBase):
    """
    Client that connects to the CrawlerServer.
    """
    def __init__(self):
        """
        Instantiate a client.
        """
        self.raw_service = xmlrpclib.ServerProxy(uri="http://%s:%s" % (self.host(), self.port()), allow_none=True)
        self.service = ResilentXmlRpcServerProxy(proxy=self.raw_service)
    def enqueue(self, **item):
        """
        Enqueue an item for crawling. The `item` is a dict with the same
        parameters accepted by `Crawler.enqueue`.
        """
        # NOTE: The XML-RPC proxy can't accept a bare **kwargs, so pass them as a `dict`.
        return self.service.enqueue(item)
    def stop(self):
        """
        Stop the CrawlerServer.
        """
        return self.raw_service.stop()
    def evaluate(self, code):
        """
        Return the result of evaluating the code on the server.
        """
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
        self.service.prepare_results()
    def results_for(self, search_id):
        """
        Return list of scored results for the `search_id`.
        """
        return self.service.results_for(search_id)
    def ping(self):
        """
        Is the server responding?
        """
        try:
            return self.raw_service.ping()
        except:
            return False



class Crawler(object):
    """
    Crawler
    =======

    The Crawler is an all-in-one multi-process crawler that searches keywords
    to get URLs, visits these to get their content, and then scores these.

    Usage
    -----

    # Load libraries
    import crawler

    # Instantiate objects and start service
    crawler = .crawler.Crawler()
    crawler.start()

    # Run a job
    crawler.enqueue(search_id=1234)

    # Shutdown
    crawler.stop()

    # Print out the result
    while True:
        try:
            print crawler.items_completed.get_nowait()
        except:
            print "DONE!"
            break
    """

    STOP = 'STOP'
    """Sentinel token used to stop workers."""

    def __init__(self, items_completed=True, searchers_count=None, visitors_count=None, scorers_count=None, concurrency_library=None):
        """
        Initialize a new crawler.

        Keyword arguments:
        * items_completed: Store completed items? Defaults to True.
        * searchers_count: Number of searcher processes to run. Defaults to sensible value.
        * visitors_count: Number of visitors processes to run. Defaults to sensible value.
        * scorers_count: Number of scorers processes to run. Defaults to sensible value.
        """

        # TODO replace attributes with uniform dicts, e.g. self.count['searcher'], self.pool['searcher'], etc

        # Concurrency
        self._concurrency_library = concurrency_library
        ### self._concurrency_library = "threading" # Override for development
        if not self._concurrency_library:
            # If a library wasn't specified as a parameter, try to pick the one
            # specified in the configuration files, else default to the most
            # reasonable one for this operating system.
            self._concurrency_library = turbogears.config.get("crawler.concurrency_library", has_fork() and "processing" or "threading")
        exec "import %s" % self._concurrency_library
        self._concurrency_library_module = eval("%s" % self._concurrency_library)
        logger.info("Using the `%s` concurrency library" % self._concurrency_library)

        # Worker counts
        self.cpu_core_count   = cpu_core_counter.cpu_core_count()
        self.searchers_count  = searchers_count  or max(2, self.cpu_core_count)
        self.visitors_count   = visitors_count   or min(40, self.cpu_core_count * 15)
        self.scorers_count    = scorers_count    or self.cpu_core_count

        # Workers pools
        self.searchers  = []
        self.visitors   = []
        self.scorers    = []

        # Queues
        if self._concurrency_library == "processing":
            self.manager           = self._concurrency_library_module.Manager()
            self.lock              = self.manager.Lock()
            self.items_to_search   = self.manager.Queue()
            self.items_to_visit    = self.manager.Queue()
            self.items_to_score    = self.manager.Queue()
            self.items_to_finalize = self.manager.Queue()
            self.items_completed = None
            if items_completed:
                logger.info("server will save completed items")
                self.items_completed = self.manager.dict()
        elif self._concurrency_library == "threading":
            self.manager           = None
            self.lock              = self._concurrency_library_module.Lock()
            self.items_to_search   = Queue.Queue()
            self.items_to_visit    = Queue.Queue()
            self.items_to_score    = Queue.Queue()
            self.items_to_finalize = Queue.Queue()
            self.items_completed = None
            if items_completed:
                logger.info("server will save completed items")
                self.items_completed = dict()
        else:
            raise NotImplementedError("Unknown concurrency_library: %s" % self._concurrency_library)

        # Queue maps
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

    def __del__(self):
        try:
            self.stop()
        except Exception, e:
            print "Crawler: failed to stop: %s" % e
            #logger.debug("failed to stop: %s" % e)
            pass
        finally:
            #logger.debug("destroyed")
            pass

    def start(self, kind=None):
        """
        Start the crawler. It will begin processing any entries in the queues
        immediately.

        Keyword arguments:
        * kind: Start a kind of subprocess, e.g., "searcher". Default is to
          start all available kinds.
        """

        if kind:
            count   = self.__dict__['%ss_count' % kind]
            workers = self.__dict__['%ss' % kind]
            for i in range(count):
                worker = None
                if self._concurrency_library == "processing":
                    worker = self._concurrency_library_module.Process(target=self._processes_wrapper, args=[kind])
                elif self._concurrency_library == "threading":
                    worker = self._concurrency_library_module.Thread(target=self._processes_wrapper, args=[kind])
                else:
                    raise NotImplementedError("Unknown concurrency_library: %s" % self._concurrency_library)
                workers.append(worker)
                worker.start()
            logger.info("started %i %s processes" % (count, kind))
        else:
            self.start("searcher")
            self.start("visitor")
            self.start("scorer")

    def searcher_process(self, item, output=None):
        """
        Search a single item.
        """

        # TODO wrap in try/except

        for result in searcher.SearchRunner(
                delete_existing = item['delete_existing'],
                search_id       = item['search_id'],
                max_results     = item['max_results']):
            logger.debug("searcher_process found: %s" % result.urltext)
            subitem = dict(
                delete_existing = item['delete_existing'],
                search_id       = item['search_id'],
                max_results     = item['max_results'],
                url_id          = result.id
            )
            output.put(subitem)
        return None

    def visitor_process(self, item, output=None):
        """
        Visit a single item.
        """

        # TODO wrap in try/except

        search = model.Search.get(item['search_id'])
        url_record = model.URLS.get(item['url_id'])
        for content in visitor.Visitor(search, url_record):
            ## print content
            subitem = dict(
                delete_existing = item['delete_existing'],
                search_id       = item['search_id'],
                max_results     = item['max_results'],
                content_id      = content.id
            )
            output.put(subitem)
        return None

    def scorer_process(self, item, output=None):
        """
        Score a single item.
        """

        search_id       = item['search_id']
        content_id      = item['content_id']
        content         = model.Content.get(content_id)

        try:
            myBotRoutines.addScoreToContent(content)
        except Exception, e:
            logger.error(traceback.format_exc(e))

        return item

    def _processes_wrapper(self, kind):
        """
        Run a persistent group of worker processes that pop items from a queue
        and process them.

        Keyword arguments:
        * kind: Kind of subprocess to run, e.g., "searcher.
        """
        tagline = "%s %s:" % (kind, self._worker_name())
        target  = self.__getattribute__('%s_process' % kind)
        input   = self.queue[kind]['input']
        output  = self.queue[kind]['output']
        ## logger.debug("%s waiting" % tagline)
        try:
            testiter = iter(input.get, self.STOP)
            mynext = testiter.next()
            for item in iter(input.get, self.STOP):
                logger.info("%s processing Search#%s" % (tagline, item['search_id']))
                ### print "%s_process(%s)" % (kind, repr(item)) # TODO is there no better way?
                result = target(item=item, output=output)
                if result and output != None:
                    output.put(result)
        except KeyboardInterrupt, e:
            pass
        ## logger.debug("%s done" % tagline)

    def _worker_name(self):
        """
        Returns string name uniquely identifying this worker. Actual name will
        depend on the underlying concurrency library.
        """
        if self._concurrency_library == "processing":
            return self._concurrency_library_module.currentProcess().getName()
        elif self._concurrency_library == "threading":
            return self._concurrency_library_module.currentThread().getName()
        else:
            raise NotImplementedError("Unknown concurrency_library: %s" % self._concurrency_library)

    def stop(self, kind=None):
        """
        Stop crawler and its related processes.

        Keyword arguments:
        * kind: Stop only a particular kind of subprocess, e.g., "searcher".
          Default is to stop all available kinds.
        """

        if kind:
            count = self.__dict__['%ss_count' % kind]
            queue = self.queue[kind]['input']
            stopped = False

            for i in range(count):
                try:
                    queue.put(self.STOP)
                except Exception, e:
                    # Ignore if the queue is already stopped?
                    pass
            workers = self.__dict__['%ss' % kind]
            for worker in workers:
                try:
                    worker.join()
                except Exception, e:
                    # Ignore if worker is already dead?
                    pass
            while len(workers) != 0:
                workers.pop()
                stopped = True
            if stopped:
                try:
                    import logging
                    global logger
                    logger.info("stopped %i %s processes" % (count, kind))
                except:
                    # Logging and logger aren't available otherwise if stop() is called from destructor.
                    print ("Crawler: stopped %i %s processes" % (count, kind))
                pass
        else:
            self.stop("searcher")
            self.stop("visitor")
            self.stop("scorer")

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
        logger.info("enqueued into `%s`: %s" % (queue_name, item))
        queue.put(item)
    def prepare_results(self):
        while True:
            item = None
            try:
                item = self.items_to_finalize.get_nowait()
            except Queue.Empty:
                pass # Handle below
            if not item:
                ## logger.debug("results_for: no items")
                break
            leaf = None
            self.lock.acquire()
            if self.items_completed.has_key(item['search_id']):
                leaf = self.items_completed[item['search_id']]
            else:
                logger.debug("results_for: creating array for Search#%s" % item['search_id'])
                leaf = []

            logger.debug("results_for: appending Search#%s/Content#%s" % (item['search_id'], item['content_id']))
            leaf.append(item['content_id'])
            self.items_completed[item['search_id']] = leaf
            self.lock.release()
    def results_for(self, search_id):
        self.prepare_results()
        if self.items_completed.has_key(search_id):
            results = self.items_completed[search_id]
            del self.items_completed[search_id]
            logger.debug("results_for: returning results for Search#%s: %s" % (search_id, results))
            return results
        else:
            ## logger.debug("results_for: no results for Search#%s" % (search_id))
            return []
    def ping(self):
        """
        Is the server alive? Yes, always because this is a local object.
        """
        return True




class CrawlerRunner(object):
    _instance = None
    _instance_lock = threading.Lock()

    # TODO collapse container_location and concurrency_library to single value
    def __init__(self, concurrency_library=None, container_location=None, manager=True, **kwargs):
        ## print "%s.__init__" % self
        self._concurrency_library = self._get_concurrency_library(concurrency_library)
        self._container_location = self._get_container_location(container_location)
        self._manager = self._container_location == "local" or manager
        self._lock = threading.Lock()

        ### OVERRIDE FOR DEVELOPMENT
        #self._concurrency_library = "threading"
        #self._concurrency_library = "processing"
        #self._container_location = "local"
        #self._container_location = "remote"

        crawler_kwargs = dict(
            concurrency_library=self._concurrency_library
        )
        crawler_kwargs.update(kwargs)

        if self._container_location == "local":
            self.crawler = Crawler(**crawler_kwargs)
        elif self._container_location == "remote":
            self.crawler = CrawlerClient()
        else:
            raise NotImplementedError("Unknown container_location: %s" % self._container_location)
    def __del__(self):
        #print "%s.__del__" % self
        self._crawler = None
        self._lock = None
    def start(self):
        #print "%s.start" % self
        if self._manager:
            atexit.register(self.stop)
            if self._container_location == "remote":
                killing_crawler = False
                try:
                    pause_seconds = 0.5
                    while True:
                        self.crawler.stop() # Will throw exception when down to end loop
                        logger.info("CrawlerRunner.start: killing stale remote crawler...")
                        killing_crawler = True
                        time.sleep(pause_seconds)
                except Exception, e:
                    if killing_crawler:
                        logger.info("CrawlerRunner.start: killed stale remote crawler")
                    pass # Ignore because service may not be running already

                logger.info("CrawlerRunner.start: launching remote crawler")
                filename = re.sub("\.pyc$", ".py", __file__, 1)
                # TODO safely quote paths
                cmd = "'%s' --server --config '%s'" % (filename, commands.configuration)
                logger.info(cmd)
                os.system("%s &" % cmd)
            elif self._container_location == "local":
                logger.info("CrawlerRunner.start: launching local crawler")
                return self.crawler.start()
            else:
                raise NotImplementedError("Unknown container_location: %s" % self._container_location)
    def stop(self):
        #print "%s.stop" % self
        if self._manager:
            with self._lock:
                if self.crawler:
                    try:
                        return self.crawler.stop()
                    except Exception, e:
                        print "CrawlerRunner.stop failed: %s" % e
    def enqueue(self, **item):
        return self.crawler.enqueue(**item)
    def results_for(self, search_id):
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



class TimeoutError(StandardError):
    """
    Raised when a timeout is reached.
    """
    pass



if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--config", dest="configfile", help="Optional configuration file", metavar="FILE")
    parser.add_option("-c", "--client", action="store_true", dest="client", help="Start client")
    parser.add_option("-s", "--server", action="store_true", dest="server", help="Start server")
    parser.add_option("-k", "--concurrency", dest="concurrency_library", help="threading OR processing", metavar="LIBRARY")
    (options, args) = parser.parse_args()

    if options.configfile:
        commands.boot(options.configfile)
    else:
        commands.boot()

    if options.client:
        logger.info("Starting client...")
        client = CrawlerClient()
        try:
            from ipdb import set_trace
        except:
            from pdb import set_trace
        set_trace()
        # TODO figure out how to make session exit without exceptions
    else:
        logger.info("Starting server...")
        global server
        server = CrawlerServer(concurrency_library=options.concurrency_library)
        try:
            server.start()
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            server.stop()
        logger.info("Stopped server")
