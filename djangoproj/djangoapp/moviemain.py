'''This module contains routines to extract data from the crawler's database to analyze content for Jeff Hardy's
    project Alpha.  The idea is to extract the database content for inclusion in a client-ready report, probably in
	Excel.  I plan to do this by producing a bunch of tab-deliminted files into a directory with the name of the search.
	    Main directory (user can specify, else defaults to "Analysis")
			 ReportDocs
		       urls (urls found/visited) (url, date first visited)
			   wordfreq (most frequently used words)  (word, count)
			   conceptfreq (concepts most related to words found/proximity) (word, concept1, concept1Proximity, concept2, concept2Proximity ...to 10)
			   polarity (polarity/sentiment score)  (score1, score2, etc.)
			   allcontent (a dump of everything)
			 Note: the following is the directory structure for luminoso
			 Documents (.xls files)
			 (empty directories) Canonical  Matrices  Results 
			 settings.json  (dictionary of documents - don't know whether I set this up or luminoso does)
'''
import sys, os
import django_dbRoutines
dbMs = django_dbRoutines.DatabaseMethods()

#make a dict of the analysis subdirectories (keeps from having to hard-code them elsewhere)
datadirs = {'Canonical':'Canonical', 'Matrices': 'Matrices', 'Results': 'Results', 'ReportDocs': 'ReportDocs', 'Documents':'Documents'}
masterContentFileName = 'masterContent.txt'
wordCountFileName = "wordCount.xls"

class CustomException(Exception):
	def __init__(self, value):
		self.parameter = value
	def __str__(self):
		return repr(self.parameter)


class PrepDirs():
	'''Routines for setting up the directories for the semantic analysis'''
	def __init__(self, rootdir, searchName):
		self.dirname = rootdir + '/' + searchName
		self.mode = 0770 #all/all/none; the initial 0 is necessary.
		os.umask(0)  #this needed because permissions are set as (mode & ~umask & 0777)
	
	def mkdir(self, proposed, mode):
		#tries to create a directory, fails gracefully if it already exists
		try:
			os.mkdir(proposed, mode)
		except OSError, (ErrorNumber, ErrorMessage):
			if ErrorNumber == 17:
				print "INFO:directory %s already exists. " %(proposed)
			else:
				print ("Sorry, you can't set up the directory %s for this project - check you permissions %s " %(proposed, ErrorMessage))
	
	def setDirs(self):		
		#set the root directory for the analysis (if needed); to keep this atomic, we'll return a dictionary of the dirs
		allSubdirs = []
		self.mkdir(self.dirname, self.mode)
		allSubdirs.append(('RootDir', self.dirname)) 
		#...and the subdirectoris (these set as module globals)
		for k, d in datadirs.items():
			thisSubDir = self.dirname + '/' + d
			self.mkdir(thisSubDir, self.mode)
			allSubdirs.append((d, thisSubDir))
		return dict(allSubdirs)	
	
	def testSetDirs(self):
		dirDict = self.setDirs()  #no directory provided - uses current
		dirDict = self.setDirs()  #no directory provided - tries to overwrite same
		dirDict = self.setDirs('/junk/junk/')  #tries to put a directory in a location that (probably) doesn't exist
		
class PullData():
	'''This has routines to tap and prepare the crawler data using the django_dbRoutines'''
	def __init__(self, name):
		#figure out what search number has been requested
		self.name = name
		self.search = dbMs.getSearchNumFromName(name)
		if self.search == 0: raise CustomException ("The search %s does not exist" %name)
		
		pass
	
	
	def makeUrlsFile(self, dirDict, limit=None):
		'''make a tab-delimited file of the urls for a search and write it to the approrpiate directory.
		 The input arg is a dict of the directories we're populating - we'll grab the correct one for urls'''
		
		dateFormatStr = "%b %d, %Y"  #more date formatting at http://docs.python.org/library/time.html
		#get the urlObjects (the urls w/ all the associated data)
		urlsObjs = dbMs.getUrlsObjectsForSearch(self.search, limit)
		#open a file for output
		fObj = open(dirDict['ReportDocs'] + '/' + 'urls.xls', 'w')
		#iterate through the db return to extract desired info; 
		fObj.write('Added \t Visited \t URL \t \n')
		for u in urlsObjs:
			if u.visit_date: #we may not have a visit date for a newly-added
				niceVisitDate = u.visit_date.strftime(dateFormatStr)
				niceVisitDate = '----'			
			fObj.write (u.add_date.strftime(dateFormatStr) + '\t' + niceVisitDate + ' \t' + u.url + ' \n')
		fObj.close()	

	def makeContentFiles(self, dirDict, limit=None):
		'''make a tab-delimited file for each of the content bits we snagged for our search and write it to the approrpiate directory.
		 The input arg is a dict of the directories we're populating - we'll grab the correct one for urls.  We'll also prepare a master
		 file that has all the content for all the urls so we can run a word frequency routine against it'''
		
		fObjMaster = open(dirDict['ReportDocs'] + '/' + masterContentFileName, 'w')
		#get the contentObjects 
		contObjs = dbMs.getContentForSearch(self.search, limit)
		#we'll write a file for each, with simple file indices
		fileix = 0
		for c in contObjs:
			#open a file for output
			fObj = open(dirDict['Documents'] + '/' + 'file_' + str(fileix) + '.txt', 'w')
			#this looks a bit strange, but it utilizes SQLObjects ability to drill thru table joins
			fObj.write (c.contentid.content + '\n')
			fObj.close()
			fileix +=1
			#write it to our master file, as well
			fObjMaster.write(c.contentid.content + '\n')	
		fObjMaster.close()	
		pass
	
	def makeWordCount(self, dirDict):
		'''do a word count against the master content file.  This taps into a word count class in wordCount.py.  NB that this class
		contains a lot of exclusion words that are highly subjective and related to the movie industry.'''
		
		#instansiate a file object
		fObj = open(dirDict['ReportDocs'] + '/' + wordCountFileName, 'w')
		
		#instansiate and run the word count routine
		import wordCount
		path = dirDict['ReportDocs']
		freq = wordCount.WordFreq()
		freqTable = freq.doWordCount(masterContentFileName, path)
		#this has returned a tab delimited list of terminated lines
		for f in freqTable:
			fObj.write(f)
		fObj.close()
		pass
	
if __name__=="__main__":
	
	
	rootDirName = os.curdir
	searchName = "LeoD"
	#prepare our target directories (their names are established at the top of this file)
	prepDirs = PrepDirs(rootDirName, searchName)
	dirDict = prepDirs.setDirs()
	
	#instansiate the data extraction class with the name of our current search
	pullData = PullData(searchName)
	
	#now run some routines
	#...pull the content and prepare it for pci analysis
	pullData.makeContentFiles(dirDict, 5000)  #second argument is an optional limit (used for testing)
	#...pull the urls for reporting
	pullData.makeUrlsFile(dirDict, 5000)
	#...get a word count/frequency for both reporting and refining the pca
	pullData.makeWordCount(dirDict)
	'''
	pullData.makeContentFiles(dirDict, 50)  #second argument is limit (for testing)
	pullData.makeUrlsFile(dirDict, 50)  #second argument is limit (for testing)
	'''
	

	pass

