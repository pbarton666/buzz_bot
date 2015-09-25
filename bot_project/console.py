#!/usr/bin/env python

"""
'console.py' is a script for starting an ipython session within the
buzzbot application's environment.

You must install ipython first. E.g.,:

  # Using Debian or Ubuntu's package manager
  sudo apt-get install ipython

  # Using easy_install
  easy_install -Z ipython
"""

if __name__ == "__main__":
    import buzzbot
    from buzzbot import *
    from buzzbot.model import *

    buzzbot.commands.boot()
    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed()
    print "* CONSOLE: Press CTRL-D or enter '%quit' to exit."
    ipshell()
