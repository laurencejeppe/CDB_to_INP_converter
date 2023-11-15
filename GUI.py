# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:29:14 2023

@author: ljr1e21
"""

import fnmatch as fnm
import math
import sys
from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QAction, 
                             QFileDialog, QVBoxLayout, QComboBox, QPushButton,
                             QHBoxLayout)

class cdb_inp_GUI(QMainWindow):
    def __init__(self):
        super(cdb_inp_GUI,self).__init__()
        self.setWindowTitle("CAD Converter")
        self.initUI()
        
        self.cdb_file = None
        self.inp_file = None
    
    def initUI(self):
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.createActions()
        self.createMenus()
        
        self.layout = QVBoxLayout()
        
        self.open_cdb_btn = QPushButton("Open CDB")
        
        self.layout.addWidget(self.open_cdb_btn)
        
        self.open_cdb_btn.clicked.connect(self.chooseOpenFile)
        
        self.hlayout = QHBoxLayout()
        self.hlayout.addStretch()
        
        self.element_type_CB = QComboBox()
        self.element_type_CB.addItems(['S4','C3D8'])
        self.setStyleSheet("QComboBox {text-align: center;}")
        
        self.hlayout.addWidget(self.element_type_CB)
        self.hlayout.addStretch()
        
        self.layout.addLayout(self.hlayout)
        
        self.save_inp_btn = QPushButton("Save INP")
        
        self.layout.addWidget(self.save_inp_btn)
        
        self.save_inp_btn.clicked.connect(self.chooseSaveFile)
        
        self.mainWidget.setLayout(self.layout)
        self.resize(200,200)
        self.show()
        
    def chooseOpenFile(self):
        """
        Handles importing and reading of cdb

        """
        fname = QFileDialog.getOpenFileName(self, 'Open file', directory='/', filter="ANSYS (*.cdb)")
        
        if fname[0] == '':
            return
        self.cdb_file = fname[0]
        self.read_cdb()
        
    def chooseSaveFile(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file', directory='/', filter="ABAQUS (*.inp)")
        
        if fname[0] == '':
            return
        self.inp_file = fname[0]
        #try:
        self.write_inp()
        #except AttributeError:
        #    print('A point has not been selected')
            
    def createActions(self):
        self.openFile = QAction(QIcon('open.png'), 'Open', self, 
                                shortcut='Ctrl+O',
                                triggered=self.chooseOpenFile)
        self.saveFile = QAction(QIcon('open.png'), 'Save', self,
                                shortcut='Ctrl+S',
                                triggered=self.chooseSaveFile)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               triggered=self.close)
        
    def createMenus(self):
        """
        Numpy style docstring.

        """
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.saveFile)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
    def read_cdb(self):
        """
        Examples
        cdb_inp('file.cdb','Stiffneck_Plastic','S4')
        cdb_inp('Foam.cdb','Foam','C3D8')

        """
        with open(self.cdb_file) as file:
            self.cdb_list = file.readlines()
    
        nodIndex = self.findIndex('NBLOCK')
        NUMNODES = self.NUMOFF('NODE')
        if NUMNODES:
            print('Number of Nodes:', NUMNODES)
        else:
            print('NO NODES!!!')
            return
    
        # Get data
        self.NODE_DATA = []
        for i in range(NUMNODES):
            string = self.cdb_list[i+nodIndex[0]+2]
            this_list = [string[0:9],string[3*9:3*9+21],string[3*9+21:3*9+21*2],string[3*9+21*2:3*9+21*3]]
            for i in range(len(this_list)):
                this_list[i] = this_list[i].strip()
            self.NODE_DATA.append(this_list)
    
        # Get element info
        # Search for EBLOCK
        ellIndex = self.findIndex('EBLOCK')
        NUMELEMENTS = self.NUMOFF('ELEM')
        if NUMELEMENTS:
            print('Number of Elements:', NUMELEMENTS)
        else:
            print('NO ELEMENTS!!!')
            return
    
        # Get data
        self.ELEMENT_DATA = []
        for i in range(NUMELEMENTS):
            self.ELEMENT_DATA.append(self.cdb_list[i+ellIndex[0]+2].split()[10:])
            if i > 2:
                if int(self.cdb_list[i+ellIndex[0]+2].split()[10]) != int(self.cdb_list[i+ellIndex[0]+1].split()[10])+1:
                    print('Something went wrong at: ' + self.cdb_list[i+ellIndex[0]+2].split()[10])
    
    def write_inp(self):
        self.title = self.inp_file.split('/')[-1][:-4]
        # Creating inp file
        self.mat_head = '*SOLID SECTION, ELSET=PT_' + self.title + ', MATERAIL=PM_' + self.title + '\n*MATERIAL, NAME=PM_' + self.title + '\n'
        self.nod_head = '*NODE\n'
        self.ell_head = '*ELEMENT, TYPE=' + self.element_type_CB.currentText() + ', ELSET=PT_' + self.title + '\n'
        
        # Open/Create new inp file and write main heading
        with open(self.inp_file,'w') as output:
            output.write(self.mat_head)
    
            # Write node data
            self.writeDATA(output,self.nod_head,self.NODE_DATA)
    
            # Write element data
            self.writeDATA(output,self.ell_head,self.ELEMENT_DATA)
    
            # Write the nodeset data
            self.nodeSets(output)

    def NUMOFF(self,ellnod):
        # ellnod is string with 'NODE' for node count or 'ELEM' for element count
        Index = self.findIndex('NUMOFF,' + ellnod)
        NUMOFF = int(self.cdb_list[Index[0]].split(',')[-1].strip())
        return NUMOFF
    
    def findIndex(self,keyWordInput):
        wildcard = '*'
        Instance = fnm.filter(self.cdb_list, keyWordInput + wildcard)
        Index = []
        if len(Instance) > 0:
            for i in range(len(Instance)):
                Index.append(self.cdb_list.index(Instance[i]))
            return Index
        else:
            print('No ' + keyWordInput + ' found, check the output file for completeness!')
            return

    def writeDATA(self,output,header,DATA):
        output.write(header)
        count = 0
        for i in range(len(DATA)):
            for j in range(len(DATA[0])):
                if DATA[i][j] == '':
                    DATA[i][j] = '0.0000000000000E+000'
                    print(DATA[i])
                    count += 1
                output.write(DATA[i][j])
                if j != len(DATA[0])-1:
                    output.write(',') 
            output.write('\n')

    def nodeSets(self,output):
        # Include a set of elements with a name
        nodSetIndex = self.findIndex('CMBLOCK')
        if not nodSetIndex:
            return
        for i in range(len(nodSetIndex)):
            NODESETNUM = int(self.cdb_list[nodSetIndex[i]].split(',')[-1].split()[0])
            NODESETNAME = self.cdb_list[nodSetIndex[i]].split(',')[1]
            NUMLINES = math.ceil(NODESETNUM / 8)
            NODESET = []
            for lines in range(NUMLINES):
                SOME_NODES = self.cdb_list[nodSetIndex[i] + 2 + lines].split()
                for nodes in range(len(SOME_NODES)):
                    NODESET.append(SOME_NODES[nodes])
            self.writeNodeSet(output,NODESETNAME,NODESET)

    def writeNodeSet(self,output,name,DATA):
        output.write('*NSET, NSET=NS_' + name + '\n')
        counter = 0
        for i in range(len(DATA)):
            output.write(DATA[i] + ',')
            if DATA[i] == DATA[-1]:
                break
            counter = counter + 1
            if(counter % 10 == 0):
                output.write('\n')
        output.write('\n')

if __name__=="__main__":
    app = QApplication(sys.argv)
    win = cdb_inp_GUI()
    win.show()
    sys.exit(app.exec_())