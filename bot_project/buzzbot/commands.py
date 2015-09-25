# -*- coding: utf-8 -*-
"""This module contains functions called from console script entry points."""

import types
import sys
from os import getcwd
from os.path import dirname, exists, join

import pkg_resources
pkg_resources.require("TurboGears>=1.0.4.4")
pkg_resources.require("SQLObject>=0.8")

import cherrypy
import turbogears

cherrypy.lowercase_api = True

global configuration
configuration = None

class ConfigurationError(Exception):
    pass


def boot(configfile=None, use_argv=False):
    """Boot the environment containing the classes and configurations."""

    setupdir = dirname(dirname(__file__))
    curdir = getcwd()

    if configfile:
        pass # Already a string
    elif use_argv and len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        alternatives = [
            join(setupdir, "local.cfg"),
            join(setupdir, "dev.cfg"),
            join(setupdir, "prod.cfg")
        ]
        for alternative in alternatives:
            if exists(alternative):
                configfile = alternative
                break

    if not configfile:
        try:
            configfile = pkg_resources.resource_filename(
              pkg_resources.Requirement.parse("buzzbot"),
                "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            raise ConfigurationError("Could not find default configuration.")

    global configuration
    configuration = configfile

    print "** Booting configuration: %s" % configfile
    turbogears.update_config(configfile=configfile,
        modulename="buzzbot.config")

def start():
    """Start the CherryPy application server."""
    boot(use_argv=True)
    from buzzbot.controllers import Root
    turbogears.start_server(Root())
