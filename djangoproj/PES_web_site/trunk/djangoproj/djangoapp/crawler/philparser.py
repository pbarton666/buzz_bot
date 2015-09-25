'''
This module employs pyparsing to extract dates from unstructured text. 

DataParser::grabData(<input string> returns a list datetime objects found (emptly list if no dates found)

Adapted from:  http://pcscholl.de/2009/09/24/better-later-than-never-the-pyparsing-based-date-parser/
  Works on most date formats (including: Jan 1, 2001; Feb 01, 2002;  Jun. 1, 2005;  
                               Jul. 01, 2006;  February 1, 2010;  29/02/2015;  30-Feb-16)
  Works for English and German                             
  Fails on verbose European-style dates like  1 March 2011
  Fails when comma is missing between day and year

First and last years are set in the code: first year is 2005, last is the current year
'''
from pyparsing import *
import string
from datetime import datetime
import os
import logging
import unittest

monthDict = {'january': 1, 'february': 2, 'march': 3, 'april':4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december':12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr':4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sept': 9, 'spt': 9, 'sep': 9, 'oct': 10, 'nov': 11, 'dec':12,
            'jan.': 1, 'feb.': 2, 'mar.': 3, 'apr.':4, 'jun.': 6, 'jul.': 7, 'aug.': 8, 'sept.': 9, 'spt.': 9, 'sep.': 9, 'oct.': 10, 'nov.': 11, 'dec.':12,
            'januar': 1, 'februar': 2, 'm\cx3rz': 3, 'april':4, 'mai': 5, 'juni': 6, 'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'dezember':12,
            'jan': 1, 'feb': 2, 'm\xc3r': 3, 'apr':4, 'mai': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'dez':12
            }

class DateParser():
    def __init__(self):
        self._lowest_year = 2005
        self._highest_year = datetime.now().year + 1 
        pass
    
    def grabDate(self, inputText):
        # zero-prefixed and non-prefixed numbers from 1 up to 31 (1, 2, ... 01, 02, ...31),
        # followed by ordinal (st, nd, rd, ...)
        days_zero_prefix = " ".join([("%02d" % x) for x in xrange(1, 10)])
        days_no_prefix = " ".join([("%d" % x) for x in xrange(1, 32)])
        day_en_short = oneOf("st nd rd th")
        day = ( (oneOf(days_zero_prefix) ^ oneOf(days_no_prefix) ).setResultsName("day")
                + Optional(Suppress(day_en_short)) ).setName("day")

        # months, in numbers or names
        months_zero_prefix = oneOf(" ".join([("%02d" % x) for x in xrange(1, 10)]))
        months_no_prefix = oneOf(" ".join([("%d" % x) for x in xrange(1, 13)]))
        months_en_long = oneOf("January February March April May June July August September October November December")
        months_en_short = oneOf("Jan Feb Mar Apr May Jun Jul Aug Sep Spt Sept Oct Nov Dec Jan. Feb. Mar. Apr. Jun. Jul. Aug. Sep. Spt. Sept. Oct. Nov. Dec.")
        months_de_long = oneOf("Januar Februar M\cx3rz April Mai Juni Juli August September Oktober November Dezember")
        months_de_short = oneOf("Jan Feb M\xc3r Apr Mai Jun Jul Aug Sep Okt Nov Dez")
        month = (months_zero_prefix.setName("month_zp").setResultsName("month") |
                 months_no_prefix.setName("month_np").setResultsName("month") |
                 months_en_long.setName("month_enl").setResultsName("month") |
                 months_en_short.setName("month_ens").setResultsName("month") |
                 months_de_long.setResultsName("month") |
                 months_de_long.setResultsName("month"))

        # set the year strings
        years = " ".join([("%d" % x) for x in xrange(self._lowest_year, self._highest_year)])
        years_short = " ".join([("%02d" % (x % 100)) for x in xrange(self._lowest_year, self._highest_year)])
        year_long = oneOf(years)
        year = (year_long ^ oneOf(years_short)).setResultsName("year")

        # choice of separators between date items; if two occur, they should match
        sep_literals = oneOf(". - /") ^ White() # ".-/ "
        sec_lit = matchPreviousLiteral(sep_literals)

        # optional comma
        comma = Literal(",") | White()
        # punctuation
        punctuation = oneOf([x for x in string.punctuation])

        # EBNF resulting
        date_normal = day + Suppress(sep_literals) + month + Suppress(sec_lit) + year
        date_rev = year + Suppress(sep_literals) + month + Suppress(sec_lit) + day
        date_usa = month + Suppress(sep_literals) + day + Suppress(sec_lit) + year
        date_written = (months_en_long.setResultsName("month") | months_en_short.setResultsName("month")) + day + Suppress(comma) + year

        # HTML tag Bounds
        anyTag = anyOpenTag | anyCloseTag
        date_start = Suppress(WordStart() ^ anyTag ^ punctuation)
        # FIXME: there is a problem here
        date_end = Suppress(WordEnd() ^ anyTag ^ punctuation)

        # final BNF
        parser = date_start + (date_normal ^ date_usa ^ date_written ^ date_rev) + date_end
        result = parser.scanString(inputText)
        #The result is an iterable object with three elements: 1) month, day, year, 2) first position of the date in the string, 2)
        #  the last position of the date in the string. The first element can be cohersed into a list or dict.  We'll use the former because
        #  we really want to return a datatime object, which we can't do with "February" say.
        returnDates=[]
        for output, firstPos, lastPos in result:
            returnDates.append(self._makeDateTime(output.asDict()))   
        return returnDates
    
    def _makeDateTime(self, oDict):
        #Utility to coherse a parser return into a valid datetime object
        year = int(oDict['year'])
        day = int(oDict['day'])
        #the month might be numeric (1, say) or a name (January, say)
        try:
            month = int(oDict['month'])
        except:
            month = monthDict.get(oDict['month'].lower())
        try:
            return datetime(year, month, day)
        except:
            return None

    
    def _set_logger(self):
        #this sets up the logging parameters.  The log will appear at ./logs/master.log (or whatever is in the settings
        #  at the top of this module.)
        LOGDIR =  os.path.join(os.path.dirname(__file__), 'logs').replace('\\','/')
        log_filename = LOGDIR + '/' + LOG_NAME
        logging.basicConfig(level=LOG_LEVEL,
                            format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_filename,
                            filemode='w')    
        
    def testDateParser(self):
        #start with some common date examples
        dateformats = ["Jan 1, 2006", "Feb 01, 2006",
                       "Jun. 1, 2006", "Jul. 01, 2006",  
                       "January 1, 2009", "February 1, 2010",
                       "28/02/2010", "30-Apr-10"]
        #bury them within some text and parse; we should be albe to coherse the results into a datatime object
        dates = []
        for d in dateformats:
            dates.append("some text " + d + " more text")    
        for date in dates:    
            myDates =  self.grabDate(date)
            assert isinstance(myDates[0], datetime)    
            a=1
                

if __name__=='__main__':
    #run some tests
    clsObj = DateParser()
    mydate = clsObj.grabDate("dateline January 1 2009 blah blah January 31, 2010")
    clsObj.testDateParser()
