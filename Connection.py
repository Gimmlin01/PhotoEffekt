#Connection class
#author: Michael Auer

import threading,time,os,importlib,sys
from queue import Queue
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox

#Connection Class
class Connection(threading.Thread):
    def __init__(self):
        super(Connection, self).__init__()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._stop_event.set()
        self.outQueue=Queue()
        self.settings = QSettings('LMU-Muenchen', 'Voltmeter')
        self.device=None

    #function to init the Device and import the given python scripts
    def initDevice(self):
        try:
            activeConnection = self.settings.value('connection', "Dummy")
            if activeConnection:
                #add the current Path to the sys path if neccessary
                if self.settings.value("devicePath",False):
                    sys.path.append(self.settings.value("path",""))
                #import the modules
                folderModule = importlib.import_module(self.settings.value("devicePath","bundled"))
                deviceModule = importlib.import_module(self.settings.value("devicePath","bundled")+"."+activeConnection)
                #reload module if already imported before
                importlib.reload(folderModule)
                importlib.reload(deviceModule)
                #return one device instance
                return getattr(deviceModule, activeConnection)()
        except Exception as e:
            text="Device not initiated"
            textd="There is a problem in the "+activeConnection+".py in the device folder.\nMake sure you Name each Device Class like its filename:\n Dummy -> Dummy.py"
            self.showDialog(t=text,td=textd,ti=str(e))

    #function to start the Connection
    def start(self):
        #init Device
        self.device=self.initDevice()
        #check if device is initiated
        if not self.device:
            return False
        #ceck if device is ready to measure
        if not self.device.isOpen():
            #if not show error dialog
            self.showDialog()
            return False

        print("Device Open")
        self._stop_event.clear()
        super(Connection, self).start()
        #return True for Start IO
        return True

    #function to stop the connection
    def stop(self,reason=""):
        print("Connection stop called: " + reason)
        if not self._stop_event.is_set():
            #if Queue is put empty the other worker knows to close the queue
            self.outQueue.put(None)
            self._stop_event.set()
            self.join()
            print("Connection stopped")

    #function to pause the connection
    def pause(self):
        if not self._pause_event.is_set():
            self._pause_event.set()
            print("Connection paused")

    #function to unpause the connection
    def unpause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            print("Connection unpaused")

    #function to return stopped state
    def stopped(self):
        return self._stop_event.is_set()

    #function to return pause state
    def paused(self):
        return self._pause_event.is_set()

    #function to override the run function of the Thread Class
    def run(self):
        print("Connection started")
        #check if stopped
        while not self.stopped():
            #check if paused
            if not self.paused():
                #call the measure function of the device and put the returned value in the Queue
                value=self.device.measure()
                self.outQueue.put(value)
            else:
                time.sleep(0.5)

    #function to show Error Dialog with the text "t" and info text "ti" and detailed text "td"
    def showDialog(self,t=None,ti=None,td=None):
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Warning)
       if (t==None):
           t,ti,td = self.device.warningText
       msg.setText(t)
       msg.setInformativeText(ti)
       msg.setWindowTitle("Warning")
       msg.setDetailedText(td)
       msg.setStandardButtons(QMessageBox.Ok)
       retval = msg.exec_()
