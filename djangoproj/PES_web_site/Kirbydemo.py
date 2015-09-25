"""
Menu Fun
by K. Urner

Oregon Curriculum Network:  DM Track

Building up a small vocabulary of test
modules will help you experiment with
design patterns and syntax.  You may
wish to repurpose the code to be about
something other then menu fun.  Maybe
save a snapshot with a different name.
Fork off in a new direction.

Possible grade level: DM(0)
Suggested activities:
* add the ability to create and retire trains
* have a menu that dynamically lists trains
* keep track of trains by number or name
* after choosing a train, then prompt with status menu
* add the option to pickle or otherwise store a train
for future retreival.

Exercises the following:
string.Template, getattr, hasattr, setattr

Illustrates:
putting functions in a list and treating them as
callables.
"""

from string import Template  # to be more interesting

"""
this Train class might be instantiated multiple times.
However in the code below, only a single instance is
created when the mainloop is launched.
"""

class Train( object ):
    """
    Only the one global train object in this module.
    Behaves likes C struct.  No methods, just state.
    """
    pass

"""
these functions check and/or change the status of
the train, including whether it has a 'moving'
attribute, added programmatically
"""

def start_train(thetrain):
    if hasattr( thetrain, 'moving' ):
        if thetrain.moving == True:
            print "The train is already moving."
            return
    thetrain.moving = True
    print "The train has started."

def stop_train(thetrain):
    if hasattr( thetrain, 'moving' ):
        if thetrain.moving == False:
            print "The train has already stopped."
        else:
            thetrain.moving = False
            print "The train has stopped."
    else:
        print "The train has never moved."

def add_car(thetrain):
    if getattr(thetrain, 'moving', False):
        print "Train moving, cannot add car."
    else:
        # Remains of an old error, left in for didactic purposes
        # print "DEBUG: ", getattr(thetrain, 'cars', 0) + 1
        # thetrain.cars = setattr(thetrain, 'cars', getattr(thetrain, 'cars', 0) + 1)
        setattr(thetrain, 'cars', getattr(thetrain, 'cars', 0) + 1)
        print "%s has %s cars" % (thetrain.name, thetrain.cars) 

def remove_car(thetrain):
    if getattr(thetrain, 'moving', False):
        print "Train moving, cannot remove car."
    else:
        setattr(thetrain, 'cars', getattr(thetrain, 'cars', 1) - 1)
        if thetrain.cars <= 0:
            thetrain.cars = 0
            print "%s has no cars" % thetrain.name
        else:
            print "%s has %s cars" % (thetrain.name, thetrain.cars) 

def end(thetrain):
    if hasattr(thetrain, 'moving'):
        print "The train is %s." % (
            ['not moving','moving'][int(thetrain.moving)],)
    else:
        print 'The train never moved.'
    print "Logging out."

mainmenu = Template("""
        $name
        ===========================
        1 - start train
        2 - stop train
        3 - add car
        4 - remove car
        0 - quit
        """)
    
def menu_loop():
    """
    the only train is created here and persists only
    so long as the loop keeps looping.  Consider adding
    menu options to store and retreive the train's state
    """
    otrain = Train()  # a train is born!
    otrain.name = "L&O Express"

    things_to_do = [start_train, stop_train, add_car, remove_car] # global functions

    while True:    
        print mainmenu.substitute({'name':otrain.name}) 
        menusel = raw_input("Choice?: ")

    
        if menusel in ['1','2','3','4']:
            sel = things_to_do[int(menusel) - 1]
            sel(otrain)
        elif menusel == '0':
            break
        else:
            print 'Choose 1,2 or 0'
    print "Quitting"
    end(otrain)
    # otrain goes out of scope here

if __name__ == '__main__':
    menu_loop()
