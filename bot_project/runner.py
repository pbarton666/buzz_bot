#!/usr/bin/env python

"""
'runner.py' is a script for running Python code within the buzzbot
application's environment.

For usage instructions, run 'runner.py -h'.

You can also use it as a class, e.g.:
    from runner import Runner
    Runner.execute(code="print 1")
    Runner.execute(filename="myfile.py")
    Runner.run(["myfile.py"])
"""

import sys
from pprint import pprint as pp

import buzzbot
import buzzbot.model
import buzzbot.model as model
from buzzbot.model import *
import buzzbot.commands
buzzbot.commands.boot()

class Runner:
    @classmethod
    def fail(self, message):
        """
        Fail with an error message and exit interpreter.
        """
        print "ERROR: %s" % message
        exit(1)

    @classmethod
    def execute(self, code=None, filename=None):
        """
        Execute a string of Python code or the contents of a Python file within the
        application environment.
        """
        bundle = None
        if code:
            bundle = compile(code, '<exec>', 'exec')
        elif filename:
            handle = None
            try:
                handle = open(filename)
                code = handle.read()
                bundle = compile(code, filename, 'exec')
            finally:
                handle.close()
        exec bundle

    @classmethod
    def run(self, argv=[]):
        """
        Use runner against command-line arguments.
        """

        if len(argv) == 1:
            self.fail("Insufficient arguments, run with -h for help")
        else:
            if argv[1] == '-h':
                print """
SUMMARY
  'runner.py' executes Python code within the application environment.

USAGE
  runner.py [options] [arguments]

EXAMPLES

  # Execute a file:
  runner.py myfile.py

  # Execute code:
  runner.py -e 'print "%s" % "Hi."'
                """.strip()
            elif argv[1] == '-e':
                if len(argv) == 3:
                    code = argv[2]
                    self.execute(code=code)
                else:
                    self.fail("Insufficient arguments for -e, no Python code was specified")
            else:
                try:
                    filename = argv[1]
                    self.execute(filename=filename)
                except Exception, e:
                    self.fail("Failed to execute code because:\n%s" % e)

if __name__ == "__main__":
    Runner.run(sys.argv)
