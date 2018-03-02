#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys,os
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget,QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings,QSize,QPoint
import numpy as np

#custom imports
from Plotter import Plotter
from Pages import SettingsPage, LcdPage

#define mainPage
class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage,self).__init__()
        self.settings = QSettings('LMU-Muenchen', 'Voltmeter')
        self.settings.setValue("path",os.path.dirname(os.path.realpath(__file__)))
        #Array to save the Multiple Plots
        self.Plots=[]
        self.lcdPage=LcdPage()
        self.settingsPage=SettingsPage()
        self.initUI()


    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('mainPageSize', QSize(1000, 400)))
        self.move(self.settings.value('mainPagePos', QPoint(50, 50)))
        self.setWindowTitle('Voltmeter')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))

        #add Action to Close Programm
        self.exitAction = QAction(QIcon(resource_path('icons/ExitIcon.png')), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

        #add Action to add New Plot and start Measuring
        self.newMeasurementAction = QAction(QIcon(resource_path('icons/PlusIcon.png')), '&New', self)
        self.newMeasurementAction.setShortcut('Ctrl+N')
        self.newMeasurementAction.setStatusTip('Create New Measurement')
        self.newMeasurementAction.triggered.connect(self.newMeasure)

        #add Action to Display Current Value LCD Style
        self.lcdPageToogleAction = QAction(QIcon(resource_path('icons/NumberIcon.png')), '&LCD', self)
        self.lcdPageToogleAction.setShortcut('Ctrl+L')
        self.lcdPageToogleAction.setStatusTip('Display Current Value')
        self.lcdPageToogleAction.triggered.connect(self.toggleLcd)

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
        self.startAction.setStatusTip('Start Measurement')
        self.startAction.triggered.connect(self.startMeasure)
        self.startAction.setEnabled(False)

        #add Action to Pause Measuring
        self.pauseAction = QAction(QIcon(resource_path('icons/PauseIcon.png')), '&Pause', self)
        self.pauseAction.setShortcut('Ctrl+P')
        self.pauseAction.setStatusTip('Pause Measurement')
        self.pauseAction.triggered.connect(self.pauseMeasure)
        self.pauseAction.setEnabled(False)

        #add Action to Stop Measuring
        self.stopAction = QAction(QIcon(resource_path('icons/StopIcon.png')), '&Stop', self)
        self.stopAction.setShortcut('Ctrl+C')
        self.stopAction.setStatusTip('Stop Measurement')
        self.stopAction.triggered.connect(self.stopMeasure)
        self.stopAction.setEnabled(False)

        #create new MenuBar
        menubar = self.menuBar()
        #MenuBar entrys
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newMeasurementAction)
        fileMenu.addAction(self.saveDataAction)
        fileMenu.addAction(self.loadDataAction)
        fileMenu.addAction(self.openSettingsAction)
        fileMenu.addAction(self.exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(self.exitAction)
        toolbar.addAction(self.newMeasurementAction)
        toolbar.addAction(self.startAction)
        #toolbar.addAction(self.pauseAction)
        toolbar.addAction(self.stopAction)
        toolbar.addAction(self.lcdPageToogleAction)

        #create Main Widget
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabWidget.tabCloseRequested.connect(self.tabClosed)
        #set Central Widget to Main Widget
        self.setCentralWidget(self.tabWidget)

        #show MainWindow
        self.show()

    #function to start a new Measuring
    def newMeasure(self):
        self.newPlot(start=True)

    #function to make a new Plot
    def newPlot(self,start=False):
        #create new Plot
        plotWidget = Plotter(self)
        if start:
            if not plotWidget.start():
                return None

        self.Plots.append(plotWidget)
        #New Plot Tab
        plotTab = QWidget()
        plotLayout = QVBoxLayout()
        plotLayout.addWidget(plotWidget)
        plotTab.setLayout(plotLayout)
        self.tabWidget.addTab(plotTab, 'Plot ' + str(len(self.Plots)))
        return plotWidget

    #function to start Measuring again
    def startMeasure(self):
        #find the current Plot in the displayed tab
        currPlot = self.tabWidget.currentWidget().findChild(Plotter)
        if currPlot.stopped():
            #if its stopped start it
            if not currPlot.start():
                return False
        elif currPlot.paused():
            #if its paused start it
            currPlot.unpause()
        else:
            print("Plot neither stopped nor paused")
        self.startAction.setEnabled(False)
        self.pauseAction.setEnabled(True)
        self.stopAction.setEnabled(True)

    #function to pause Measuring
    def pauseMeasure(self):
        self.tabWidget.currentWidget().findChild(Plotter).pause("User Paused")
        self.startAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(True)

    #function to stop Measuring
    def stopMeasure(self):
        #stop current plot
        self.tabWidget.currentWidget().findChild(Plotter).stop("User Stopped")
        self.stopUi()

    def stopUi(self):
        #change Actions
        self.startAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(False)

    #function to Handle if User Changes the Tab
    def tabChanged(self):
        currWidget=self.tabWidget.currentWidget()
        if not currWidget==None:
            currPlot=currWidget.findChild(Plotter)
            #disconnect all Signals from all Plots (saves ressources), so they don't update their plot when not shown
            for p in self.Plots:
                p.disconnectAll()
            #connect the current Plot (live Updates)
            currPlot.connect()
            #connect the Lcd to the current Plot
            self.lcdPage.connectTo(currPlot)
            #fix Actions
            if currPlot.stopped():
                self.startAction.setEnabled(True)
                self.pauseAction.setEnabled(False)
                self.stopAction.setEnabled(False)
            elif currPlot.paused():
                self.startAction.setEnabled(True)
                self.pauseAction.setEnabled(False)
                self.stopAction.setEnabled(True)
            else:
                self.startAction.setEnabled(False)
                self.pauseAction.setEnabled(True)
                self.stopAction.setEnabled(True)
        else:
            self.startAction.setEnabled(False)
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.lcdPage.display(0.000)

    #function to handle Tab Close
    def tabClosed(self,tab_index):
        self.tabWidget.widget(tab_index).findChild(Plotter).stop("Tab Closed")
        self.tabWidget.removeTab(tab_index)

    #function to save the data of the Current opened Plot
    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Dialog Title', '', filter='*.txt')[0]
        if fileName != "":
            #enshure it is a .txt file
            if fileName[len(fileName)-4:] == ".txt":
                fileName=fileName[:-4]
            for i,d in enumerate(self.tabWidget.currentWidget().findChild(Plotter).data):
                np.savetxt(fileName + "_Graph" + str(i+1)+".txt",d)



    #function to load data to a new Plot
    def loadData(self):
        fileNames = QFileDialog.getOpenFileNames(self, 'Dialog Title', '', filter='*.txt')[0]
        plotWidget = self.newPlot()
        for f in fileNames:
            if f != "":
                loadedData = np.loadtxt(f)
                plotWidget.newPlot(loadedData)


    #function to toggle Lcd on and off
    def toggleLcd(self):
        if not self.lcdPage.isVisible():
            self.lcdPage.display(0.000)
            self.lcdPage.show()
        else:
            self.lcdPage.close()

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
            for p in self.Plots:
                #Stop Connection and its Thread
                if p.connection.stopped():
                    print("Connection already stopped")
                else:
                    p.connection.stop("App CloseEvent")
                #Stop Plot and its Thread
                if p.stopped():
                    print("Plot already stopped")
                else:
                    p.stop("App CloseEvent")

            allstopped=True
            for p in self.Plots:
                if p.connection.stopped() and p.stopped():
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
