# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 19:29:14 2023

@author: ljr1e21
"""

import fnmatch as fnm
import sys
from dataclasses import dataclass
from PyQt6.QtGui import (QIcon, QAction)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QFileDialog,
                             QVBoxLayout, QComboBox, QPushButton, QHBoxLayout)

class cdb_inp_GUI(QMainWindow):
    def __init__(self):
        super(cdb_inp_GUI,self).__init__()

        self.ELEMENT_DATA = []
        self.NODE_DATA = []
        self.sets = [] # List of Sets

        self.cdb_file = None
        self.cdb_list = None
        self.inp_file = None
        self.mainWidget = None
        self.element_type_CB = None
        self.fileMenu = None

        self.setWindowTitle("CAD Converter")
        self.initUI()

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
        self.element_type_CB.addItems(['S4','S8R','C3D8', 'C3D4'])
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
        fname = QFileDialog.getOpenFileName(self,
                                            'Open file',
                                            directory='/',
                                            filter="ANSYS (*.cdb)")

        if fname[0] == '':
            return
        self.cdb_file = fname[0]
        self.read_cdb()

    def chooseSaveFile(self):
        fname = QFileDialog.getSaveFileName(self,
                                            'Save file',
                                            directory='/',
                                            filter="ABAQUS (*.inp)")

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
        with open(self.cdb_file, 'r', encoding='utf-8') as file:
            self.cdb_list = file.readlines()

        nodIndex = self.findIndex('NBLOCK')
        NUMNODES = self.NUMOFF('NODE')
        if NUMNODES:
            print('Number of Nodes:', NUMNODES)
        else:
            print('NO NODES!!!')
            return

        # Get data
        # Read format string
        node_format = self.cdb_list[nodIndex[0]+1].strip()[1:-1].split(',')
        [N, L] = [int(i) for i in node_format[0].split('i')]
        # N is the number of secitons and L is the legnth of those sections in the numbering string.
        Cl = int(node_format[1].split('.')[0].split('e')[1])
        for i in range(NUMNODES):
            string = self.cdb_list[i+nodIndex[0]+2]
            this_list = [string[0:L],
                         string[N*L:N*L+Cl],
                         string[N*L+Cl:N*L+Cl*2],
                         string[N*L+Cl*2:N*L+Cl*3]]
            for i, l in enumerate(this_list):
                this_list[i] = l.strip()
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
        # Read format string
        element_format = self.cdb_list[ellIndex[0] + 1].strip()[1:-1].split(',')
        element_data \
            = [line.split() for line in self.cdb_list[ellIndex[0]+2:NUMELEMENTS+ellIndex[0]+2]]
        num_sets = len(list(set([line[0] for line in element_data if len(line) > 0])))
        set_names = [f'Set-{n}' for n in range(1,num_sets+1)]
        self.sets = [self.Set(x) for x in set_names]
        for _set in self.sets:
            _set.el_data = {}
            _set.nodes = []
        for i in range(NUMELEMENTS):
            line = self.cdb_list[i+ellIndex[0]+2].split()
            if len(line) == 0:
                continue
            self.ELEMENT_DATA.append(line[10:])
            self.sets[int(line[0]) - 1].el_data[line[10]] = line[11:]
            if i > 2:
                if int(line[10]) != int(self.cdb_list[i+ellIndex[0]+1].split()[10])+1:
                    print('Something went wrong at: ' + line[10])

        # Extracts the nodes in each set.
        for i, _set in enumerate(self.sets):
            self.sets[i].get_nodes()
            self.sets[i].el_type = 'C3D4'
        #print(self.ELEMENT_DATA)

    def write_inp(self):
        self.title = self.inp_file.split('/')[-1][:-4]
        # Creating inp file
        self.nod_head = '*NODE\n'
        self.ell_head = '*ELEMENT, TYPE=' + self.element_type_CB.currentText() + ', ELSET=PT_' + self.title + '\n'

        for i, _set in enumerate(self.sets):
            self.sets[i].el_type = self.element_type_CB.currentText()

        # Open/Create new inp file and write main heading
        with open(self.inp_file, 'w', encoding='utf-8') as output:

            for _set in self.sets:
                output.write(_set.mat_head())

            # Write node data
            self.writeNodeData(output, self.nod_head, self.NODE_DATA)

            # Write element data
            for _set in self.sets:
                output.write(_set.get_elset_output())

            # Write the nodeset data
            for _set in self.sets:
                output.write(_set.get_nset_output())

        print('Successfully written .inp file!')

    def NUMOFF(self, ellnod):
        # ellnod is string with 'NODE' for node count or 'ELEM' for element count
        Index = self.findIndex('NUMOFF,' + ellnod)
        NUMOFF = int(self.cdb_list[Index[0]].split(',')[-1].strip())
        return NUMOFF

    def findIndex(self, key_word_input):
        """Finds the index of the occurances of a specified keyword."""
        wildcard = '*'
        Instance = fnm.filter(self.cdb_list, key_word_input + wildcard)
        Index = []
        if len(Instance) > 0:
            for instance in Instance:
                Index.append(self.cdb_list.index(instance))
            return Index
        else:
            print('No ' + key_word_input + ' found, check the output file for completeness!')
            return

    def writeNodeData(self, output, header, DATA):
        output.write(header)
        count = 0
        for i, D in enumerate(DATA):
            for j, d in enumerate(D):
                if DATA[i][j] == '':
                    DATA[i][i] = '0.0000000000000E+000'
                    print(DATA[i])
                    count += 1
                output.write(d)
                if j != len(DATA[0])-1:
                    output.write(',')
            output.write('\n')

    @dataclass
    class Set:
        """Class for holding the data for an element set.
        Data is a dictionary with the element number as the key and list of
        corresponding nodes as the data."""
        name: str
        el_type: str = None
        el_data: dict = None
        nodes: list = None

        def get_elset_output(self) -> str:
            """Creates the string to be written to the output file for the element set."""
            _list = []
            _list.append(f'*ELEMENT, TYPE={self.el_type}, ELSET={self.name}\n')
            for element in self.el_data:
                line = f"{element}, {', '.join(self.el_data[element])}\n"
                _list.append(line)
            return ''.join(_list)

        def get_nset_output(self) -> str:
            """Creates string to be written to the output file for the node set."""
            _list = []
            _list.append(f'*NSET, NSET={self.name}, internal')
            num_lines = round((len(self.nodes) / 16) + 1)
            x = 1
            for i in range(num_lines):
                if i == num_lines - 1:
                    x = 0
                string = ', '.join(self.nodes[i*16:(i*16+16+1)*x-1])
                _list.append(string)
            return '\n'.join(_list) + '\n'
        
        def get_nodes(self) -> None:
            for element in self.el_data:
                for node in self.el_data[element]:
                    self.nodes.append(node)
            self._remove_duplicate_nodes()

        def _remove_duplicate_nodes(self) -> None:
            self.nodes =  list( dict.fromkeys(self.nodes) )
            for element in self.el_data:
                self.el_data[element] = list( dict.fromkeys(self.el_data[element]))

        def mat_head(self) -> str:
            return f'*SOLID SECTION, ELSET={self.name}, MATERIAL=PM_{self.name}\n*MATERIAL, NAME=PM_{self.name}\n'


if __name__=="__main__":
    app = QApplication(sys.argv)
    win = cdb_inp_GUI()
    win.show()
    sys.exit(app.exec())
