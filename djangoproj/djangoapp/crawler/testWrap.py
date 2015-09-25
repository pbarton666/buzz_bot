from django.template import Variable, Library
from django.conf import settings
from django.utils.translation import ugettext, ungettext
from django.utils.encoding import force_unicode, iri_to_uri
from django.utils.safestring import mark_safe, SafeData
import urllib
import urllib2
import urlparse
import html2text

from django.utils.text import wrap
for i in range(1,10):
	value = " , Ehrhardt-Martinex, Karen; November&nbsp;2008, Report&nbsp;#&nbsp;E87,"
	arg = 2
	dogma = html2text.name2cp(value)
	print dogma
	a=1

print wrap(value, int(arg))