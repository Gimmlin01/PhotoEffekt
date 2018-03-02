#Connection class
#author: Michael Auer
import time
#Dummy Device make a new Class based on this one if a new Device should be connected.
#search for IMPORTANT to see the lines witch should be changed
class Dummy(object):
    def __init__(self):
        super(Dummy,self).__init__()
        print("Running Dummy Connection")
        import random
        self.a=random.random()

        #----IMPORTANT
        self.startTime=time.time()
        self.open = True
        self.warningText=("Text1","Text2","Detail")

    #function to check if Connection is open
    def isOpen(self):
        return self.open

    #function is called in a loop in the Connection-Thread run function
    def measure(self):
        import math
        yvalue=time.time()-self.startTime
        # Do your Magic
        xvalue =0.0015* math.sin(self.a*yvalue)
        time.sleep(0.01)
        #-----IMPORTANT funciton must return (MEASURED VALUE as int/float ,UNIT as String only A not mA (automagical))
        return (yvalue,xvalue,("Zeit","s"),("x","m"))
