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
genesAssets = dna.loadGenes(genesFileAssets)
genesSequences = json.load(open(genesFileSequences))
genesShots = json.load(open(genesFileShots))

class CreateAssset(QtWidgets.QWidget):
    def __init__(self):
        # SETUP UI WINDOW
        super(CreateAssset, self).__init__()
        ui_main = "{}/projectManager_addAsset.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_main, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(320, 120)  # resize window
        self.setWindowTitle('Add Asset')  # Title Main window

        ui_asset = "{}/projectManager_asset.ui".format(dna.folderUI)
        self.ui_asset = QtUiTools.QUiLoader().load(ui_asset, parentWidget=self)
        self.ui.assetLayout.addWidget(self.ui_asset)
        self.ui_asset.com_assetType.addItems(dna.assetTypes)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.ui.btn_add.clicked.connect(self.addAsset)
        self.ui.btn_add.clicked.connect(self.close)

    def addAsset(self):
        '''
        Create asset entity in datatbase
        :return:
        '''
        assetName = self.ui_asset.lin_assetName.text()

        # Skip creation if asset exists in DB
        if dna.checkExistsAsset(genesFileAssets, assetName):
            print '>> Unable to create asset {}: Asset exists!'.format(assetName)
            return

        assetData = dna.assetTemplate

        assetData['code'] = assetName
        assetData['sg_asset_type'] = self.ui_asset.com_assetType.currentText()
        assetData['hda_name'] = self.ui_asset.lin_assetHDA.text()

        genesAssets.append(assetData)

        json.dump(genesAssets, open(genesFileAssets, 'w'), indent=4)  # write

        # Send data to PM
        PM.addAssets(catch='')

class ProjectManager(QtWidgets.QWidget):
    def __init__(self):
        super(ProjectManager, self).__init__()
        ui_main = "{}/projectManager_main.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_main, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(800, 400)  # resize window
        self.setWindowTitle('{} Project Manager'.format(os.environ['ROOT'].split('/')[-1]))  # Title Main window

        # Asset UI
        ui_asset = "{}/projectManager_asset.ui".format(dna.folderUI)
        self.ui_asset = QtUiTools.QUiLoader().load(ui_asset, parentWidget=self)
        self.ui.assetLayout.addWidget(self.ui_asset)
        self.ui_asset.com_assetType.addItems(dna.assetTypes)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # Fill UI
        self.poulateAssets()
        self.poulateSequences()

        # Functionality
        self.ui.lis_seq.itemClicked.connect(self.poulateShots)
        self.ui.lis_shots.itemClicked.connect(self.displayShotProperties)
        self.ui.lis_assets.itemClicked.connect(self.displayAssetProperties)

        #self.ui.btn_shotsAdd.clicked.connect(self.addShots)
        self.ui.btn_assetAdd.clicked.connect(self.addAssets)
        self.ui.btn_assetDel.clicked.connect(self.delAssets)


    def poulateAssets(self):
        '''Add Asset data to UI'''
        self.ui.lis_assets.clear()
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
        dataAsset = dna.getAssetDataByName(genesAssets, assetCode)

        # Fill UI with asset data
        self.ui_asset.lin_assetName.setText(assetCode)
        index = self.ui_asset.com_assetType.findText(dataAsset['sg_asset_type'], QtCore.Qt.MatchFixedString)
        self.ui_asset.com_assetType.setCurrentIndex(index)
        self.ui_asset.lin_assetHDA.setText(dataAsset['hda_name'])

    def addAssets(self, catch=None):
        '''Add asset to database'''
        if catch == None:
            AS = CreateAssset()
            AS.show()
        else: # After closing Add Asset window
            # Reload genes
            global genesAssets
            genesAssets = dna.loadGenes(genesFileAssets)
            # Repopulate Asset
            self.poulateAssets()

    def delAssets(self):
        selectedAssets = self.ui.lis_assets.selectedItems()

        assetNames = []
        for asset in selectedAssets:
            assetNames.append(asset.text())

        dna.deleteAssets(genesFileAssets, assetNames)

        global genesAssets
        genesAssets = dna.loadGenes(genesFileAssets)
        # Repopulate Asset
        self.poulateAssets()

    # TO DNA







# Create Tool instance
PM = ProjectManager()

def run():
    # Run the Tool
    PM.show()