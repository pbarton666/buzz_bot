# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.


import sys
from os import getcwd
from os.path import dirname, exists, join

import pkg_resources
pkg_resources.require("TurboGears>=1.0.4.4")
pkg_resources.require("SQLObject>=0.8,<=0.10.0")

import cherrypy
import turbogears
import sqlobject

cherrypy.lowercase_api = True


from turbogears import testutil, database
import buzzbot.model

sqlobject.dburi="notrans_mysql://root:dogma@localhost:3306/datamine1"
class testDatetimeobj(testutil.DBTest):
    def get_model(self):
        return Test
    def test_input(self):
        t = buzzbot.model.Test()
        assert t.testdatetime    



# database.set_db_uri("sqlite:///:memory:")

# class TestUser(testutil.DBTest):
#     def get_model(self):
#         return User
#     def test_creation(self):
#         "Object creation should set the name"
#         obj = User(user_name = "creosote",
#                       email_address = "spam@python.not",
#                       display_name = "Mr Creosote",
#                       password = "Wafer-thin Mint")
#         assert obj.display_name == "Mr Creosote"

