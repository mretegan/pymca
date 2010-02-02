#/*##########################################################################
# Copyright (C) 2004-2010 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem for you.
#############################################################################*/
import sys
import SimpleFitControlWidget
qt = SimpleFitControlWidget.qt
HorizontalSpacer = SimpleFitControlWidget.HorizontalSpacer
VerticalSpacer = SimpleFitControlWidget.VerticalSpacer
import ConfigDict
import PyMca_Icons as Icons
import os.path
import PyMcaDirs

#strip background handling
import StripBackgroundWidget
SCANWINDOW = StripBackgroundWidget.SCANWINDOW
import numpy

import Parameters
DEBUG = 1

class SimpleFitConfigurationGUI(qt.QDialog):
    def __init__(self, parent = None, fit=None):
        qt.QDialog.__init__(self, parent)
        self.setWindowTitle("PyMca - Simple Fit Configuration")
        self.setWindowIcon(qt.QIcon(qt.QPixmap(Icons.IconDict["gioconda16"])))
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setMargin(2)
        self.mainLayout.setSpacing(2)
        if 0:
            self.fitControlWidget = SimpleFitControlWidget.SimpleFitControlWidget(self)
            self.mainLayout.addWidget(self.fitControlWidget)
            self.connect(self.fitControlWidget,
                         qt.SIGNAL("FitControlSignal"),
                         self._fitControlSlot)
            self._stripDialog = None
        else:            
            self.tabWidget = qt.QTabWidget(self)
            self.fitControlWidget = SimpleFitControlWidget.SimpleFitControlWidget(self)
            self.connect(self.fitControlWidget,
                         qt.SIGNAL("FitControlSignal"),
                         self._fitControlSlot)
            self.tabWidget.insertTab(0, self.fitControlWidget, "FIT")
            self.fitFunctionWidgetStack = qt.QWidget(self)
            self.fitFunctionWidgetStack.mainLayout = qt.QStackedLayout(self.fitFunctionWidgetStack)
            self.fitFunctionWidgetStack.mainLayout.setMargin(0)
            self.fitFunctionWidgetStack.mainLayout.setSpacing(0)            
            self.tabWidget.insertTab(1, self.fitFunctionWidgetStack, "FUNCTION")
            self.backgroundWidgetStack = qt.QWidget(self)
            self.backgroundWidgetStack.mainLayout = qt.QStackedLayout(self.backgroundWidgetStack)
            self.backgroundWidgetStack.mainLayout.setMargin(0)
            self.backgroundWidgetStack.mainLayout.setSpacing(0)            
            self.tabWidget.insertTab(2, self.backgroundWidgetStack, "BACKGROUND")
            self.mainLayout.addWidget(self.tabWidget)
            self._stripDialog = None
        self.buildAndConnectActions()
        self.mainLayout.addWidget(VerticalSpacer(self))
        self._fitFunctionWidgets = {}
        self._backgroundWidgets = {}
        self.setSimpleFitInstance(fit)
        #input output directory
        self.initDir = None

    def _fitControlSlot(self, ddict):
        if DEBUG:
            print "FitControlSignal", ddict
        event = ddict['event']
        if event == "stripSetupCalled":
            if self._stripDialog is None:
                self._stripDialog = StripBackgroundWidget.StripBackgroundDialog()
                self._stripDialog.setWindowIcon(qt.QIcon(\
                                    qt.QPixmap(Icons.IconDict["gioconda16"])))
            pars = self.__getConfiguration("FIT")
            if self.simpleFitInstance is None:
                return
            xmin = pars['xmin']
            xmax = pars['xmax']
            idx = (self.simpleFitInstance._x0 >= xmin) & (self.simpleFitInstance._x0 <= xmax)
            x = self.simpleFitInstance._x0[idx] * 1
            y = self.simpleFitInstance._y0[idx] * 1
            self._stripDialog.setParameters(pars)
            self._stripDialog.setData(x, y)
            ret = self._stripDialog.exec_()
            if not ret:
                return
            pars = self._stripDialog.getParameters()
            self.fitControlWidget.setConfiguration(pars)
        if event == "fitFunctionChanged":
            functionName = ddict['fit_function']
            if functionName in [None, "None", "NONE"]:
                functionName = "None"
                instance = self._fitFunctionWidgets.get(functionName, None)
                if instance is None:
                    instance = qt.QWidget(self.fitFunctionWidgetStack)
                    self.fitFunctionWidgetStack.mainLayout.addWidget(instance)
                    self._fitFunctionWidgets[functionName] = instance
                self.fitFunctionWidgetStack.mainLayout.setCurrentWidget(instance)
                return
            fun = self.simpleFitInstance._fitConfiguration['functions'][functionName]
            instance = self._fitFunctionWidgets.get(functionName, None)
            if instance is None:
                widget = fun.get('widget', None)
                if widget is None:
                    instance = self._buildDefaultWidget(functionName, background=False)
                self._fitFunctionWidgets[functionName] = instance
            self.fitFunctionWidgetStack.mainLayout.setCurrentWidget(instance)
        if event == "backgroundFunctionChanged":
            functionName = ddict['background_function']
            if functionName in [None, "None", "NONE"]:
                functionName = "None"
                instance = self._backgroundWidgets.get(functionName, None)
                if instance is None:
                    instance = qt.QWidget(self.backgroundWidgetStack)
                    self.backgroundWidgetStack.mainLayout.addWidget(instance)
                    self._backgroundWidgets[functionName] = instance
                self.backgroundWidgetStack.mainLayout.setCurrentWidget(instance)
                return
            fun = self.simpleFitInstance._fitConfiguration['functions'][functionName]
            instance = self._backgroundWidgets.get(functionName, None)
            if instance is None:
                widget = fun.get('widget', None)
                if widget is None:
                    instance = self._buildDefaultWidget(functionName, background=True)
                self._backgroundWidgets[functionName] = instance
            self.backgroundWidgetStack.mainLayout.setCurrentWidget(instance)

    def _buildDefaultWidget(self, functionName, background=False):
        parameters = self.simpleFitInstance._fitConfiguration['functions'][functionName]['parameters']
        xmin = self.simpleFitInstance._x.min()
        xmax = self.simpleFitInstance._x.max()
        paramlist = []
        if background:
            group = 0
        else:
            group = 1
        for i in range(len(parameters)):
            pname = parameters[i]
            paramlist.append({'name':pname+"_1",
                              'estimation':0,
                              'group':group,
                              'code':'FREE',
                              'cons1':0,
                              'cons2':0,
                              'fitresult':0.0,
                              'sigma':0.0,
                              'xmin':xmin,
                              'xmax':xmax})
        if background:
            widget = Parameters.Parameters(self.backgroundWidgetStack)
            widget.fillTableFromFit(paramlist)
            self.backgroundWidgetStack.mainLayout.addWidget(widget)
        else:
            widget = Parameters.Parameters(self.fitFunctionWidgetStack)
            widget.fillTableFromFit(paramlist)
            self.fitFunctionWidgetStack.mainLayout.addWidget(widget)
        return widget

    def buildAndConnectActions(self):
        buts= qt.QGroupBox(self)
        buts.layout = qt.QHBoxLayout(buts)
        load= qt.QPushButton(buts)
        load.setAutoDefault(False)
        load.setText("Load")
        save= qt.QPushButton(buts)
        save.setAutoDefault(False)
        save.setText("Save")
        reject= qt.QPushButton(buts)
        reject.setAutoDefault(False)
        reject.setText("Cancel")
        accept= qt.QPushButton(buts)
        accept.setAutoDefault(False)
        accept.setText("OK")
        buts.layout.addWidget(load)
        buts.layout.addWidget(save)
        buts.layout.addWidget(reject)
        buts.layout.addWidget(accept)
        self.mainLayout.addWidget(buts)

        self.connect(load, qt.SIGNAL("clicked()"), self.load)
        self.connect(save, qt.SIGNAL("clicked()"), self.save)
        self.connect(reject, qt.SIGNAL("clicked()"), self.reject)
        self.connect(accept, qt.SIGNAL("clicked()"), self.accept)

    def setSimpleFitInstance(self, fitInstance):
        self.simpleFitInstance = fitInstance
        if self.simpleFitInstance is not None:
            self.setConfiguration(self.simpleFitInstance.getConfiguration())

    def setConfiguration(self, ddict):
        if ddict.has_key('fit'):
            self.fitControlWidget.setConfiguration(ddict['fit'])
            fitFunction = ddict['fit']['fit_function']
            background = ddict['fit']['background_function']
            if fitFunction not in self._fitFunctionWidgets.keys():
                self._fitControlSlot({'event':'fitFunctionChanged',
                                      'fit_function':fitFunction})
            if background not in self._backgroundWidgets.keys():
                self._fitControlSlot({'event':'backgroundFunctionChanged',
                                      'background_function':background})
            #fit function
            fname = ddict['fit']['fit_function']
            widget = self._fitFunctionWidgets[fname]
            if fname not in [None, "None", "NONE"]:
                if ddict.has_key(fname):
                    widget.setConfiguration(ddict[fname])
            
            #background function
            fname = ddict['fit']['background_function']
            widget = self._backgroundWidgets[fname]
            if fname not in [None, "None", "NONE"]:
                if ddict.has_key(fname):
                    widget.setConfiguration(ddict[fname])

    def getConfiguration(self):
        ddict = {}
        for name in ['fit']:
            ddict[name] = self.__getConfiguration(name)

        #fit function
        fname = ddict['fit']['fit_function']
        widget = self._fitFunctionWidgets[fname]
        if fname not in [None, "None", "NONE"]:
            ddict[fname] = widget.getConfiguration()
                        

        #background function
        fname = ddict['fit']['background_function']
        widget = self._backgroundWidgets[fname]
        if fname not in [None, "None", "NONE"]:
            ddict[fname] = widget.getConfiguration()
        return ddict

    def __getConfiguration(self, name):
        if name in ['fit', 'FIT']:
            return self.fitControlWidget.getConfiguration()

    def load(self):
        if PyMcaDirs.nativeFileDialogs:
            filedialog = qt.QFileDialog(self)
            filedialog.setFileMode(filedialog.ExistingFiles)
            filedialog.setWindowIcon(qt.QIcon(qt.QPixmap(Icons.IconDict["gioconda16"])))
            initdir = os.path.curdir
            if self.initDir is not None:
                if os.path.isdir(self.initDir):
                    initdir = self.initDir
            filename = filedialog.getOpenFileName(
                        self,
                        "Choose fit configuration file",
                        initdir,
                        "Fit configuration files (*.cfg)\nAll Files (*)")
            filename = str(filename)
            if len(filename):
                self.loadConfiguration(filename)
                self.initDir = os.path.dirname(filename)
        else:
            filedialog = qt.QFileDialog(self)
            filedialog.setFileMode(filedialog.ExistingFiles)
            filedialog.setWindowIcon(qt.QIcon(qt.QPixmap(Icons.IconDict["gioconda16"])))
            initdir = os.path.curdir
            if self.initDir is not None:
                if os.path.isdir(self.initDir):
                    initdir = self.initDir
            filename = filedialog.getOpenFileName(
                        self,
                        "Choose fit configuration file",
                        initdir,
                        "Fit configuration files (*.cfg)\nAll Files (*)")
            filename = str(filename)
            if len(filename):
                self.loadConfiguration(filename)
                self.initDir = os.path.dirname(filename)
        
    def save(self):
        if self.initDir is None:
            self.initDir = PyMcaDirs.outputDir
        if PyMcaDirs.nativeFileDialogs:
            filedialog = qt.QFileDialog(self)
            filedialog.setFileMode(filedialog.AnyFile)
            filedialog.setWindowIcon(qt.QIcon(qt.QPixmap(Icons.IconDict["gioconda16"])))
            initdir = os.path.curdir
            if self.initDir is not None:
                if os.path.isdir(self.initDir):
                    initdir = self.initDir
            filename = filedialog.getSaveFileName(
                        self,
                        "Enter output fit configuration file",
                        initdir,
                        "Fit configuration files (*.cfg)\nAll Files (*)")
            filename = str(filename)
            if len(filename):
                if len(filename) < 4:
                    filename = filename+".cfg"
                elif filename[-4:] != ".cfg":
                    filename = filename+".cfg"
                self.saveConfiguration(filename)
                self.initDir = os.path.dirname(filename)
        else:
            filedialog = qt.QFileDialog(self)
            filedialog.setFileMode(filedialog.AnyFile)
            filedialog.setWindowIcon(qt.QIcon(qt.QPixmap(Icons.IconDict["gioconda16"])))
            initdir = os.path.curdir
            if self.initDir is not None:
                if os.path.isdir(self.initDir):
                    initdir = self.initDir
            filename = filedialog.getSaveFileName(
                        self,
                        "Enter output fit configuration file",
                        initdir,
                        "Fit configuration files (*.cfg)\nAll Files (*)")
            filename = str(filename)
            if len(filename):
                if len(filename) < 4:
                    filename = filename+".cfg"
                elif filename[-4:] != ".cfg":
                    filename = filename+".cfg"
                self.saveConfiguration(filename)
                self.initDir = os.path.dirname(filename)
                PyMcaDirs.outputDir = os.path.dirname(filename)

    def loadConfiguration(self, filename):
        cfg= ConfigDict.ConfigDict()
        if DEBUG:
            cfg.read(filename)
            self.initDir = os.path.dirname(filename)
            self.setConfiguration(cfg)
        else:
            try:
                cfg.read(filename)
                self.initDir = os.path.dirname(filename)
                self.setConfiguration(cfg)
            except:
                qt.QMessageBox.critical(self, "Load Parameters",
                    "ERROR while loading parameters from\n%s"%filename, 
                    qt.QMessageBox.Ok,
                    qt.QMessageBox.NoButton,
                    qt.QMessageBox.NoButton)
        
    def saveConfiguration(self, filename):
        cfg= ConfigDict.ConfigDict(self.getConfiguration())
        if DEBUG:
            cfg.write(filename)
            self.initDir = os.path.dirname(filename)
        else:
            try:
                cfg.write(filename)
                self.initDir = os.path.dirname(filename)
            except:
                qt.QMessageBox.critical(self, "Save Parameters", 
                    "ERROR while saving parameters to\n%s"%filename,
                    qt.QMessageBox.Ok, qt.QMessageBox.NoButton, qt.QMessageBox.NoButton)
        

def test():
    app = qt.QApplication(sys.argv)
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), app.quit)
    wid = SimpleFitConfigurationGUI()
    ddict = {}
    ddict['fit'] = {}
    ddict['fit']['use_limits'] = 1
    ddict['fit']['xmin'] = 1
    ddict['fit']['xmax'] = 1024
    wid.setConfiguration(ddict)
    wid.exec_()
    print wid.getConfiguration()
    sys.exit()

if __name__=="__main__":
    DEBUG = 1
    test()
