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
        pass

        # Load current sequences

    def addShots(self):

        pass

# Create Tool instance
PM = ProjectManager()

def run():
    # Run the Tool
    PM.show()