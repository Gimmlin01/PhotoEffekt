from PyQt5.QtWidgets import QWidget,QHBoxLayout, QVBoxLayout,QGroupBox,QRadioButton,QGridLayout,QPushButton,QCheckBox,QSpinBox,QLabel,QColorDialog,QLCDNumber,QGridLayout,QLineEdit
from PyQt5.QtGui import QIcon,QColor,QFont
from PyQt5.QtCore import QSettings,QSize,QPoint,Signal,Qt
from functools import partial
import sys,os

defaultColors=[
QColor(5, 252, 82, 255),QColor(8, 248, 253, 255),QColor(253, 7, 241, 255),QColor(75, 0, 255, 255),
QColor(255, 0, 0, 255),QColor(239, 41, 41, 255),QColor(138, 226, 52, 255),QColor(114, 159, 207, 255),
QColor(173, 127, 168, 255),QColor(136, 138, 133, 255),QColor(164, 0, 0, 255),QColor(206, 92, 0, 255),
QColor(196, 160, 0, 255),QColor(78, 154, 6, 255),QColor(32, 74, 135, 255),QColor(92, 53, 102, 255)
]

wellenString='[["585nm",585e-9],["581nm",581e-9],["580nm",580e-9],["546nm",546e-9],["492nm",492e-9],["439nm",439e-9],["400nm",400e-9]]'


prefix = {-24:"y",-21:"z",-18:"a",-15:"f",-12:"p",-9:"n",-6:"u",-3:"m",-2:"c",-1:"d",0:"",
                3:"k",6:"M",9:"G",12:"T",15:"P",18:"E",21:"Z",24:"Y"}

#function witch maps relative_path to absolute path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

keymap = {}
for key, value in vars(Qt).items():
    if isinstance(value, Qt.Key):
        keymap[value] = key.partition('_')[2]
keymap[196]="Ä"
keymap[214]="Ö"
keymap[220]="Ü"


