#Plot class
# author: Michael Auer

#imports
import pyqtgraph as pg
import numpy as np
import threading
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor,QFont
#custom imports
from Connection import Connection

#Constants
defaultColors=[
QColor(5, 252, 82, 255),QColor(8, 248, 253, 255),QColor(253, 7, 241, 255),QColor(75, 0, 255, 255),
QColor(255, 0, 0, 255),QColor(239, 41, 41, 255),QColor(138, 226, 52, 255),QColor(114, 159, 207, 255),
QColor(173, 127, 168, 255),QColor(136, 138, 133, 255),QColor(164, 0, 0, 255),QColor(206, 92, 0, 255),
QColor(196, 160, 0, 255),QColor(78, 154, 6, 255),QColor(32, 74, 135, 255),QColor(92, 53, 102, 255)
]

#Plot Class witch inherits from PlotWidget and holds the PlotData and has its
#own Thead to liveplot things
class Plotter(pg.PlotWidget):
    #newData Signal
    newData = pg.QtCore.Signal(object)

    def __init__(self,parent):
        super(Plotter, self).__init__()

        #save parent
        self.parent=parent
        #Stop Event to make it stoppable
        self._stop_event = threading.Event()
        self._stop_event.set()
        self._pause_event = threading.Event()
        #Define Array to contain Measured Points
        self.data = []
        #init Variables
        self.connection=None
        self.plotThread=None
        self.plots=[]
        self.legend=None
        self.xunit="xunit"
        self.yunit="yunit"
        self.settings = QSettings('LMU-Muenchen', 'Voltmeter')
        self.parent.settingsPage.uiChange.connect(self.uiChange)
        self.uiChange()

    #function to connect the updatePlot function to the newData Signal
    def connect(self):
        #connect the newData Signal to the updatePlot function
        self.newData.connect(self.updatePlot)

    #function to disconnect all handlers from the newData signal
    def disconnectAll(self):
        #try to disconnect all handlers connectet to newData
        try:
            self.newData.disconnect()
        #catch and ignore error if it was not connected to anything
        except TypeError:
            pass

    #function to start the live Plot
    def start(self):
        #establish Connection
        self.connection=Connection()
        #start the Connection
        if not self.connection.start():
            self.stop("No Connection")
            return False

        #create new Plot Thread to liveplot things
        self.plotThread=PlotThread(self)
        #start the Thread
        self.plotThread.start()
        self.newPlot()

        #it is now running
        self._stop_event.clear()
        return True

    #make Plot stoppable
    def stop(self,reason=""):
        print("Plot stop calles: " + reason)
        if not self._stop_event.is_set():
            self.connection.stop(reason)
            self.parent.stopUi()
            #wati for the PlotThread to "finish"
            self.plotThread.wait()
            self._stop_event.set()
            print("Plot stopped")

    #make Plot pausable
    def pause(self,reason=""):
        self._pause_event.set()
        self.connection.pause()
        print("Plot paused: " + reason)

    def unpause(self):
        self._pause_event.clear()
        self.connection.unpause()
        print("Plot unpaused")

    #function to check if live Plot is stopped
    def stopped(self):
        allstopped=False
        if not self.plotThread ==None:
            allstopped=self._stop_event.is_set() and self.plotThread.stopped()
        else:
            allstopped=self._stop_event.is_set()
        return allstopped

    #function to check if live Plot is paused
    def paused(self):
        return self._pause_event.is_set()

    #function to add a New Plot to the Plotter
    def newPlot(self,data=np.empty([0,2])):
        lp=len(self.plots)
        pen=pg.mkPen(color=self.settings.value("colors",defaultColors,QColor)[lp%16],width=self.settings.value("lineThickness",3,int))
        self.data.append(data)
        plot=self.plot(self.data[lp],pen=pen)
        self.plots.append(plot)
        if lp==1:
            self.legend=self.addLegend()
            self.legend.addItem(self.plots[0], "Graph 1")
        if self.legend:
            self.legend.addItem(plot, "Graph "+str(lp+1))
        return plot

    #function to update the plot (must happen in Main Thread)
    def updatePlot(self,inpData=None):
        lp=len(self.plots)-1
        #plot the new data
        self.plots[lp].setData(self.data[lp])

        if inpData:
            if inpData[2] != self.xunit or inpData[3] != self.yunit:
                self.xunit=inpData[2]
                self.yunit=inpData[3]
                self.uiChange()
        #show status
        self.parent.statusBar().showMessage("Working",1000)

    #function witch is called if Something was changed in the Settings
    def uiChange(self):
        #get colors and width
        c=self.settings.value("colors",defaultColors,QColor)
        w=self.settings.value("lineThickness",3,int)
        #create each pen and update colors and width
        for i,p in enumerate(self.plots):
            pen=pg.mkPen(color=c[i],width=w)
            p.setPen(pen)
        #update labelStyle
        labelStyle = {'color': '#FFF', 'font-size': str(self.settings.value("axisThickness",20,int))+"px"}
        self.setLabel("bottom",self.xunit[0],units=self.xunit[1],**labelStyle)
        self.setLabel("left",self.yunit[0],units=self.yunit[1],**labelStyle)
        font=QFont()
        font.setPixelSize(self.settings.value("tickThickness",15,int))
        self.getAxis("bottom").tickFont = font
        self.getAxis("left").tickFont = font


#PlotThread Class inherits from QThread
#looks for Items in Queue and if one found calls for an Plot update
class PlotThread(pg.QtCore.QThread):

    def __init__(self,parent):
        super(PlotThread, self).__init__()
        self._stop_event = threading.Event()
        self.parent=parent
        self.inQueue=self.parent.connection.outQueue

    #make Thead stoppable
    def stop(self,reason=""):
        print("PlotThread stop called: " + reason)
        if not self._stop_event.is_set():
            self._stop_event.set()
            self.parent.stop(reason)
            print("PlotThread stopped")

    #function to check if Thread has stopped
    def stopped(self):
        return self._stop_event.is_set()

    #custom run function
    def run(self):
        print("Running PlotThread")
        while not self.stopped():
            #get Item from inQueue
            inpData=self.inQueue.get()
            if inpData == None:
                self.stop("Input Queue shutdown")
            elif inpData:
                lp=len(self.parent.plots)-1
                time,value,xunit,yunit=inpData
                #append inpData to the data array
                self.parent.data[lp]=np.append(self.parent.data[lp],[(time,value)],axis=0)
                #broadcast the new data array
                self.parent.newData.emit(inpData)
