
class Urls(SQLObject):
    class sqlmeta:
        fromDatabase = True  
        
class Badurls(SQLObject):
    class sqlmeta:
        fromDatabase = True       
      
class Word(SQLObject):
    class sqlmeta:
        fromDatabase = True
class Semanticlist(SQLObject):
    class sqlmeta:
        fromDatabase = True