#class for the Settings Dialog
class SettingsPage(QWidget):

    #Signal wich emits on an UI Settings change
    uiChange = Signal(object)

    def __init__(self):
        super(SettingsPage,self).__init__()
        self.settings = QSettings("LMU-Muenchen", 'PhotoEffekt')
        self.resize(self.settings.value('settingsPageSize', QSize(250, 250)))
        self.move(self.settings.value('settingsPagePos', QPoint(1100, 50)))
        self.devs=[]
        self.changeingKeys=False
        self.initDevices()
        self.initUI()

    def keyPressEvent(self, event):
        if self.changeingKeys:
            keys=self.settings.value("measureKeys", type=int)
            key=event.key()
            if not key in keys:
                keys.append(event.key())
                self.settings.setValue("measureKeys",keys)
                text=""
                for k in keys:
                    text+=keymap.get(k,"NotAKey")+","
                self.keyLabel.setText(text[:-1])

    #function to scan all devices in devicePath
    def initDevices(self):
        self.devs=[]
        try:
            devs=os.listdir(self.settings.value("devicePath",resource_path("bundled")))
            for d in devs:
                if d[-3:] == ".py" and d[:2] != "__":
                    print(d+" found!")
                    self.devs.append(d[:-3])
        except:
            print(self.settings.value("devicePath","bundled") +" folder not found")
            devs=None

    #function to show the Page
    def show(self):
        QWidget().setLayout(self.grid)
        self.initDevices()
        self.initUI()
        super(SettingsPage, self).show()

    #function to initiate UI
    def initUI(self):
        #cosmeticals
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.grid = QGridLayout()

        #Create Menu to Choose Connections
        self.conGroupBox=QGroupBox("Devices")
        conVbox = QVBoxLayout()
        activeConnection = self.settings.value("connection","Dummy")
        for d in self.devs:
            radio = QRadioButton(d)
            radio.toggled.connect(partial(self.setConnection,radio))
            conVbox.addWidget(radio)
            if (d==activeConnection):
                radio.setChecked(True)
        conVbox.addStretch(1)

        #Create Possibility to extract devices
        if not self.settings.value("devicePath",False):
            extractButton = QPushButton("extract Devices")
            extractButton.clicked.connect(lambda:self.extract())
            conVbox.addWidget(extractButton)

        self.conGroupBox.setLayout(conVbox)
        self.grid.addWidget(self.conGroupBox)



        self.keyBox=QGroupBox("Key/s for measuring")
        keyVbox = QVBoxLayout()
        keys=self.settings.value("measureKeys",[16777272], type=int)
        text=""
        for k in keys:
            text+=keymap.get(k,"NotAKey")+","
        self.keyLabel=QLabel(text[:-1])
        keyVbox.addWidget(self.keyLabel)

        self.keyButton = QPushButton("Change Key/s")
        self.keyButton.clicked.connect(lambda:self.changeKey())
        keyVbox.addWidget(self.keyButton)
        self.keyBox.setLayout(keyVbox)
        self.grid.addWidget(self.keyBox)




        self.wellenGroupBox=QGroupBox("Wavelengths")
        wellenVbox = QVBoxLayout()
        self.wellenEdit=QLineEdit()
        self.wellenEdit.setText(self.settings.value("wellenText",wellenString))
        self.wellenEdit.returnPressed.connect(self.changeWellenText)
        wellenVbox.addWidget(self.wellenEdit)
        self.wellenGroupBox.setLayout(wellenVbox)
        self.grid.addWidget(self.wellenGroupBox)

        #Create Menu to set Appearence
        self.uiGroupBox=QGroupBox("UI")
        #create Axis Size chooser
        uiVbox = QVBoxLayout()
        axisThickInp=QSpinBox()
        axisThickInp.setPrefix("Axis Lable: ")
        axisThickInp.setSuffix("px")
        lineThick=self.settings.value("axisThickness", 20,int)
        axisThickInp.setValue(lineThick)
        axisThickInp.valueChanged.connect(self.changeAxisThickness)
        uiVbox.addWidget(axisThickInp)

        #create Tick Size chooser
        tickThickInp=QSpinBox()
        tickThickInp.setPrefix("Tick Lable: ")
        tickThickInp.setSuffix("px")
        lineThick=self.settings.value("tickThickness", 15,int)
        tickThickInp.setValue(lineThick)
        tickThickInp.valueChanged.connect(self.changeTickThickness)
        uiVbox.addWidget(tickThickInp)

        #create Font Size chooser
        fontThickInp=QSpinBox()
        fontThickInp.setPrefix("Font Size: ")
        fontThickInp.setSuffix("px")
        lineThick=self.settings.value("fontThickness", 15,int)
        fontThickInp.setValue(lineThick)
        fontThickInp.valueChanged.connect(self.changeFontThickness)
        uiVbox.addWidget(fontThickInp)

        self.uiGroupBox.setLayout(uiVbox)
        self.grid.addWidget(self.uiGroupBox)

        #Create Menu to Choose Plot appearing
        self.plotGroupBox=QGroupBox("Plot")
        plotVbox = QVBoxLayout()
        thickInp=QSpinBox()
        thickInp.setPrefix("Line Thickness: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("lineThickness", 3,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changeLineThickness)
        plotVbox.addWidget(thickInp)
        thickInp=QSpinBox()
        thickInp.setPrefix("Point Thickness: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("pointThickness", 8,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changePointThickness)
        plotVbox.addWidget(thickInp)
        colors=self.settings.value("colors",defaultColors,QColor)
        plotHbox = QHBoxLayout()
        for c in range(16):
            cl=QPushButton()
            cl.setFixedSize(20,20)
            p = cl.palette()
            p.setColor(cl.backgroundRole(), colors[c])
            cl.setPalette(p)
            cl.setAutoFillBackground(True)
            plotHbox.addWidget(cl)
            cl.setFlat(True)
            cl.clicked.connect(partial(self.colorPicker,c))
            if (c==7):
                plotHbox.addStretch(1)
                plotVbox.addLayout(plotHbox)
                plotHbox = QHBoxLayout()
        plotHbox.addStretch(1)
        plotVbox.addLayout(plotHbox)
        plotVbox.addStretch(1)
        self.plotGroupBox.setLayout(plotVbox)
        self.grid.addWidget(self.plotGroupBox)

        #Create Menu to Choose Size/Pos saving
        self.exGroupBox=QGroupBox("Save on Exit")
        exVbox = QVBoxLayout()
        for s in ["Size","Position"]:
            cb = QCheckBox(s)
            cb.toggled.connect(partial(self.toggled,cb))
            exVbox.addWidget(cb)
            cb.setChecked(self.settings.value(s,True,bool))
        exVbox.addStretch(1)
        self.exGroupBox.setLayout(exVbox)
        self.grid.addWidget(self.exGroupBox)

        #Create Possibility to reset Settings
        settingsResetButton = QPushButton("Reset Settings")
        settingsResetButton.clicked.connect(lambda:self.resetSettings())
        self.grid.addWidget(settingsResetButton)

        #Create Possibility to reset Settings
        settingsCloseButton = QPushButton("Close Settings")
        settingsCloseButton.clicked.connect(lambda:self.close())
        self.grid.addWidget(settingsCloseButton)

        #set Grid as Layout
        self.setLayout(self.grid)

    #function to Pick color for color[nr]
    def colorPicker(self,nr):
        colors=self.settings.value("colors",defaultColors,QColor)
        colors[nr] = QColorDialog.getColor(colors[nr])
        self.settings.setValue("colors",colors)
        self.uiChange.emit(None)
        self.show()

    #function to set connection to wich
    def setConnection(self,wich):
        if (wich.isChecked()):
            self.settings.setValue('connection', wich.text())

    #function to set settings to checkbutton state
    def toggled(self,wich):
        self.settings.setValue(wich.text(), wich.isChecked())

    #function to reset Settings
    def resetSettings(self):
        self.settings.clear()
        self.uiChange.emit(None)
        self.show()

    #function to change Axis Thickness
    def changeAxisThickness(self,thick):
        self.settings.setValue("axisThickness",thick)
        self.uiChange.emit(None)

    #function to change Tick Thickness
    def changeTickThickness(self,thick):
        self.settings.setValue("tickThickness",thick)
        self.uiChange.emit(None)

    #function to change Font Thickness
    def changeFontThickness(self,thick):
        self.settings.setValue("fontThickness",thick)
        self.uiChange.emit(None)

    #function to change Line Thickess
    def changeLineThickness(self,thick):
        self.settings.setValue("lineThickness",thick)
        self.uiChange.emit(None)

    def changePointThickness(self,thick):
        self.settings.setValue("pointThickness",thick)
        self.uiChange.emit(None)

    def changeWellenText(self):
        self.settings.setValue("wellenText", self.wellenEdit.text())
        self.uiChange.emit(None)

    def changeKey(self):
        if not self.changeingKeys:
            self.startChangeKey()
        else:
            self.stopChangeKey()

    def startChangeKey(self):
        self.keyButton.setText("Finish recording")
        self.grabKeyboard()
        self.keyLabel.setText("")
        self.settings.setValue("measureKeys", [])
        self.changeingKeys=True


    def stopChangeKey(self):
        self.keyButton.setText("Change Key/s")
        self.releaseKeyboard()
        self.changeingKeys=False

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        self.releaseKeyboard()
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("settingsPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("settingsPagePos",self.pos())

    # function wich handles the extraction and copy the bundled devices!
    def extract(self):
        self.settings.setValue("devicePath","devices")
        print("extracting")
        try:
            folder = self.settings.value("path","") + "\devices"
            bundlefolder=resource_path("bundled")
            devs=os.listdir(bundlefolder)
            try:
                os.mkdir(folder)
            except:
                pass
            import shutil
            for d in devs:
                if not os.path.exists(folder+"/"+d):
                    shutil.copy2(resource_path("bundled/"+d), folder)
                    print(d+" extracted!")

        except OSError as e:
            print("extraction failed:" +str(e))

        self.show()

#class for the LCD Page witch shows the Current Value
class LcdPage(QWidget):
    def __init__(self):
        super(LcdPage,self).__init__()
        self.settings = QSettings('LMU-Muenchen', 'PhotoEffekt')
        self.resizeEvent = self.onResize
        self.initUI()

    #function to adapt to resized window size
    def onResize(self,event):
        self.font.setPixelSize(self.height()*0.4)
        self.text.setFont(self.font)

    #function to initiate UI
    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('lcdPageSize', QSize(200, 350)))
        self.move(self.settings.value('lcdPagePos', QPoint(1100, 50)))
        self.setWindowTitle('LCD Display')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        #add the Layout
        grid=QGridLayout()
        self.lcd=QLCDNumber()
        self.lcd.setDigitCount(5)
        self.text=QLabel("unit")
        self.font=QFont()
        self.font.setPixelSize(self.height()*0.4)
        self.text.setFont(self.font)
        grid.addWidget(self.lcd,0,0)
        grid.addWidget(self.text,0,1)
        grid.setColumnStretch(0,5)
        grid.setColumnStretch(1,1)
        self.setLayout(grid)

    #function to display the given number on its lcd
    def display(self,what):
        self.lcd.display(what)

    #connect the updateLcd function to the newData signal of the given plot
    def connectTo(self,plot):
        plot.newData.connect(self.updateLcd)

    #update displayed value
    def updateLcd(self,inpData):
        number,prefix = self.parseNumber(inpData[1])
        self.display(round(number,2))
        self.lcd.setDigitCount(len(str(round(number,2))))
        self.text.setText(str(prefix) + str(inpData[3][1]))

    #function to parse the number n to write it like kV or mV
    def parseNumber(self,n,s=0):
        nt=abs(n)
        if nt == 0:
            return (0,prefix[0])
        elif nt >1000:
            return self.parseNumber(n/1000,s+3)
        elif nt<1:
            if s > -3:
                return self.parseNumber(n*10,s-1)
            elif s<-24:
                return (0,prefix[0])
            else:
                return self.parseNumber(n*1000,s-3)
        elif nt<10:
                return (round(n,2),prefix[s])
        elif nt<100:
            return (round(n,1),prefix[s])
        else:
            return (round(n,0),prefix[s])

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("lcdPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("lcdPagePos",self.pos())
