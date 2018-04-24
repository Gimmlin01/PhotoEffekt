# LMU Voltmeter
Ein Programm das zur Live Darstellung einer Messung mit einem Multimeter genutzt wird.

## Programm Aufbau
Programm Besteht aus mehreren Teilen:

### main.py:
  Verantwortlich für die GUI(PyQT5).
  MainPage in der die verschiedenen Aktionen und das TabWidget sitzt in dem die Plots dargestellt werden.

### Pages.py:
Verwaltet die verschiedenen Seiten die das Programm benötigt

#### Seiten:
* LcdPage: Seite in der der Aktuelle Messwert angezeigt werden kann.
* SettingsPage: Seite für das Einstellen der Schriftgröße/Strichdicke, ...

### Connection.py:
  Dieser Programmteil is für die verständigung zwischen Programm <-> Gerät zuständig
  Er besteht aus einem Thread der im Hintergrund läuft und das ausgewählte Gerät immer wieder "ausliest" indem er jede ankommende Messung sofort ausliest parst und in eine OUT Schlange schiebt die später vom Plotter ausgelesen wird.

### Plotter.py:
  Plotter ist eine Klasse die ein pyqtgraph.PlotWidget ergänzt:
  Sie besitzt die nötigen variablen um die daten der verschiedenen plots zu speichern
  Ebenso einen PlotThread in dem die OUT Schlange der Connection ausgelesen und in den neuesten Plot geschrieben wird.

### devices/:
* Dummy.py Ein Beispiel Gerät was die nötigsten Funktionalitäten besitzt.
* UT61C.py Die UT61C klasse die kommunikation mit dem Gerät ermöglicht.


## GUI aufbau:
```
MainPage:
  toolbar
  menuBar
  tabWidget:
    Tab:
      Plotter:
        Plots:
          Connection:
            Device  
```

## Erklärung der UT61C.py:
Der Hersteller UNI-Trend hat sich dazu entschieden das Multimeter mit einem USB-Gerät auszustatten das sich als HID meldet. Dies hat den Vorteil das kein spezieller Treiber benötigt wird. Um nun die Daten auszulesen muss das python modul hid folgend benutzt werden:

```
  dev = hid.device()
  dev.open(6790,57352) #gerät mit VendorID,ProduktID (UT61C) öffnen
  buf = [0x05,0x60, 0x09, 0x00, 0x60, 0x03] #sequenz zum starten der Übertragung
  dev.send_feature_report(buf) #sequenz senden
```
die buf sequenz musste mit einem USB-Sniffer ausgelesen zwischen UT61C und Originalprogramm.
Die Daten kommen dann in vereinzelt in Tupeln wobei der erste Eintrag ein Konrollbyte (0xf1=ok 0xff=nok) im 2. das InfoByte und müssen in 14Byte Nachrichten unterteilt werden 	


## Erklärung pyqt signal:
  Eine art Queue die aber dynamischer ist. Man kann an ein solches signal eine Funktion connecten die dann,
  falls das Signal emmitiert wird ausgeführt wird.


## Hinzufügen neuer Geräte:
  Wenn man in den Einstellungen die Devices entpackt hat sollte sich in dem Ordner in dem das Programm ausgeführt wird ein devices Ordner befinden.
  In disem Ordner befindet sich eine Dummy.py diese beinhaltet alle wichtigen Funkionen:

### wichtigste Funkionen:
* measure(): Diese Funktion muss eine Tupel mit (y,x,"x AchsenBeschriftung","y AchsenBeschriftung") zurückgeben
* isOpen(): Diese Funkion gibt True zurück falls das Gerät bereit ist um Daten zu übertragen.
* warningText: Eine Tupel mit den Texten ("Text1","Text2","Detail") für die Warnung falls das gerät nicht bereit ist.
  Nun diese Dummy datei in eine "meinNeuesGerät.py" und die Klasse in der Datei mit dem Namen "meinNeuesGerät" umbenennen und die funktionen nach belieben abändern

## Kompilieren des Scriptes mit pyinstaller:
Falls die exe neu kompiliert werden soll bitte nicht vergessen neue geräte in der build.spec bei a=Analysis["Gerät1","Gerät2"] einzutragen um zusätzliche Imports zu sichern. Dann einfach die build.bat ausführen und die verschiedenen abhänigkeiten über pip installieren.



All Icons made by http://www.flaticon.com/authors/freepik from www.flaticon.com

author: Michael Auer
