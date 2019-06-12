'''
Create and manage assets and shots in project
'''


# TODO: split list of asset to categories: char, env, prop, fx
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
genesSequences = dna.loadGenes(genesFileSequences)
genesShots = dna.loadGenes(genesFileShots)

class CreateSequences(QtWidgets.QWidget):
    def __init__(self):
        # SETUP UI WINDOW
        super(CreateSequences, self).__init__()
        ui_main = "{}/projectManager_addSequences.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_main, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(320, 60)  # resize window
        self.setWindowTitle('Create Sequences')  # Title Main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.ui.btn_add.clicked.connect(self.addSequences)
        self.ui.btn_add.clicked.connect(self.close)

    def addSequences(self):


        listSeq = self.ui.lin_seqs.text()
        for sequenceName in listSeq.split(' '):

            if dna.checkExistsingEntity(genesFileSequences, sequenceName):
                print '>> Unable to create sequence {}: Sequence exists!'.format(sequenceName)
                continue

            sequenceData = dict(dna.sequenceTemplate)
            sequenceData['code'] = sequenceName
            genesSequences.append(sequenceData)

        json.dump(genesSequences, open(genesFileSequences, 'w'), indent=4)
        PM.addSequences(catch='')

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
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        ui_asset = "{}/projectManager_asset.ui".format(dna.folderUI)
        self.ui_asset = QtUiTools.QUiLoader().load(ui_asset, parentWidget=self)
        self.ui.assetLayout.addWidget(self.ui_asset)
        self.ui_asset.com_assetType.addItems(dna.assetTypes)


        self.ui.btn_add.clicked.connect(self.addAsset)
        self.ui.btn_add.clicked.connect(self.close)

    def addAsset(self):
        '''
        Create asset entity in datatbase
        :return:
        '''
        assetName = self.ui_asset.lin_assetName.text()

        # Skip creation if asset exists in DB
        if dna.checkExistsingEntity(genesFileAssets, assetName):
            print '>> Unable to create asset {}: Asset exists!'.format(assetName)
            return

        assetData = dna.assetTemplate

        assetData['code'] = assetName
        assetData['sg_asset_type'] = self.ui_asset.com_assetType.currentText()
        assetData['hda_name'] = self.ui_asset.lin_assetHDA.text()

        genesAssets.append(assetData)

        json.dump(genesAssets, open(genesFileAssets, 'w'), indent=4)

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
        self.resize(960, 400)  # resize window
        self.setWindowTitle('{} Project Manager'.format(os.environ['ROOT'].split('/')[-1]))  # Title Main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)


        # Asset UI
        ui_asset = "{}/projectManager_asset.ui".format(dna.folderUI)
        self.ui_asset = QtUiTools.QUiLoader().load(ui_asset, parentWidget=self)
        self.ui.assetLayout.addWidget(self.ui_asset)
        self.ui_asset.com_assetType.addItems(dna.assetTypes)

        # Shot UI
        ui_shot = "{}/projectManager_shot.ui".format(dna.folderUI)
        self.ui_shot = QtUiTools.QUiLoader().load(ui_shot, parentWidget=self)
        self.ui.shotLayout.addWidget(self.ui_shot)

        # Fill UI
        self.poulateAssets()
        self.poulateSequences()

        # Functionality
        self.ui.lis_seq.itemClicked.connect(self.poulateShots)
        self.ui.lis_shots.itemClicked.connect(self.displayShotProperties)
        self.ui.lis_assets.itemClicked.connect(self.displayAssetProperties)

        self.ui.btn_assetAdd.clicked.connect(self.addAssets)
        self.ui.btn_assetDel.clicked.connect(self.delAssets)
        self.ui.btn_seqAdd.clicked.connect(self.addSequences)
        self.ui.btn_seqDel.clicked.connect(self.delSequences)


    def poulateAssets(self):
        '''Add Asset data to UI'''
        self.ui.lis_assets.clear()
        for asset in genesAssets:
            self.ui.lis_assets.addItem(asset['code'])

    def poulateSequences(self):
        '''Add Sequence data to UI'''
        self.ui.lis_seq.clear()
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
        shotNumber = shotCode[-3:]
        sequenceCode = self.ui.lis_seq.selectedItems()[0].text()
        dataShot = dna.getShotData(sequenceCode, shotNumber, genesShots)

        # Get list of shot sequences
        listSequences = []
        for seq in genesSequences:
            listSequences.append(seq['code'])

        # Get list of shots assets
        listAssets = []
        for asset in genesAssets:
            listAssets.append(asset['code'])

        # Fill UI with Shot data
        self.ui_shot.com_shotSequence.clear()
        self.ui_shot.lis_assets.clear()
        self.ui_shot.lin_shotName.setText(shotCode)
        self.ui_shot.com_shotSequence.addItems(listSequences)
        self.ui_shot.lis_assets.addItems(listAssets)

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
            CA = CreateAssset()
            CA.show()
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

        dna.deleteEntity(genesFileAssets, assetNames)

        global genesAssets
        genesAssets = dna.loadGenes(genesFileAssets)
        # Repopulate Asset
        self.poulateAssets()

    def addSequences(self, catch=None):
        if catch == None:
            CS = CreateSequences()
            CS.show()
        else: # After closing Add Asset window
            # Reload genes
            global genesSequences
            genesSequences = dna.loadGenes(genesFileSequences)
            # Repopulate Asset
            self.poulateSequences()

    def delSequences(self):
        selectedSequences = self.ui.lis_seq.selectedItems()

        sequenceNames = []
        for seq in selectedSequences:
            sequenceNames.append(seq.text())

        dna.deleteEntity(genesFileSequences, sequenceNames)

        global genesSequences
        genesSequences = dna.loadGenes(genesFileSequences)
        # Repopulate Asset
        self.poulateSequences()


# Create Tool instance
PM = ProjectManager()

def run():
    # Run the Tool
    PM.show()