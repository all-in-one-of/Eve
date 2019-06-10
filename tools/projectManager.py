'''
Create and manage assets and shots in project
'''

import hou
import json
import os

from PySide2 import QtCore, QtUiTools, QtWidgets
import dna
reload(dna)


# Get environment data
rootProject = os.environ['ROOT']
genesFileAssets = dna.genesFileAssets.format(rootProject)
genesFileShots = dna.genesFileShots.format(rootProject)
genesFileSequences = dna.genesFileSequences.format(rootProject)
#genesProject = json.load(open(genesFileProject))

seqItemParams = ['Number', 'Description']

class AlignDelegate(QtWidgets.QItemDelegate):
    '''
    Central alignment of UI table of shots
    '''
    def paint(self, painter, option, index):
        option.displayAlignment = QtCore.Qt.AlignCenter # Center align
        QtWidgets.QItemDelegate.paint(self, painter, option, index)

class AddSequences(QtWidgets.QWidget):
    def __init__(self):
        # SETUP UI WINDOW
        super(AddSequences, self).__init__()
        ui_file = "{}/projectManager_sequences.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(320, 120)  # resize window
        self.setWindowTitle('List of Sequences')  # Title Main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # SETUP SEQ TABLE
        self.ui.tab_seq.verticalHeader().hide()  # Hide row numbers
        self.ui.tab_seq.setItemDelegate(AlignDelegate())  # Set text alignment for cells
        self.ui.tab_seq.setColumnCount(2)  # Columns count
        # Set columns width
        self.ui.tab_seq.setColumnWidth(0, 80)
        self.ui.tab_seq.setColumnWidth(1, 240)
        self.ui.tab_seq.setHorizontalHeaderLabels(seqItemParams)
        self.ui.tab_seq.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # Load existing Sequences
        self.addSequences()

        # Set up functionality
        self.ui.btn_add.clicked.connect(self.addSequences)

    def addSequences(self, listSequences=None):

        # INIT LAUNCH: LOAD EXISTING SEQ
        if listSequences == None:

            sequencesItems = json.load(open(genesFileSequences))
            print sequencesItems

            # Clear table
            self.ui.tab_seq.setRowCount(0)

            # for n, seqItem in enumerate(sequencesItems):
                # seqItem = self.populateSeqItem(seqItem)
                # shotItemsUP.append(seqItem)


        #sequenceNumber = self.ui.lin_sequence.text()
        #shotNumbers = self.ui.lin_shots.text()
        #BR.addShots(sequenceNumber, shotNumbers)

    def populateSeqItem(self, seqItem):

        seqNumber = seqItem['name']

        #table = self.ui.tab_seq
        #rows = table.rowCount()  # Get quantity of rows
        #table.setRowCount(rows + 1)  # Add one row to existing rows
        pass

class ProjectManager(QtWidgets.QWidget):
    def __init__(self):
        super(ProjectManager, self).__init__()
        ui_file = "{}/projectManager_main.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        # self.resize(320, 120)  # resize window
        self.setWindowTitle('Project Manager')  # Title Main window

        # Functionality
        self.ui.btn_addShots.clicked.connect(self.addShots)
        self.ui.btn_addSequences.clicked.connect(self.addSequences)

        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

    def addSequences(self):
        SEQ = AddSequences()
        SEQ.show()

        # Load current sequences

    def addShots(self):

        pass

# Create Tool instance
PM = ProjectManager()

def run():
    # Run the Tool
    PM.show()