import sys
import os
from os.path import dirname, abspath

approot = dirname(dirname(abspath(__file__)))

sys.path.append(approot)
sys.stdout = sys.stderr

os.environ['PYTHON_EGG_CACHE'] = "%s/eggs" % approot

import atexit
import cherrypy
import cherrypy._cpwsgi
import turbogears

configfile = "%s/prod.cfg" % approot
import buzzbot.commands
buzzbot.commands.boot(configfile)

turbogears.update_config(configfile=configfile, modulename="buzzbot.config")
turbogears.config.update({'global': {'server.environment': 'production'}})
turbogears.config.update({'global': {'autoreload.on': False}})
turbogears.config.update({'global': {'server.log_to_screen': False}})

#For non root mounted app:
#turbogears.config.update({'global': {'server.webpath': '/buzzbot'}})

import buzzbot.controllers
import logging
logging.basicConfig()

cherrypy.root = buzzbot.controllers.Root()

if cherrypy.server.state == 0:
    atexit.register(cherrypy.server.stop)
    cherrypy.server.start(init_only=True, server_class=None)

#For root mounted app
application = cherrypy._cpwsgi.wsgiApp

#For none-root mounted app
#def application(environ, start_response):
#    environ['SCRIPT_NAME'] = ''
#    return cherrypy._cpwsgi.wsgiApp(environ, start_response)

