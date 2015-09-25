'''
This contains a few generally-useful classes for analyzing content for Jeff Hardy's movie blog
analysis project.  It's pretty one-off but can be repurposed for other work.

SysUtils has routines to a) build fully-specified path names for windows and linux systems,
b) to pull URLs out of unstructured text stored in a file.  WordFreq calculates the frequencies
of words found in one or more files, screening out uninteresting ones (frequently used, specific
to the movie industry, articles, numbers, etc.)
'''

import os
import traceback
import exceptions
import string
import re

class MyException(exceptions.Exception):
    def __init__(self, message):
        print message
    def __str__(self):
        print "Sorry."
   
class SysUtils:
    #catch-all class for utilities
    def __init__(self, *args, **kwargs):
        #detect the os as windows or anything else then set the path delimiter
        if os.name == 'nt':
            self.slash = '\\'
        else:
            self.slash = '/'
           
    def verboseFileName(self, fn, path = None):
        #returns a verbose, fully-specified file name kwargs: fn filename; path path (optional)
        #construct the absolute path
        if path:
            return path + self.slash + fn
        else:
            return fn

   
    def openFile(self, fn, path = None):
        #opens a file and returns a list object of its contents
        #build the absolute path
        filestr = self.verboseFileName(fn = fn, path = path)   
        myfile =  open(filestr, 'r')
        content = myfile.readlines()
        myfile.close()
        return content
   
    def dumpToFile(self, fn, obj, path = None):
        #opens a file and writes the contents of list-like object to a file
        if len(obj) ==0:
            print "Warning: the file %s contains a null list"%fn
            obj = []
        filestr = self.verboseFileName(fn=fn, path=path)   
        myfile =  open(filestr, 'w')
        for o in obj:
            #if the string is not newline-terminated, add it
            if o[-1:] <> "\n":
                o = o + "\n"
            else:
                pass
            myfile.write (o)
        myfile.close()
       
   
    def pullUrls(self, content):
        #Grab everything that looks like a url from unstructured text; returns a clean list
        #      We'll define these as strings that contain any of the following:
        urlFlags = ["http:", "www.", ".com", ".net", ".org"]
        urls = []
        success = 0
        for c in content:
            #split it up; the url should be a contiguous piece beginning with http:
            words = c.split()
            #see if any of our url flags signals that this string is a url
            goodUrl = False
            for f in urlFlags:
                if c.lower().find(f) >=0: goodUrl = True
            #if our url string is a short version, make sure it begins with "http"
            if goodUrl:
                if c.lower()[:4] == "http":
                        urls.append(c)
                else:
                    urls.append ("http://" + c)
        return urls

   
