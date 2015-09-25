'''
This is invoked from models.py to wrap whatever we're testing today within the Django framework.  This 
way, all the Django components are pre-loaded, the environmental variables are set, etc.
'''
mydebug = 1
class testMods():
    def __init__(self):
        if mydebug:
            import utilities
            print X
            
        