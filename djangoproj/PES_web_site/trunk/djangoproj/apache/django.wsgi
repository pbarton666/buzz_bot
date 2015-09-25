import os
import sys
#projroot = '/home/pat/workspace'
#projpath = '/home/pat1/workspace/djangoproj'
projroot = '/var/www/pes/current'
projpath = '/var/www/pes/current/djangoproj'




if not projpath in sys.path:
     sys.path.append(projpath)
if not projroot in sys.path:
     sys.path.append(projroot)
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoproj.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
if not projpath in sys.path or not projroot in sys.path:
	print "dogma"

