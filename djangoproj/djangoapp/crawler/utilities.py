
import models
import logging
import settings    
    
#set logs
log_filename = settings.LOGDIR + '/' + settings.LOG_NAME
logging.basicConfig(level=settings.LOG_LEVEL,
                    format='%(module)s %(funcName)s %(lineno)d %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_filename,
                    filemode='w')

class testDb():
    #some methods to add, delete content from the database to make sure it works as advertised
    def test(self):
        t = models.Urls 
        u = t.urls(url = "dogma.html")
        
        u = t.urls(url = "karma.html")
        u = t.urls(url = "fang.html")
        
        