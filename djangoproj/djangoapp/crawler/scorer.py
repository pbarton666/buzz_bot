''''
This module does scoring of the contents of the Contents table, storing the results in the Scores table.
To support reseasrch on strengths and weaknesses of different approaches, the design allows several 
scoring algorithms to be stored in the ScoreMethods table and separately applied.  The Scores table holds
an index to the Content table, and index to the ScoreMethods table and the score itself.

The scoring algorithms need to use the same variable names used in this module.  Also, since we're using
Python's built-in eval() function, the operators need to be supported by eval() unless we build a custom
parser.

'''
import logging
from optparse import OptionParser
#third party modules
import sys
import random
import string
import re

#custom modules
#this is the sqlObject flavor of database routines.
import b_dbRoutines as dbRoutines

#instansiate imported classes
dbUtils = dbRoutines.DatabaseMethods()

regexNoPunctuation = re.compile('[%s]' % re.escape(string.punctuation))

class Counter():
    '''
	counts words in content blocks, storing the counts in the WordCount table
	'''
    def __init__(self):
        #do a one-time creation of dicts for the word lists; this way we need hit the database
        #  only once, and it should be faster
        self.posWords = dbUtils.generateWordListFrom('pos') 
        self.negWords = dbUtils.generateWordListFrom('neg')
        self.obsceneWords = dbUtils.generateWordListFrom('obs')
        pass
    

    def doAllWordCounts(self, contentObj, forceRecount = False):
        '''Counts words in a content object that are found in a various database tables.  
            -assumes content is an iterable object w/ ".id" and ".content" properties			
            -skips the operation if word counts exist (unless forceRecount = True)
        '''
        count = 0
        #this forces contObj to be iterable, even if it's a single entity
        try: 
            test= contentObj[0]
        except: 
            contentObj = [contentObj]    
        for contentRow in contentObj:
            contid = contentRow.id
            cont = contentRow.content
            if cont:
                #do we want to do a (re)count?  Yes if we have no entry in WordCount or we have forced a recount
                if not dbUtils.haveWordCountForContent(contid) or forceRecount:
                    #strip the punctuation, convert to lower case, and split the content into individual words
                    #allWords = cont.translate(string.maketrans("",""), string.punctuation).lower().split()                
                    allWords =  regexNoPunctuation.sub('', cont).lower().split()
                    posWords = self.countWords(allWords, self.posWords)
                    negWords = self.countWords(allWords, self.negWords)
                    obsWords = self.countWords(allWords, self.obsceneWords)
                    #update the table
                    retcode = dbUtils.updateWordCount(contid, posWords, negWords, obsWords)
	
    
    def countWords(self, content, wordList):
        #counts words in content that are found in wordList
        count = 0
        for c in content:
            if c in wordList:
                count += 1
        return count    
    
    def _set_logger(self):
        #Our friend the logger. Sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
        #  at the top of this module).
        LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
        log_filename = LOGDIR + '/' + LOG_NAME
        logging.basicConfig(level=LOG_LEVEL,
                            format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_filename,
                            filemode='w')	

class Scorer():
    '''this routine scores all content for which we have a word count, using all the scoring
       algorithms stored in the ScoreMethods table
    '''
    
    def __init__(self):
        pass
    
    def scoreAllContentAllMethods(self, overwrite=None):
        #score all content in the data base by all methods
        if not overwrite:  overwrite=False
        contentObj = dbUtils.getAllConten()
        for c in contentObj:
            self.scoreAllContentAllMethods(c.id)
    
    def scoreContentAllMethods(self, contentid, overwrite=None):
        if not overwrite:  overwrite=False
        methods = dbUtils.getScoreMethods()
        for m in methods:
            self.scoreContentOneMethod(contentid, m.id, overwrite=overwrite)

    
    def scoreContentOneMethod(self, contentid, methodid, overwrite=None):
        if not overwrite:  overwrite=False
        wordCountObj =dbUtils.getWordCountFor(contentid = contentid)
        if wordCountObj.count() > 0:
            pos = wordCountObj[0].pos or 0
            neg = wordCountObj[0].neg or 0
            obscene = wordCountObj[0].obscene or 0
            scoreMethodObj = dbUtils.getScoreMethodFor(methodid)
            try:
                equation = scoreMethodObj[0].equation
                score = eval(equation)
            except:
                logging.info("Eval failed for : %s" %equation)
                raise    
            try:
                dbUtils.setScoreForContentMethod(score = score, contentid = contentid, methodid = methodid, overwrite = overwrite)
                
            except:
                logging.info("Could not set/update score for failed for : %i" %contentid)
                raise                  
                    

    def _set_logger(self):
        #Our friend the logger. Sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
        #  at the top of this module).
        LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
        log_filename = LOGDIR + '/' + LOG_NAME
        logging.basicConfig(level=LOG_LEVEL,
                            format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_filename,
                            filemode='w')	

class CountAndScore():
    #wrapper class to do word counts and scorint
    def __init__(self):
        self.counter = Counter()
        self.scorer = Scorer()
    def countAndScoreAll(self, overwrite = None):
        if not overwrite: overwrite = False
        cont = dbUtils.getContent()
        for c in cont:
            self.counter.doAllWordCounts(c)
            self.scorer.scoreContentAllMethods(c.id, overwrite=overwrite)

class RunTests():
    def runTests(self):
        counter = Counter()
        scorer = Scorer()
        #test a bit of content with countWords (used in doAllWordCounts)
        cont = unicode('''good SAd? airhead, TeRrible''')
        #note: translate doesn't work w/ uncode
        allWords = regexNoPunctuation.sub('', cont).lower().split()
        posWords = counter.countWords(allWords, counter.posWords)
        negWords = counter.countWords(allWords, counter.negWords)
        obsceneWords = counter.countWords(allWords, counter.obsceneWords)
        assert posWords == 1
        assert negWords ==2
        assert obsceneWords ==1
        #test the logic against a real content object
        cont = dbUtils.getContent()
        counter.doAllWordCounts(cont[0], forceRecount = False)
        counter.doAllWordCounts(cont[0], forceRecount = True)
        counter.doAllWordCounts(cont[0])
        #test against a block of content
        bitOfCont = cont[0:10]
        counter.doAllWordCounts(bitOfCont[0])
        counter.doAllWordCounts(bitOfCont)
        for b in bitOfCont:       
            scorer.scoreContentOneMethod(b.id, 1, overwrite=True)
            scorer.scoreContentAllMethods(b.id, overwrite=False)
        a=1

if __name__=='__main__':
    run = RunTests()
    run.runTests()
    

    







