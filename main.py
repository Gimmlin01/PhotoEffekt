#!/usr/bin/python3

#author: Michael Auer

#Standart imports
import sys,os,ast
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget,QFileDialog,QGroupBox,QPushButton,QRadioButton,QLabel,QGridLayout
from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QSettings,QSize,QPoint
import numpy as np
from scipy.optimize import curve_fit
#custom imports
from Plotter import Plotter
from Pages import SettingsPage, LcdPage

wellenString='[["585nm",585e-9],["581nm",581e-9],["580nm",580e-9],["546nm",546e-9],["492nm",492e-9],["439nm",439e-9],["400nm",400e-9]]'

def f(x,a,c):
    return a*x+c

def find_in_sublist(haufen,nadel):
    for x in range(0,len(haufen)):
        if nadel in haufen[x]:
            break
        else:
            pass
    else:
        x=None
    return x

#define mainPage
class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage,self).__init__()
        self.settings = QSettings('LMU-Muenchen', 'PhotoEffekt')
        self.settings.setValue("path",os.path.dirname(os.path.realpath(__file__)))
        try:
            self.wellen=ast.literal_eval(self.settings.value("wellenText",wellenString))
        except Exception as e:
            print(e)
            self.wellen=[]
        self.lcdPage=LcdPage()
        self.settingsPage=SettingsPage()
        self.lastData=None
        self.labels=[]
        self.wellenRadios=[]
        self.settingsPage.uiChange.connect(self.uiChange)
        self.initUI()

    def keyPressEvent(self, event):
        super(MainPage,self).keyPressEvent(event)
        keys=self.settings.value("measureKeys",[16777272], type=int)
        key=event.key()
        if key in keys:
            self.measure()


    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('mainPageSize', QSize(1000, 400)))
        self.move(self.settings.value('mainPagePos', QPoint(50, 50)))
        self.setWindowTitle('PhotoEffekt')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))

        #add Action to Close Programm
        self.exitAction = QAction(QIcon(resource_path('icons/ExitIcon.png')), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)


        #add Action to Open Settings
        self.openSettingsAction = QAction(QIcon(resource_path('icons/SettingsIcon.png')), '&Settings', self)
        self.openSettingsAction.setShortcut('Ctrl+E')
        self.openSettingsAction.setStatusTip('Open Settings')
        self.openSettingsAction.triggered.connect(self.openSettings)

        #add Action to Save the Data of the current Plot
        self.saveDataAction = QAction(QIcon(resource_path('icons/SaveIcon.png')), '&Save', self)
        self.saveDataAction.setShortcut('Ctrl+S')
        self.saveDataAction.setStatusTip('Save Plot Data')
        self.saveDataAction.triggered.connect(self.saveData)

        #add Action to Load the Data
        self.loadDataAction = QAction(QIcon(resource_path('icons/LoadIcon.png')), '&Open', self)
        self.loadDataAction.setShortcut('Ctrl+O')
        self.loadDataAction.setStatusTip('Open saved Plot Data')
        self.loadDataAction.triggered.connect(self.loadData)

        #add Action to Start Measuring again
        self.startAction = QAction(QIcon(resource_path('icons/StartIcon.png')), '&Start', self)
        self.startAction.setShortcut('Ctrl+R')
        self.startAction.setStatusTip('Connect to Device')
        self.startAction.triggered.connect(self.startMeasure)


        #add Action to Stop Measuring
        self.stopAction = QAction(QIcon(resource_path('icons/StopIcon.png')), '&Stop', self)
        self.stopAction.setShortcut('Ctrl+C')
        self.stopAction.setStatusTip('Stop Measurement')
        self.stopAction.triggered.connect(self.stopMeasure)
        self.stopAction.setEnabled(False)

        #add Action to Measured
        self.measureAction = QAction(QIcon(resource_path('icons/SaveIcon.png')), '&Measure', self)
        self.measureAction.setShortcut('F9')
        self.measureAction.triggered.connect(self.measure)
        #create new MenuBar
        menubar = self.menuBar()
        #MenuBar entrys
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.saveDataAction)
        fileMenu.addAction(self.loadDataAction)
        fileMenu.addAction(self.openSettingsAction)
        fileMenu.addAction(self.exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(self.exitAction)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.stopAction)
        toolbar.addAction(self.openSettingsAction)


        self.plotWidget = Plotter(self,legend=False)
        #show MainWindow
        self.uiChange()
        self.show()


    def createInfoWidget(self):
        self.labels=[]
        self.wellenRadios=[]
        freqGroupBox=QGroupBox("Wellenlänge")
        freqVbox=QVBoxLayout()
        for w in self.wellen:
            radio = QRadioButton(w[0])
            self.wellenRadios.append(radio)
            freqVbox.addWidget(radio)
        if len(self.wellenRadios) >0:
            self.wellenRadios[0].setChecked(True)
        freqGroupBox.setLayout(freqVbox)

        #create Ergebnisse Layout
        layout = QGridLayout()
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 4)

        #create Steigung Row
        labelSteigungText=QLabel("Steigung: ")
        self.labels.append(labelSteigungText)
        layout.addWidget(labelSteigungText,0,0)
        labelSteigung=QLabel("0")
        self.labels.append(labelSteigung)
        layout.addWidget(labelSteigung,0,1)

        #create Y-Achsenabschnitt Row
        labelYachseText=QLabel("Y-Achsenabschnitt: ")
        self.labels.append(labelYachseText)
        layout.addWidget(labelYachseText,1,0)
        labelYachse=QLabel("0")
        self.labels.append(labelYachse)
        layout.addWidget(labelYachse,1,1)

        #create Plank Row
        labelPlankText=QLabel("Plank Konstante: ")
        self.labels.append(labelPlankText)
        layout.addWidget(labelPlankText,2,0)
        labelPlank=QLabel("0")
        self.labels.append(labelPlank)
        layout.addWidget(labelPlank,2,1)


        #create resultGroupBox
        resultGroupBox=QGroupBox("Ergebnisse")
        resultGroupBox.setLayout(layout)

        #create infofreqWidget
        infofreqWidget=QWidget()
        infofreqHBox = QHBoxLayout()
        infofreqHBox.addWidget(freqGroupBox,1)
        infofreqHBox.addWidget(resultGroupBox,2)
        infofreqWidget.setLayout(infofreqHBox)

        measureButton=QPushButton("Messen")
        resetButton=QPushButton("Reset")
        calcButton=QPushButton("Auswerten")
        measureButton.clicked.connect(lambda:self.measure())
        resetButton.clicked.connect(lambda:self.reset())
        calcButton.clicked.connect(lambda:self.calc())
        buttonWidget=QWidget()
        buttonHBox = QHBoxLayout()
        buttonHBox.addWidget(measureButton)
        buttonHBox.addWidget(calcButton)
        buttonHBox.addWidget(resetButton)
        buttonWidget.setLayout(buttonHBox)



        #create Info Widget
        infoWidget=QWidget()
        infoVBox=QVBoxLayout()
        infoVBox.addWidget(self.lcdPage,4)
        infoVBox.addWidget(infofreqWidget,4)
        infoVBox.addStretch(1)
        infoVBox.addWidget(buttonWidget)
        infoWidget.setLayout(infoVBox)

        return infoWidget

    def connectDevice(self):
        #connect the Lcd to the current Plot
        self.lcdPage.connectTo(self.plotWidget)
        self.plotWidget.newData.connect(self.newData)

    def newData(self,inpData):
        self.lastData=inpData

    def measure(self):
        if self.plotWidget.stopped():
            if not self.startMeasure():
                return
        if self.lastData:
            i=0
            wert=0
            for w in self.wellenRadios:
                if w.isChecked():
                    i=self.wellenRadios.index(w)
                    wert=self.wellen[find_in_sublist(self.wellen,w.text())][1]
                    freq=(299792458)/wert
            mdata=self.plotWidget.data[0]
            ii=find_in_sublist(mdata,freq)
            xvalue,yvalue,xunit,yunit=self.lastData
            if not ii==None:
                mdata[ii]=[freq,yvalue]
                self.plotWidget.replacePlot(id=0,scatter=True,data=mdata)
            else:
                data=(freq,yvalue,("Frequenz","Hz"),yunit)
                self.plotWidget.updatePlot(id=0,inpData=data)
                if i<len(self.wellenRadios)-1:
                    self.wellenRadios[i].setChecked(False)
                    self.wellenRadios[(i+1)%len(self.wellenRadios)].setChecked(True)

    def calc(self):
        xdata,ydata = self.plotWidget.plots[0].getData()
        popt, pcov = curve_fit(f, xdata, ydata)
        newx=np.arange(min(xdata),max(xdata),(max(xdata)-min(xdata))/1000)
        newy=f(newx,*popt)
        data=np.empty([0,2])
        for paar in zip(newx,newy):
            data=np.append(data,[paar],axis=0)
        a,c=popt
        e=1.6021766208E-19
        h=a*e
        self.labels[3].setText('{:.2e} {}'.format(c,"V"))
        self.labels[1].setText('{:.2e} {}/{}'.format(a,"V","Hz"))
        self.labels[5].setText('{:.2e} Js'.format(h))
        self.plotWidget.replacePlot(data=data,id=1)

    def reset(self):
        self.plotWidget.clearPlots()
        self.uiChange()

    #function to start Measuring again
    def startMeasure(self):
        #find the current Plot in the displayed tab
        currPlot = self.plotWidget
        if currPlot.stopped():
            #if its stopped start it
            if not currPlot.start(scatter=True):
                return False
            else:
                self.connectDevice()
        elif currPlot.paused():
            #if its paused start it
            currPlot.unpause()
        else:
            print("Plot neither stopped nor paused")
        self.startAction.setEnabled(False)
        self.stopAction.setEnabled(True)
        return True

    #function to stop Measuring
    def stopMeasure(self):
        #stop current plot
        self.plotWidget.stop("User Stopped")
        self.stopUi()

    #function to set the actions right
    def stopUi(self):
        self.startAction.setEnabled(True)
        self.stopAction.setEnabled(False)

    def uiChange(self):
        try:
            self.wellen=ast.literal_eval(self.settings.value("wellenText",wellenString))
        except Exception as e:
            print(e)
            self.wellen=[["Wellenlängeneinstellungen Falsch",0],["Bitte Einstellungen Resetten",0]]
        self.infoWidget = self.createInfoWidget()
        #create Main Widget
        self.mainWidget=QWidget()
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.plotWidget,10)
        self.mainLayout.addWidget(self.infoWidget,8)
        self.mainWidget.setLayout(self.mainLayout)
        #set Central Widget to Main Widget
        self.setCentralWidget(self.mainWidget)
        newfont = QFont("Times", self.settings.value("fontThickness",15,int))
        for l in self.labels:
            l.setFont(newfont)


    #function to save the data of the Current opened Plot
    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Dialog Title', '', filter='*.txt')[0]
        if fileName != "":
            #enshure it is a .txt file
            if fileName[len(fileName)-4:] == ".txt":
                fileName=fileName[:-4]
            np.savetxt(fileName +".txt",self.plotWidget.data[0])



    #function to load data to a new Plot
    def loadData(self):
        fileNames = QFileDialog.getOpenFileNames(self, 'Dialog Title', '', filter='*.txt')[0]
        for f in fileNames:
            if f != "":
                loadedData = np.loadtxt(f)
                self.plotWidget.replacePlot(data=loadedData,id=0,scatter=True)


    #function to open Settings
    def openSettings(self):
        try:
            if not self.settingsPage.isVisible():
                self.settingsPage.show()
            else:
                self.settingsPage.close()
        except Exception as e:
            print(e)

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        print("App called CloseEvent")
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes |
        #     QMessageBox.No, QMessageBox.No)
        #
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

        #close additional Windows
        self.lcdPage.close()
        self.settingsPage.close()

        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("mainPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("mainPagePos",self.pos())
        try:
            #Stop Connection and its Thread
            if self.plotWidget.connection.stopped():
                print("Connection already stopped")
            else:
                self.plotWidget.connection.stop("App CloseEvent")
            #Stop Plot and its Thread
            if self.plotWidget.stopped():
                print("Plot already stopped")
            else:
                self.plotWidget.stop("App CloseEvent")

            allstopped=True
            if self.plotWidget.connection.stopped() and self.plotWidget.stopped():
                allstopped=True
            else:
                allstopped=False
        except:
            allstopped=True
        #check if all are stopped
        if not allstopped:
            #ignore the event
            event.ignore()
            #try again
            self.close()
        else:
            event.accept()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":

    #create Main app
    app = QApplication(sys.argv)

    #create new Window (opens a new Window if not bound into another widget)
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
