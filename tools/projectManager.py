'''
Create and manage assets and shots in project
'''

import hou
from PySide2 import QtCore, QtUiTools, QtWidgets
import dna
reload(dna)

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
        self.resize(320, 120)  # resize window
        self.setWindowTitle('Create Scene')  # Title Main window

        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)


PM = ProjectManager()

def run():
    # Run the Create Scene Tool
    PM.show()