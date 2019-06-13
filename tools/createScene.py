# 256 Pipeline tools
# Create ANIMATION and RENDER scenes

import hou
import os
import json

from PySide2 import QtCore, QtUiTools, QtWidgets
import dna
reload(dna)

# Get environment data
rootProject = os.environ['ROOT']
genesFileShots = dna.genesFileShots.format(rootProject)
genesFileAssets = dna.genesFileAssets.format(rootProject)
genesShots = json.load(open(genesFileShots)) # All shots genes
genesAssets = json.load(open(genesFileAssets)) # All shots genes

# Get Houdini root nodes
sceneRoot = hou.node('/obj/')
outRoot = hou.node('/out/')


def createHip(fileType, sequenceNumber, shotNumber, catch=None):
    '''
    Save new scene, build scene content.
    :param sceneType: type of created scene, Render, Animation etc
    :param catch: determinate if procedure were run for the firs time from this class,
    or it returns user reply from SNV class
    :return:
    '''

    print '>> Saving {} hip file...'.format(fileType)

    # Get current shot gene
    # shotGene = dna.getShotGene(sequenceNumber, shotNumber, genesShots, genesAssets)
    # if not shotGene:
        # return

    # If createRenderScene() runs first time
    print catch
    if catch == None:

        # Build path to 001 version
        pathScene = dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)

        # Start new Houdini session without saving current
        hou.hipFile.clear(suppress_save_prompt=True)

        # Check if file exists
        if not os.path.exists(pathScene):
            # Save first version if NOT EXISTS
            hou.hipFile.save(pathScene)
            hou.ui.displayMessage('File created:\n{}'.format(pathScene.split('/')[-1]))
            # print '>> First version of file saved!'
        else:
            # If 001 version exists, get latest existing version
            pathScene = dna.buildPathLatestVersion(pathScene)
            # Run Save Next Version dialog if EXISTS
            winSNV = SNV(fileType, sequenceNumber, shotNumber, pathScene)
            winSNV.show()
            # winSNV.wait_modal()
            # winSNV.close()
            return

    # If createRenderScene() runs from SNV class: return user choice, OVR or SNV
    elif catch == 'SNV':
        # Save latest version
        newPath = dna.buildPathNextVersion(dna.buildPathLatestVersion(
            dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)))
        hou.hipFile.save(newPath)
        hou.ui.displayMessage('New version saved:\n{}'.format(newPath.split('/')[-1]))
    elif catch == 'OVR':
        # Overwrite existing file
        pathScene = dna.buildPathLatestVersion(
            dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber))
        hou.hipFile.save(pathScene)
        hou.ui.displayMessage('File overwited:\n{}'.format(pathScene.split('/')[-1]))
    else:
        return

    # Build scene content
    # buildSceneContent(fileType, sequenceNumber, shotNumber)

    # Save scene
    hou.hipFile.save()

    print '>> Saving {} hip file done!'.format(fileType)


def buildSceneContent(fileType, sequenceNumber, shotNumber, genesShots):
    '''
    Create scene content: import characters, environments, props, materials etc.

    Render scene schema:
        [Render obj]      [Environment]     [Characters]     [Props]      [FX]
        - materials       - Env             - char 1         - prop 1     - fx 1
        - lights                            - char 2         - prop 2     - fx 2
        - camera                            - ...            - ...        - ...

    :param fileType:
    :param sequenceNumber:
    :param shotNumber:
    :return:
    '''

    print '>> Building scene content...'

    # Get shot data. Stop if no data in database for current shot
    shotGenes = dna.getShotGenes(sequenceNumber, shotNumber, genesShots)
    if not shotGenes:
        return

    # Expand shot data

    #env_data = shotGene['environmentData']
    #char_data = shotGene['charactersData']
    #fx_data = shotGene['fxData']
    #frameEnd = shotGene['shotData']['sg_cut_out']

    # Initialize scene
    scenePath = hou.hipFile.path()

    """
    # SETUP SCENE (end frame ...)
    hou.playbar.setFrameRange(dna.frameStart, frameEnd)
    hou.playbar.setPlaybackRange(dna.frameStart, frameEnd)

    # [Render obj]
    if env_data:
        # Add Material lib HDA
        mat_data = env_data['materials']
        ML = sceneRoot.createNode(mat_data['hda_name'], mat_data['name'])
        ML.setPosition([0, 0])
        # Add lights HDA
        lit_data = env_data['lights']
        LIT = sceneRoot.createNode(lit_data['hda_name'], lit_data['name'])
        LIT.setPosition([0, -dna.nodeDistance_y])
        # Add Camera via ABC. Done in Import ANM

    # [Environment]
    if env_data:
        pass
        #ENV = createHDA(sceneRoot, env_data['hda_name'], env_data['code'])
        #ENV.setPosition([dna.nodeDistance_x, 0])

    # [Characters]
    if char_data:
        for n, character in enumerate(char_data):
            CHAR = dna.createContainer(sceneRoot, char_data[n]['code'], mb=1)
            CHAR.setPosition([2*dna.nodeDistance_x, n*dna.nodeDistance_y])

    # [FX]
    if fx_data:
        for n, FX in enumerate(fx_data):
            FX = sceneRoot.createNode(FX['hda_name'], FX['code'])
            FX.setPosition([3*dna.nodeDistance_x, n*dna.nodeDistance_y])

    # Setup Render scene
    if fileType == dna.fileTypes['renderScene']:
        # SETUP MANTRA OUTPUT
        # Create mantra render node
        mantra = outRoot.createNode('ifd', dna.mantra)

        # Render sequence setup
        renderSequence = dna.buildRenderSequencePath(scenePath)

        # Setup Mantra parameters
        mantra.parm('vm_picture').set(renderSequence)
        cameraName = dna.cameraName.format(sequenceNumber, shotNumber)
        mantra.parm('camera').set('/obj/{}'.format(cameraName))
        # Set common parameters from preset
        for param, value in dna.renderSettings['common'].iteritems():
            mantra.parm(param).set(value)
        # Set DRAFT parameters
        for param, value in dna.renderSettings['draft'].iteritems():
            mantra.parm(param).set(value)

    # Setup Animation Scene
    if fileType == dna.fileTypes['animationScene']:
        # Create Camera
        CAM = sceneRoot.createNode('cam', 'E{0}_S{1}'.format(sequenceNumber, shotNumber))
        CAM.setPosition([0, -dna.nodeDistance_y*2])
        dna.setCameraParameters(CAM)
    """
    print '>> Building scene content done!'