class WordFreq:
    #adopted from http://www.daniweb.com/code/snippet216747.html

    def __init__(self, *kwargs):
        self.boringWords()

    def getFilename(self, fn, path = None):
        #use the system utilities construction of the file name
        #grab an instance of the utilities class
        sysutils = SysUtils()
        #fn = dict(fn=fn, path=path)
        filestr = sysutils.verboseFileName(fn=fn, path = path)
        return filestr  
       
    def boringWords(self):
        #this simply creates a list words we don't care about for creating a word frequency chart
        #NB it removes some negation words "not", "nor", etc. which could change the sentiment
        bw=[]
        #numbers
        bw.append(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"])
        bw.append(["eleven", "twelve","thirteen", "fourteen","fifteen", "sixteen", "seventeen", "eighteen", "nineteen"])
        bw.append(["ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninty"])
        bw.append(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"])       
        bw.append(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
       
        #short words, articles, etc.
        bw.append(["and", "or", "a", "an", "the", "i", "o", "oh", "etc"])
        bw.append(["is", "was", "will", "am", "as", "can", "cannot"])
        #frequency
        bw.append(["some", "both", "other", "much", "each", "several", "all", "any", "always", "often", "seldom", "never", "sometimes", "sometime", "about", "approximate", "frequently", "infrequently"])
        bw.append(["more", "such", "various", "many", "only", "most", "least", "less", "often", "seldom", "frequently", "with", "without", "very"])
        #negation
        bw.append(["no", "not", "too", "also", "although"]) 
        #logic
        bw.append(["or", "if", "when", "during", "still", "same", "however", "therefore", "but", "neither", "either", "nor", "ergo"])
        #interrogation
        bw.append(["who", "what", "when", "where", "why", "which", "how"])
        #conditional
        bw.append(["to", "of", "would", "could", "should", "may", "might", "then", "than"])
        #pronouns
        bw.append(["me", "i", "you", "we", "us", "they", "them", "we", "us", "he", "him", "she", "her", "it"])
        bw.append(["mine", "yours", "your", "theirs", "their", "ours", "our", "his", "hers", "its"])
        #prepositions and locations
        bw.append(["of", "at", "by", "from", "into", "around", "under", "over", "left", "right", "top", "bottom", "front", "back", "side"])
        bw.append(["on", "for", "between", "next", "last", "up", "in", "here", "there", "while", "through", "throughout", "are", "this", "that", "these", "those", "so"])
        bw.append(["before", "after", "during", "while", "now", "then"])
        bw.append(["close", "near", "far", "away", "widely", "distant", "high", "low"])
        #film industry throwaway words
        bw.append(["act", "play", "release", "perform", "open", "release", "star", "direct", "cast", "motion", "picture", "cinema", "screen", "movie", "film", "flick", "theater", "review", "actor", "actress", "produce", "producer", "audience", "box", "office"])
        bw.append(["acted", "played", "released", "performed", "opened", "releasing", "starred", "directed",  "screened", "filmed", "reviewed", "acted", "produce", "produced"])
        bw.append(["acts", "plays", "opens", "releases", "stars", "directs", "casts", "cinemas", "pitures", "screens", "movies", "films", "flicks", "theaters", "reviews", "actors", "actresses", "produces", "producers", "audiences"])
        bw.append(["acting", "playing", "performing", "opening", "releasing", "starring", "directing", "casting", "screening", "making", "reviewing" "acting", "producing"])
        bw.append(["nominated", "nominate", "nomination", "critic", "critics", "performance", "performance", "los", "angeles", "new york", "awards", "academy", "guild", "society" ])
        bw.append(["role", "roles", "won", "production", "character", "characters", "plot", "project", "performance", "supporting", "mtv", "television", "artist", "artists"])
        bw.append(["director", "actor", "career", "hollywood", "gross", "association", "critic"])
        #the most common nouns/verbs per http://en.wikipedia.org/wiki/Most_common_words_in_English
        bw.append(["time","person","year","way","day","thing","man","world","life","hand","part","child","eye","woman","place","work","week","case","point","government","company","number","group","problem","fact"])
        bw.append(["have","do","say","get","make","go","know","take","see","come","think","look","want","give","use","find","tell","ask","work","seem","feel","try","leave","call"])
        bw.append(["had","did","said","got","made","went","knew","took","saw","came","thought","looked","wanted","gave","used","found","told","asked","worked","seemed","felt","tried","left","called"])
        bw.append(["having","doing","saying","getting","making","going","knowing","taking","seeing","coming","thinking","looking","wanting","giving","using","finding","telling","asking","working","seeming","feeling","trying","leaving","calling"])
        bw.append(["has", "does", "says", "gets", "makes", "goes", "knows", "takes", "sees", "comes", "thinks", "looks", "wants", "gives", "finds", "asks", "feels", "seems", "feels", "tries", "leaves", "calls", "seems", "feels"])       
        #existential/copular
        bw.append(["be", "been", "being", "was", "are", "were", "is", "it's", "i'm", "we're"])
        #time references
        bw.append(["new", "old", "young",  "early", "late", "teen", "time", "timing", "date", "month", "year", "day", "hour", "minute", "time", "weekend", "week"])
        bw.append([ "times", "dates", "months", "years", "days", "hours", "minutes",  "weekends", "weeks"])
        bw.append(["first", "last", "long"])
        bw.append(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])
        bw.append(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
        bw.append(["2011", "2010", "2009", "2008", "2007", "2006", "2005"])
        #uncategorized, frequently used words (from http://en.wikipedia.org/wiki/Most_common_words_in_English)
        bw.append(["little", "own", "other", "big", "small", "different", "large", "public", "able"])
        #clean this up to make a one-d list of boring words
        #self.bwords = []
        self.bwords={}
        for wordVectors in bw:
            for words in wordVectors:
                #self.bwords.append(words)   
                self.bwords[words]=("",words)
                pass
       
    def cleanBoringWords(self, original):
        #deletes any uninteresting words from a list of words collected
        if type(original) == list:        
            clean = []
            for word in original:
                if not word[0] in self.bwords:
                    clean.append(word)
                else:
                    pass
        if type(original) == dict:
            clean = {}
            #freq_list2 = [(val, key) for key, val in freq_dic.items()]
            for i in original.items():
                key,val = i
                if not key in self.bwords:
                    clean[key] = val
                else:
                    pass               
        return clean
       
       
    def doWordCount(self, fn, path = None, freq_dic=None): 
        
        ret = []
       
        # set a regular expression for the punctuation marks to be removed
        punctuation = re.compile(r'[.?!,":;@$+*()#/]')
        filename = self.getFilename(fn, path)
        # create a list of all the words in the input file
        word_list = re.split('\s+', file(filename).read().lower())

        # create dictionary of word:frequency pairs; if we've passed one in, augment it.
        if not freq_dic:
            freq_dic = {}
       
        #increment the word counter as we find new instances of the word
        for word in word_list:
            # remove punctuation marks
            word = punctuation.sub("", word)
            # form dictionary; this adds an item if none exists and updates existant entries
            freq_dic[word] = freq_dic.get(word,0) + 1
            # create list of (key, val) tuple pairs
            freq_list = freq_dic.items()
            pass
               
        #get rid of the prosaic words ("and", "or", etc.)
        freq_dic =  self.cleanBoringWords(freq_dic)
       
        ret.append( 'Unique words: ' + str(len(freq_dic)) + ' sorted by highest frequency first:' + '\n')
        # create list of (val, key) tuple pairs
        freq_list2 = [(val, key) for key, val in freq_dic.items()]
        # sort by val or frequency
        freq_list2.sort(reverse=True)
        # display result
        for freq, word in freq_list2:
            ret.append( str(word) + '\t' + str(freq) + '\n')
        self.freq_dic = freq_dic
        self.freq_list2 = freq_list2
        return ret
    
def testUtils():
    '''runs tests on our url extraction routines'''
    sysutils = SysUtils()
    fn = "test.txt"
    #set up a file with some urls we hope to find in unstructured text
    urls = ["http://www.test.com",
            "https:/www.example.com",
            "www.example.com",
            "www.example.net",
            "www.example.org",
            "www."]
    fn = "junk"
    mypath = "C:\Documents and Settings\pat\My Documents\__jeff"

    #can we dump this to a file without a path?
    sysutils.dumpToFile(fn, urls)
    #...how about with a path?
    sysutils.dumpToFile(fn, urls, mypath)
    #open the file we just wrote
    rawList = sysutils.openFile(fn)
    #clean it up
    cleanList = sysutils.pullUrls(rawList)
    #set the output file to be something sensible
    ofn = fn + ".clean.txt"
    #write the cleaned-up version to an output file
    sysutils.dumpToFile(ofn, cleanList, mypath )  
    #dump the completed file
    outputList = sysutils.openFile(ofn, mypath)
    for o in outputList:
        print o
    pass

def testWordCount():
    #test teh work count logic
    wordfreq = WordFreq()
    mypath = "/home/pat1/workspace/djangoproj/djangoapp/LeoD/ReportDocs"
    myfile = "test.txt"
    #open ('/home/pat1/workspace/djangoproj/djangoapp/LeoD/ReportDocs/test.txt', 'r')
    wordfreq.doWordCount(myfile, mypath)
    '''this code demonstrates that we can feed an existing dictionary back into the freq
      rountine and augment its word list and the word counts.'''
    #fn = dict(fn=myfile, path=mypath, freq_dic = wordfreq.freq_dic)
    wordfreq.doWordCount(myfile, mypath, wordfreq.freq_dic)
    pass
   
if __name__ == "__main__":
    #testUtils()
    #testWordCount()
    pass
   

   '''
   
    #instance of our utilities module
    sysutils = SysUtils()
   
    #set the path and provide a list of input files
    mypath = "C:\Documents and Settings\pat\My Documents\__jeff"
    myfiles = ["LeoD.txt", "movieReviewBlog.txt"]
    '''