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
genesAssets = json.load(open(genesFileAssets))
genesSequences = json.load(open(genesFileSequences))
genesShots = json.load(open(genesFileShots))

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
        self.resize(800, 400)  # resize window
        self.setWindowTitle('{} Project Manager'.format(os.environ['ROOT'].split('/')[-1]))  # Title Main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # Fill UI
        self.poulateAssets()
        self.poulateSequences()

        # Functionality
        self.ui.lis_seq.itemClicked.connect(self.poulateShots)
        self.ui.lis_shots.itemClicked.connect(self.displayShotProperties)
        self.ui.lis_assets.itemClicked.connect(self.displayAssetProperties)
        #self.ui.btn_addShots.clicked.connect(self.addShots)

    def poulateAssets(self):
        '''Add Asset data to UI'''
        for asset in genesAssets:
            self.ui.lis_assets.addItem(asset['code'])

    def poulateSequences(self):
        '''Add Sequence data to UI'''
        for sequence in genesSequences:
            self.ui.lis_seq.addItem(sequence['code'])

    def poulateShots(self, sequence):
        '''Add Shot data to UI'''
        sequenceCode = sequence.text()

        # Clear list
        self.ui.lis_shots.clear()

        # get list of shots for current sequence
        for sequence in genesSequences:
            if sequence['code'] == sequenceCode:
                shots = sequence['shots']

        for shot in shots:
            self.ui.lis_shots.addItem(shot['code'])

    def displayShotProperties(self, shot):
        shotCode = shot.text()
        self.ui.lin_shotName.setText(shotCode)

    def displayAssetProperties(self, asset):
        assetCode = asset.text()
        self.ui.lin_assetName.setText(assetCode)


# Create Tool instance
PM = ProjectManager()

def run():
    # Run the Tool
    PM.show()