class SNV(QtWidgets.QWidget):
    def __init__(self, fileType, sequenceNumber, shotNumber, pathScene):
        # Setup UI
        super(SNV, self).__init__()
        self.fileType = fileType # RND, ANM etc. To return back to CS object
        self.sequenceNumber = sequenceNumber
        self.shotNumber = shotNumber
        ui_file = '{}/saveNextVersion_Warning.ui'.format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        # Setup label
        message = 'File exists!\n{}'.format(dna.analyzeFliePath(pathScene)['fileName'])
        self.ui.lab_message.setText(message)

        # Setup buttons
        self.ui.btn_SNV.clicked.connect(self.SNV)
        self.ui.btn_SNV.clicked.connect(self.close)
        self.ui.btn_OVR.clicked.connect(self.OVR)
        self.ui.btn_OVR.clicked.connect(self.close)
        self.ui.btn_ESC.clicked.connect(self.close)

    def SNV(self):
        createHip(self.fileType, self.sequenceNumber, self.shotNumber, catch='SNV')

    def OVR(self):
        createHip(self.fileType, self.sequenceNumber, self.shotNumber, catch='OVR')

class CreateScene(QtWidgets.QWidget):
    def __init__(self):
        super(CreateScene, self).__init__()
        ui_file = "{}/createScene_main.ui".format(dna.folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(320, 120)  # resize window
        self.setWindowTitle('Create Scene')  # Title Main window

        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        self.ui.btn_createRenderScene.clicked.connect(lambda: self.createScene(fileType=dna.fileTypes['renderScene']))
        self.ui.btn_createAnimScene.clicked.connect(lambda: self.createScene(fileType=dna.fileTypes['animationScene']))
        self.ui.btn_createRenderScene.clicked.connect(self.close)

    def createScene(self, fileType):
        '''
        Create hip scene and build all content (bring assets and camera)
        :param fileType:
        :return:
        '''
        sequenceNumber = self.ui.lin_episode.text()
        shotNumber = self.ui.lin_shot.text()
        print 'A'
        createHip(fileType, sequenceNumber, shotNumber)
        #buildSceneContent(fileType, sequenceNumber, shotNumber, genesShots)
        print 'C'

    def createScene_rem(self, fileType, catch = None):
        '''
        Save new scene, build scene content.
        :param sceneType: type of created scene, Render, Animation etc
        :param catch: determinate if procedure were run for the firs time from this class,
        or it returns user reply from SNV class
        :return:
        '''

        print '>> Building {} scene...'.format(fileType)

        # Get sequence and shot from UI
        sequenceNumber = self.ui.lin_episode.text()
        shotNumber = self.ui.lin_shot.text()

        # Get current shot gene
        shotGene = dna.getShotGene(sequenceNumber, shotNumber, genesShots, genesAssets)
        if not shotGene:
            return

        # If createRenderScene() runs first time
        if catch == None:

            # Build path to 001 version
            pathScene = dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)

            # Start new Houdini session without saving current
            hou.hipFile.clear(suppress_save_prompt=True)

            # Check if file exists
            if not os.path.exists(pathScene):
                # Save first version if NOT EXISTS
                hou.hipFile.save(pathScene)
                hou.ui.displayMessage('File created:\n{}'.format(pathScene.split('/')[-1]))
                # print '>> First version of file saved!'
            else:
                # If 001 version exists, get latest existing version
                pathScene = dna.buildPathLatestVersion(pathScene)
                # Run Save Next Version dialog if EXISTS
                winSNV = SNV(pathScene, fileType)
                winSNV.show()
                return

        # If createRenderScene() runs from SNV class: return user choice, OVR or SNV
        elif catch == 'SNV':
            # Save latest version
            newPath = dna.buildPathNextVersion(dna.buildPathLatestVersion(dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)))
            hou.hipFile.save(newPath)
            hou.ui.displayMessage('New version saved:\n{}'.format(newPath.split('/')[-1]))
        elif catch == 'OVR':
            # Overwrite existing file
            pathScene = dna.buildPathLatestVersion(dna.buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber))
            hou.hipFile.save(pathScene)
            hou.ui.displayMessage('File overwited:\n{}'.format(pathScene.split('/')[-1]))
        else:
            return

        # Build scene content
        self.buildSceneContent(fileType, shotGene)

        # Save scene
        hou.hipFile.save()

        print '>> Building {} scene done!'.format(fileType)

    def createHDA(self, parent, hdaTypeName, hdaName):
        '''
        Create Houdini digital asset node and set latest file version
        :param hdaTypeName:
        :param hdaName:
        :return:
        '''

        # Create HDA node inside parent container
        hda = parent.createNode(hdaTypeName, hdaName)

        # Set HDA file version (latest)
        hdaDefinitions = hda.type().allInstalledDefinitions()
        hdaPaths = [i.libraryFilePath() for i in hdaDefinitions]
        latestVersion = dna.extractLatestVersionFile(hdaPaths)  # 010

        for i in hdaPaths:
            if latestVersion in i.split('/')[-1]:
                latestIndex = hdaPaths.index(i)
                hdaDefinitions[latestIndex].setIsPreferred(True)

        return hda

    def buildSceneContent_rem(self, fileType, shotGene):
        '''
        Create scene content: import characters, environments, props, materials etc.

        Render scene schema:
            [Render obj]      [Environment]     [Characters]     [Props]      [FX]
            - materials       - Env             - char 1         - prop 1     - fx 1
            - lights                            - char 2         - prop 2     - fx 2
            - camera                            - ...            - ...        - ...

        :param fileType:
        :param sequenceNumber:
        :param shotNumber:
        :return:
        '''

        # Expand shot data
        shotNumber = shotGene['shotData']['code'][-3:]
        sequenceNumber  = shotGene['shotData']['sg_sequence']['name']
        env_data = shotGene['environmentData']
        char_data = shotGene['charactersData']
        fx_data = shotGene['fxData']
        frameEnd = shotGene['shotData']['sg_cut_out']

        # Initialize scene
        scenePath = hou.hipFile.path()


        # SETUP SCENE (end frame ...)
        hou.playbar.setFrameRange(dna.frameStart, frameEnd)
        hou.playbar.setPlaybackRange(dna.frameStart, frameEnd)

        # [Render obj]
        if env_data:
            # Add Material lib HDA
            mat_data = env_data['materials']
            ML = sceneRoot.createNode(mat_data['hda_name'], mat_data['name'])
            ML.setPosition([0, 0])
            # Add lights HDA
            lit_data = env_data['lights']
            LIT = sceneRoot.createNode(lit_data['hda_name'], lit_data['name'])
            LIT.setPosition([0, -dna.nodeDistance_y])
            # Add Camera via ABC. Done in Import ANM

        # [Environment]
        if env_data:
            #ENV = sceneRoot.createNode(env_data['hda_name'], env_data['code'])
            ENV = self.createHDA(sceneRoot, env_data['hda_name'], env_data['code'])
            ENV.setPosition([dna.nodeDistance_x, 0])

        # [Characters]
        if char_data:
            for n, character in enumerate(char_data):
                CHAR = dna.createContainer(sceneRoot, char_data[n]['code'], mb=1)
                CHAR.setPosition([2*dna.nodeDistance_x, n*dna.nodeDistance_y])

        # [FX]
        if fx_data:
            for n, FX in enumerate(fx_data):
                FX = sceneRoot.createNode(FX['hda_name'], FX['code'])
                FX.setPosition([3*dna.nodeDistance_x, n*dna.nodeDistance_y])

        # Setup Render scene
        if fileType == dna.fileTypes['renderScene']:
            # SETUP MANTRA OUTPUT
            # Create mantra render node
            mantra = outRoot.createNode('ifd', dna.mantra)

            # Render sequence setup
            renderSequence = dna.buildRenderSequencePath(scenePath)

            # Setup Mantra parameters
            mantra.parm('vm_picture').set(renderSequence)
            cameraName = dna.cameraName.format(sequenceNumber, shotNumber)
            mantra.parm('camera').set('/obj/{}'.format(cameraName))
            # Set common parameters from preset
            for param, value in dna.renderSettings['common'].iteritems():
                mantra.parm(param).set(value)
            # Set DRAFT parameters
            for param, value in dna.renderSettings['draft'].iteritems():
                mantra.parm(param).set(value)

        # Setup Animation Scene
        if fileType == dna.fileTypes['animationScene']:
            # Create Camera
            CAM = sceneRoot.createNode('cam', 'E{0}_S{1}'.format(sequenceNumber, shotNumber))
            CAM.setPosition([0, -dna.nodeDistance_y*2])
            dna.setCameraParameters(CAM)

# Create CS object
CS = CreateScene()

def run():
    # Run the Create Scene Tool
    CS.show()