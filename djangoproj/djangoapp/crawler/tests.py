"""

"""

from django.test import TestCase

import unittest
import buzz
import buzz.buzzapp

#tests fror module models.py

#catch-all error
class generalFailureError():
    pass

class urlTests(unittest.TestCase):
    #see if we can import a bunch of strange urls
    def testImport(self):
        testUrls = [
            "http://www.dogma.com", 
            "http://www.dogma.com/?inp='inp'",
            "http://www.dogma.com/something/something_else/whatever/",
            666,
            ]
        for u in testUrls:
            u = buzz.buzzapp.models.Urls(url = u)
            self.assertTrue(type(u.url)==type(str()), ("url %s should be a string" %str(u)))

        
        #self.assertEquals(self.lion.speak(), 'The lion says "roar"')
        #self.assertRaises(ValueError, random.sample, self.seq, 20)
        #self.assert_(element in self.seq)
        #self.failUnless(self.widget.size() == (50,50), 'incorrect default size')
        
        
