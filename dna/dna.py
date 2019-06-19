'''
256 Pipeline Tools
DNA of EVE: common core to be used in misc modules

General notes.
Versions and publishing. Before we implement Shotgun and develop a publishing mechanizm with it
we will consider LATEST version of file published (which needs to be used).

'''

# TODO: modify STATIC assets handling: move them to LIBRARY
# TODO: Solve sorting of FX assets scenes(ASSETS(CHAR, ENV, PROP), SHOTS) in PATTERNS
# TODO: Solve sorting of CHARACTER assets scenes (GEO, RIG, FUR) in PATTERNS

import os
import json
import glob
import hou
from PySide2 import QtCore, QtUiTools, QtWidgets

#import utils

# DEFINE COMMON VARIABLES AND PATHS
# Pipeline items
pipelineName = 'Eve'
extensionHoudini = 'hiplc'
extensionHDA = 'hdalc'
extensionRender = 'exr'
extensionFlipbook = 'jpg'
extensionCacheAnim = 'bgeo.sc'
extensionCamera = extensionHoudini


# FILE TYPES dictionary. Used for:
#   - define file name prefixes in file name patterns
#   - define file type in buildFilePath()
fileTypes = {'animationScene': 'ANM',
             'renderScene': 'RND',
             'character': 'GEO',
             'environment': 'ENV',
             'prop': 'PRO',
             'FX': 'FXS',
             'HDA': 'HDA',
             'renderSequence': 'EXR',
             'flipbookSequence': 'FBK',
             'cacheAnim': 'CAN',
             'cacheCamera': 'CAM'}

# Asset types
assetTypes = ['character', 'environment', 'prop', 'FX']

# Common variables
frameStart = 1
resolution_HR = (1920, 810)
resolution_LR = (1280, 540)

# PATHS
# Documentation paths
DOCS = 'https://github.com/kiryha/Eve/wiki/'
# Get Eve pipeline root folder <X:/Eve>
rootPipeline = os.path.dirname(os.path.dirname(__file__)).replace('\\','/')
# Get project root folder, defined in runHoudini.py  <P:/PROJECTS/NSI/>
rootProject = os.environ['ROOT']
# Get root for Houdini project ($JOB variable), defined in runHoudini.py <P:/PROJECTS/NSI/PROD/3D>
root3D = os.environ['JOB']
# Get path to *.UI files <X:/Eve/ui>
folderUI = '{0}/ui'.format(rootPipeline)
# Database files
genesFileAssets = '{0}/PREP/PIPELINE/genes/assets.json'
genesFileShots = '{0}/PREP/PIPELINE/genes/shots.json'
genesFileSequences = '{0}/PREP/PIPELINE/genes/sequences.json'

# FILE NAMES AND PATHS PATTERNS
fileNameSequence =  'E{0}_S{1}_{2}.$F.{3}'                                 # Output sequence (flipbook, mantra, cache)
fileNameAnimation = fileTypes['animationScene'] + '_E{0}_S{1}_{2}.{3}'     # Animation scene name
fileNameRender =    fileTypes['renderScene'] + '_E{0}_S{1}_{2}.{3}'        # Render scene name
fileNameCamera =    fileTypes['cacheCamera'] + '_E{0}_S{1}_{2}.{3}'        # Camera exported ANM >> RND name
fileNameChar =      fileTypes['character'] + '_{0}_{1}.{2}'                # Character asset scene name
fileNameEnv =       fileTypes['environment'] + '_{0}_{1}.{2}'              # Env asset scene name
fileNameProp =      fileTypes['prop'] + '_{0}_{1}.{2}'                     # Prop asset scene name
fileNameFX =        fileTypes['FX'] + '_{0}_{1}.{2}'                       # FX asset scene name
fileNameHDA =       fileTypes['HDA'] + '_{0}_{1}.{2}'                      # HDA file name

filePathAnimation =       '{0}/scenes/ANIMATION/{1}/SHOT_{2}/{3}'          # Animation scene path
filePathRender =          '{0}/scenes/RENDER/{1}/SHOT_{2}/{3}'             # Render scene path
filePathSequenceRender =  '{0}/render/{1}/SHOT_{2}/{3}/{4}'                # Render sequence path
filePathSequenceCache =   '$JOB/geo/SHOTS/{0}/SHOT_{1}/{2}/GEO/{3}/{4}'    # Characters geometry cache path
filePathCamera =          '{0}/geo/SHOTS/{1}/SHOT_{2}/CAM/{3}'             # Camera ANM >> RND path
filePathChar =            '{0}/scenes/ASSETS/CHARACTERS/{1}/{2}/{3}'       # Character asset scene path
filePathEnv =             '{0}/scenes/ASSETS/ENVIRONMENTS/{1}/{2}'         # Environment asset scene path
filePathProp =            '{0}/scenes/ASSETS/PROPS/{1}/{2}'                # Prop asset scene path
filePathFX =              '{0}/scenes/FX/ASSETS/ENVIRONMENTS/{1}/{2}'      # FX asset scene path. WIP! need solve sorting
filePathHDA =             '{0}/hda/{1}/{2}/{3}/{4}'                         # HDA path.



# HOUDINI SCENE CONTENT
# Currently string oriented.
# Another option is to use custom UID (node.setUserData()) for each node and save it in database. Potentially TBD.

# Get Houdini root nodes


sceneRoot = hou.node('/obj/')
outRoot = hou.node('/out/')
# Distance between nodes in scene view
nodeDistance_x = 3.0
nodeDistance_y = 0.8
# Shot camera name Animation scene
cameraName = 'E{0}_S{1}'
# File Cache SOP name for characters
fileCacheName = 'CACHE_{}'
# Mantra node
mantra = 'RENDER'

# SETTINGS
renderSettings = {
    'common': {
            'trange': 1,                     # Frame range
            'vm_dof': 1,                     # Enable DOF
            'allowmotionblur': 1,            # Enable MB
            'vm_renderengine': '3',          # PBR render engine
            'vm_reflectlimit': 1,            # Reflection limit
            'vm_refractlimit': 1,            # Refraction limit
            'vm_diffuselimit': 1,            # Diffuse limit
            'vm_ssslimit': 1,                # SSS limit
            'vm_volumelimit': 1              # Volume limit
    },
    'draft': {
            'vm_samplesx': 3,                # Pixel samples X
            'vm_samplesy': 3,                # Pixel samples Y
            'vm_maxraysamples': 1            # Max Ray Samples
    },
    'production': {}
}

# TEMPLATES
sequenceTemplate = {"code": "",
                    "shots": []}

shotTemplate = {"code": "",
                "sg_cut_out": 125,
                "sg_sequence": {},
                "assets": [],
                "description": ""}

assetTemplate = {"code": "",
                 "sg_asset_type": "",
                 "hda_name": "",
                 "hda_version": "",
                 "description": "",
                 "materials": [],
                 "lights": []}

# FILE PATH (STRING) MANIPULATIONS
# File Naming convention for filePath:
# <filePath> = <fileLocation>/<fileNme>
# <fileName> = <fileCode>_<fileVersion>.<fileExtension>
# filePathExample = 'P:/PROJECTS/NSI/PROD/3D/scenes/ANIMATION/ANM_E010_S010_001.hipnc'
# folderPathExample = 'P:/PROJECTS/NSI/PROD/3D/render/010/SHOT_010/001/'

def analyzeFliePath(filePath):
    '''
    Disassemble full path (string) into components
    Example filePaths:
        'P:/PROJECTS/NSI/PROD/3D/scenes/ANIMATION/ANM_E010_S010_001.hipnc'
        'P:/PROJECTS/NSI/PROD/3D/render/010/SHOT_020/001/E010_S020_002.$F.exr'

    fileLocation = P:/PROJECTS/NSI/PROD/3D/scenes/ANIMATION/
    fileName = ANM_E010_S010_001.hipnc
    fileType = ANM
    sequenceNumber = 010
    shotNumber = 010
    fileVersion = 001
    fileCode = ANM_E010_S010
    fileExtension = hipncw
    '''

    fileName = filePath.split('/')[-1]
    fileLocation = filePath.replace('{}'.format(fileName), '')
    outputMapName = analyzeFileName(fileName)

    # File elements dictionary
    pathMap = {'fileLocation': fileLocation,
               'folderVersion': fileLocation.split('/')[-2],
               'fileName': fileName,
               'fileType': outputMapName['fileType'],
               'sequenceNumber': outputMapName['sequenceNumber'],
               'shotNumber': outputMapName['shotNumber'],
               'fileVersion': outputMapName['fileVersion'],
               'fileCode': outputMapName['fileCode'],
               'fileExtension': outputMapName['fileExtension']}

    return pathMap

def analyzeFileName(fileName):
    '''
    Disassemble <fileName> string
    Example naming conventions:
        <fileName> = ANM_E010_S010_001.hipnc (ANM, RND scenes)
        <fileName> = CITY_001.hipnc,  CITY_ANM_001.hipnc (HDA)
        <fileName> = GEO_CITY_001.hipnc (asset scenes)
        <fileName> = E010_S010_001.exr ( Render sequence (Flipbook or mantra))

    '''

    fileExtension = fileName.split('.')[-1]
    fileCodeVersion = fileName.split('.')[0]

    parts = fileCodeVersion.split('_')

    # HANDLE DIFFERENT NAMING CONVENTIONS:
    # Output sequence (Flipbook or mantra or cache)
    if parts[0].startswith('E'):
        # E010_S010_001.exr
        fileVersion = parts[-1]
        shotNumber = parts[1][-3:]
        sequenceNumber = parts[0][-3:]
        fileType = ''
        fileCode = '{0}_{1}'.format(parts[0], parts[1])

    # ANM, RND, CAM scene file names
    elif parts[0] in fileTypes.values():
        # ANM_E010_S010_001.hipnc
        fileVersion = parts[-1]
        shotNumber = parts[-2][-3:]
        sequenceNumber = parts[-3][-3:]
        fileType = parts[0]
        fileCode = fileCodeVersion.replace('_{0}'.format(fileVersion), '')

    # ARBITRARY names
    else:
        # CITY_001.hipnc, CITY_ANM_001.hdnc
        fileVersion = parts[-1]
        shotNumber = ''
        sequenceNumber = ''
        fileType = ''
        fileCode = ''

        # Join all parts but version to one string
        for i in parts[:-1]:
            if fileCode == '':
                fileCode = i
            else:
                fileCode = fileCode + '_' + i

    # Return dictionary: sequenceNumber, shotNumber
    outputMap = {'fileType': fileType,
                 'sequenceNumber': sequenceNumber,
                 'shotNumber': shotNumber,
                 'fileVersion': fileVersion,
                 'fileCode': fileCode,
                 'fileExtension': fileExtension}

    return outputMap

def extractLatestVersionFile(listExisted):
    '''
    Get list of files paths (listExisted), return latest existing version (<###> string)
    '''

    listVersions = []
    for filePath in listExisted:
        listVersions.append(int(analyzeFliePath(filePath)['fileVersion']))
    latestVersion = '{:03}'.format(max(listVersions))
    return latestVersion

def extractLatestVersionFolder(filePath):
    '''
    Get FOLDER filePath, return string: latest (by number) available version ("002")
    Assume that last folder in filePath is a version (P:/<...>/.../<...>/<version>)
    :param filePath:
    :return: string latest existing version ('001')
    '''

    # print 'dna.extractLatestVersionFolder [filePath] = {}'.format(filePath)

    # Strip last slash from path
    if filePath.endswith('/'):
        filePath = filePath[:-1]

    # Get list of version folders
    pathVersions = filePath[:-3] # strip version folder from path
    listVersions = os.listdir(pathVersions)
    listVersionsInt = []

    # Build list of Integer folder names
    for i in listVersions:
        if len(i) == 3:
            listVersionsInt.append(int(i))

    # Find highest folder number
    maxInt = max(listVersionsInt)
    # Build a string ('002') from highest number
    latestVersion = '{:03d}'.format(maxInt)

    # print 'dna.extractLatestVersionFolder [latestVersion] = {}'.format(latestVersion)
    return latestVersion

def buildPathNextVersion(filePath):
    '''
    Build next version of input path
    Get filePath, create new full filePath with a next version in fileName (P:/.../ANM_E010_S010_002.hipnc)
    '''

    # print 'dna.buildPathNextVersion [filePath] = {}'.format(filePath)

    # Disassemble file path
    filePathData = analyzeFliePath(filePath)
    fileLocation = filePathData['fileLocation']
    fileCode = filePathData['fileCode']
    fileVersion = filePathData['fileVersion']
    fileExtension = filePathData['fileExtension']
    # print 'dna.buildPathNextVersion [filePathData] = {}'.format(filePathData)

    fileVersionNext = '{:03}'.format(int(fileVersion) + 1)
    filePathNextVersion = '{0}{1}_{2}.{3}'.format(fileLocation, fileCode, fileVersionNext, fileExtension)

    # print 'dna.buildPathNextVersion [filePathNextVersion] = {}'.format(filePathNextVersion)

    return filePathNextVersion

def buildPathLatestVersion(filePath):
    '''
    Get filePath, create new filePath with a latest available version in fileName
    '''

    #print 'dna.buildPathLatestVersion [filePath] = {}'.format(filePath)

    # Disassemble file path
    filePathData = analyzeFliePath(filePath)
    fileLocation= filePathData['fileLocation']
    fileCode = filePathData['fileCode']
    fileExtension = filePathData['fileExtension']

    listExisted = glob.glob('{0}{1}_*.{2}'.format(fileLocation, fileCode, fileExtension))
    fileVersionLatest = extractLatestVersionFile(listExisted)
    filePathLatestVersion = '{0}{1}_{2}.{3}'.format(fileLocation, fileCode, fileVersionLatest, fileExtension)

    #print 'dna.buildPathLatestVersion [filePathLatestVersion] = {}'.format(filePathLatestVersion)

    return filePathLatestVersion

def buildFilePath(version, fileType, scenePath=None, assetName=None, sequenceNumber=None, shotNumber=None, assetType=None):
    '''
    Generate and return a full path to a file <filePath> (string).

    Rely on # FILE NAMES AND PATHS PATTERNS
    There are 2 options to build a path:
        - based on Houdini scene name (in addition to file type and version)
        - based on Scene and Shot code (in addition to file type and version)

    :param version: version of the file
    :param fileType: type of file to generate (string), 'ANM', 'RND' etc
    :param scenePath: Full path to Houdini scene
    :param assetName: name of character asset
    :param sequenceNumber: Episode number (sequence number = sequence code) (010)
    :param shotNumber: Shot number (010)
    :return filePath: generated full path (string)
    '''

    if scenePath != None:
        filePathData = analyzeFliePath(scenePath)
        sequenceNumber = filePathData['sequenceNumber']
        shotNumber = filePathData['shotNumber']

    # HDA. ENV
    if fileType == fileTypes['HDA']:
        fileName = fileNameHDA.format(assetName, version, extensionHDA)
        if assetType == 'environment':
            filePath = filePathHDA.format(root3D, 'ASSETS', 'ENVIRONMENTS', assetName, fileName)

    # ASSET scenes. CHARACTER
    if fileType == fileTypes['character']:
        fileName = fileNameChar.format(assetName, version, extensionHoudini)
        filePath = filePathChar.format(root3D, assetName, 'GEO', fileName)

    # ASSET scenes. ENV
    if fileType == fileTypes['environment']:
        fileName = fileNameEnv.format(assetName, version, extensionHoudini)
        filePath = filePathEnv.format(root3D, assetName, fileName)

    # RENDER scene path
    if fileType == fileTypes['renderScene']:
        fileName = fileNameRender.format(sequenceNumber, shotNumber, version, extensionHoudini)
        filePath = filePathRender.format(root3D, sequenceNumber, shotNumber, fileName)

    # ANIMATION scene path
    if fileType == fileTypes['animationScene']:
        fileName = fileNameAnimation.format(sequenceNumber, shotNumber, version, extensionHoudini)
        filePath = filePathAnimation.format(root3D, sequenceNumber, shotNumber, fileName)

    # FLIPBOOK or MANTRA render sequence path
    elif fileType == fileTypes['flipbookSequence'] or fileType == fileTypes['renderSequence']:
        # Set file extension for RENDER or FLIPBOOK
        if fileType == fileTypes['flipbookSequence']:
            extension = extensionFlipbook
        else:
            extension = extensionRender

        fileName = fileNameSequence.format(sequenceNumber, shotNumber, version, extension)
        filePath = filePathSequenceRender.format(root3D, sequenceNumber, shotNumber, version, fileName)

    # Character animation CACHE path
    elif fileType == fileTypes['cacheAnim']:
        fileName = fileNameSequence.format(sequenceNumber, shotNumber, version, extensionCacheAnim)
        filePath = filePathSequenceCache.format(sequenceNumber, shotNumber, assetName, version, fileName)

    # CAMERA file ANM scene >> RND scene
    elif fileType == fileTypes['cacheCamera']:
        fileName = fileNameCamera.format(sequenceNumber, shotNumber, version, extensionCamera)
        filePath = filePathCamera.format(root3D, sequenceNumber, shotNumber, fileName)

    # print 'dna.buildFilePath() [filePath] = {}'.format(filePath)

    return filePath

def convertPathCache(pathCache):
    '''
    Convert geometry cache string path (used in FileCacheSOP) to path suitable for dna.extractLatestVersionFolder()
    Expand $JOB variable to a full path, remove file name
    :param pathCache:
    :return :
    '''

    fileName = pathCache.split('/')[-1]
    pathCacheFolder = pathCache.replace('$JOB', root3D).replace(fileName, '')

    return pathCacheFolder

def buildRenderSequencePath(scenePath=None):
    '''
    Create string path of the render images for MANTRA output node (LATEST VERSION)

    :param scenePath: string render scene path
                      P:/PROJECTS/NSI/PROD/3D/scenes/RENDER/010/SHOT_010/RND_E010_S010_004.hiplc
    :return: render images path of the LATEST VERSION ($JOB/render/010/SHOT_010/005/E010_S010_005.$F.exr)
    '''

    # Create path of the 001 version
    renderSequence = buildFilePath('001', fileTypes['renderSequence'], scenePath=scenePath)
    # Create folder for render file
    fileLocation = analyzeFliePath(renderSequence)['fileLocation']
    if not os.path.exists(fileLocation):
        # Make 001 folder
        os.makedirs(fileLocation)
    else:
        # If 001 file exists get latest version
        latestVersion = extractLatestVersionFolder(fileLocation)
        # If latest version folder is empty, use it. Otherwise create and use next version
        renderSequence = buildFilePath(latestVersion, fileTypes['renderSequence'], scenePath=scenePath)
        if os.listdir(analyzeFliePath(renderSequence)['fileLocation']):
            nextVersion = '{:03d}'.format(int(latestVersion) + 1)
            # Build latest existing path
            renderSequence = buildFilePath(nextVersion, fileTypes['renderSequence'], scenePath=scenePath)
            os.makedirs(analyzeFliePath(renderSequence)['fileLocation'])

        # Localize path (add $JOB)
        renderSequence = renderSequence.replace(root3D, '$JOB')

    return renderSequence

# DATABASE COMMUNICATIONS
# sequenceNumber = '010'
# shotNumber = '010'
# shotCode = 'SHOT_010'

def checkGenes(sequenceNumber, shotNumber, genesShots):
    ''' Check if data for current shot exists in database '''

    shotGene = getShotData(sequenceNumber, shotNumber, genesShots)
    if shotGene:
        return True
    else:
        print '>> There is no data for shot E{0}_S{1}'.format(sequenceNumber, shotNumber)

def loadGenes(genesFile):
    return json.load(open(genesFile))

def checkExistsingEntity(genesFile, name, sequenceNumber=None):
    '''
    Check if entity (asset, shot, sequence) with provided name exist in database
    :param name:
    :return:
    '''

    genes = loadGenes(genesFile)

    if not sequenceNumber: # check asset and sequence
        for entity in genes:
            if entity['code'] == name:
                return True
    else: # check shot
        for shot in genes:
            if shot['code'] == 'SHOT_{}'.format(name):
                if shot['sg_sequence']['name'] == sequenceNumber:
                    return True

def deleteEntity(genesFile, names, sequenceNumber=None):
    '''
    Delete entity (asset, shot, sequence) from database
    :param genesFile:
    :param names:
    :return:
    '''
    genes = loadGenes(genesFile)
    genesFiltered = []

    # Assets and Sequences
    if not sequenceNumber:
        for entity in genes:
            if not entity['code'] in names:
                genesFiltered.append(entity)
    # Shots
    else:
        for shot in genes:
            if not shot['code'] in names:
                if not shot['sg_sequence']['name'] == sequenceNumber:
                    genesFiltered.append(shot)

    json.dump(genesFiltered, open(genesFile, 'w'), indent=4)

def getShotData(sequenceNumber, shotNumber, genesShots):
    '''
    Get shot dictionary via sequence and shot numbers (010 > 010)

    To reduce database file (shots.json) before using Shotgun we don`t store sequences data there.
    So we looking for shots iterating shots dict, getting linked sequence, getting proper shot (shot > sequence > shot)
    Having Shotgun in place will allow to iterAte sequences and then find proper shot (sequence > shot)
    :param sequenceNumber: string '010'
    :param shotNumber: string '010'
    :return genesShots: list of shots dictionaries from db file (shots.json)
    [ {'code': 'SHOT_010', 'sg_cut_out': 200, 'sg_sequence': {'name': '010'}, 'assets': [{'name': 'CITY'}, {'name': 'ROMA'}]}, {}, ...]
    '''

    shotCode = 'SHOT_{0}'.format(shotNumber)
    shotData = None

    for shot in genesShots:
        # Get shot > sequence data
        if shot['sg_sequence']['name'] == sequenceNumber:
            # Get shot data
            if shot['code'] == shotCode:
                shotData = shot

    return shotData

def getAssetsDataByShot(shotData, genesAssets):
    '''
    Get full dictionaries of assets LINKED TO SHOT (including FXs)

    :param shotData: shot data dictionary
    :return assetsData: list of assetData dics (full dictionaries of assets linked to shot (with FXs))
    '''

    # assetsData = [{'name': 'CITY'}, {'name': 'ROMA'}]

    assetsData = []

    # Get assets
    for asset in shotData['assets']:
        for assetData in genesAssets:
            if assetData['code'] == asset['code']:
                assetsData.append(assetData)
    # Get FXs
    #for FX in shotData['fxs']:
        #for assetData in genesAssets:
            #if assetData['code'] == FX['name']:
                #assetsData.append(assetData)

    return assetsData

def getAssetDataByType(assetsData, assetType):
    '''
    Get data of particular type (char, env, prop) for the shot from input asset data dictionary (all shot assets).

    :param assetsData: list of all assets dictionaries linked to shot
    :param assetType: 'Environment', 'Character', 'Prop'
    :return:
    '''

    # assetsData = list of assets dictionaries linked to shot
    # assetType = 'Environment', 'Character', 'Prop'

    if assetType == 'environment':
        listEnvironments = []
        for assetData in assetsData:
            if assetData['sg_asset_type'] == assetType:
                listEnvironments.append(assetData)
        return listEnvironments

    if assetType == 'Character':
        listCharacters = []
        for assetData in assetsData:
            if assetData['sg_asset_type'] == assetType:
                listCharacters.append(assetData)
        return listCharacters

    if assetType == 'FX':
        listFXs = []
        for assetData in assetsData:
            if assetData['sg_asset_type'] == assetType:
                listFXs.append(assetData)
        return listFXs

def getAssetDataByName(genesAssets, assetCode):
    '''
    Return asset dictionary by asset name
    :param genesAsset:
    :param assetCode:
    :return:
    '''
    for asset in genesAssets:
        if asset['code'] == assetCode:
            return asset

def getShotGenes(sequenceNumber, shotNumber, genesShots, genesAssets):
    '''
    Pull all asset and shot data from the database during one call:
       - Get data for the current shot
       - Get assets linked to current shot
       - Organize assets by types (characters, env, props, fx)

    shotData = {
           'sg_sequence': {'name': '010'},
           'code': 'SHOT_010', 'sg_cut_out': 200,
           'assets': [{'name': 'CITY'}, {'name': 'ROMA'}]}

    environmentData = {
           'code': 'CITY',
           'sg_asset_type': 'Environment'
           'hda_name': 'city',
           'light_hda': {'hda_name': 'city_lights', 'name': 'CITY_LIT'},
           'animation_hda': {'hda_name': 'city_anm', 'name': 'CITY_ANM'},
           'crowds_hda': {'hda_name': 'city_crowds', 'name': 'CROWDS'},
           'proxy_hda': {'hda_name': 'city_prx', 'name': 'CITY_PRX'}}

    charactersData = [
           {'code': 'ROMA',
           'sg_asset_type': 'Character'}]

    :param sequenceNumber:
    :param shotNumber:
    :return genesShots: list of shots dictionaries
    :return genesAssets: list of assets dictionaries
    '''

    shotGene = {}

    shotData = getShotData(sequenceNumber, shotNumber, genesShots)

    if shotData:
        assetsData = getAssetsDataByShot(shotData, genesAssets)
        environmentData = getAssetDataByType(assetsData, 'environment')
        charactersData = getAssetDataByType(assetsData, 'Character')
        fxData = getAssetDataByType(assetsData, 'FX')

        shotGene['shotData'] = shotData
        shotGene['environmentData'] = environmentData
        shotGene['charactersData'] = charactersData
        shotGene['fxData'] = fxData

        return shotGene

# SCENE MANIPULATIONS
def collectCamera(camera):
    '''
    Create and return list of all camera nodes (parents)
    :param camera: shot camera object
    :return:
    '''

    listCameraNodes = []
    listCameraNodes.extend(camera.inputAncestors())
    listCameraNodes.append(camera)

    return listCameraNodes

def setCameraParameters(camera):
    # Set camera parameters
    camera.parm('far').set(5000)
    camera.parm('resx').set(resolution_HR[0])
    camera.parm('resy').set(resolution_HR[1])

def exportHDA(assetType, hdaName, hdaLabel):
    '''
    Create Houdini Digital Asset: create empty subnet, convert to HDA

    TODO: Need to implement SNV !!!!
    '''

    # Build HDA file path

    filePathHDA = buildFilePath('001', fileTypes['HDA'], assetName=hdaName, assetType=assetType)

    # Create subnetwork container
    subnet = sceneRoot.createNode("subnet", hdaLabel)

    # Create HDA from subnetwork
    hda = subnet.createDigitalAsset(
        name=hdaName,
        hda_file_name=filePathHDA,
        description=hdaLabel)

    # Update and save HDA
    # hdaDefinition = hda.type().definition()
    # hdaOptions = hdaDefinition.options()
    # hdaOptions.setSaveInitialParmsAndContents(True)
    # hdaDefinition.setOptions(hdaOptions)
    # hdaDefinition.save(hdaDefinition.libraryFilePath(), hda, hdaOptions)

def importHDA(parent, hdaName, hdaLabel):
    '''
    Create Houdini Digital Asset node in the scene and set latest file version

    :param hdaName: Name of HDA node (node type name)
    :param hdaLabel: label of HDA node (name shown in Node Editor)
    :return:
    '''

    # Create HDA node inside parent container
    hda = parent.createNode(hdaName, hdaLabel)

    # Set HDA file version (latest)
    hdaDefinitions = hda.type().allInstalledDefinitions()
    hdaPaths = [i.libraryFilePath() for i in hdaDefinitions]
    latestVersion = extractLatestVersionFile(hdaPaths)  # 010

    for i in hdaPaths:
        if latestVersion in i.split('/')[-1]:
            latestIndex = hdaPaths.index(i)
            hdaDefinitions[latestIndex].setIsPreferred(True)

    return hda

def createContainer(parent, name, bbox=0, mb=None, disp=1):
    '''
    Create scene container for CHARS, ENV etc

    :param parent: container node parent object (where to cretae it)
    :param name: container name
    :param bbox: display container content as bounding box (bbox = 2, full = 0)
    :param mb: turn on motion blur for container content geometry
    :param disp: Display container node flag (ON = 1, OFF = 0)
    :return:
    '''

    CONTAINER = parent.createNode('geo', name)

    # Display as bounding box
    CONTAINER.parm('viewportlod').set(bbox)

    # Set display flag
    CONTAINER.setDisplayFlag(disp)

    # Turn ON motion blur
    if mb is not None:
        CONTAINER.parm('geo_velocityblur').set(1)

    print '>>>> Created Container: {0}'.format(name)

    return CONTAINER

def buildShotContent(fileType, sequenceNumber, shotNumber, genesShots, genesAssets):
    '''
    Create (Update???) SHOT scene content: import characters, environments, props, materials etc.

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

    print '>> Building shot content...'#

    # Expand shot data
    shotGene = getShotGenes(sequenceNumber, shotNumber, genesShots, genesAssets)
    environmentData = shotGene['environmentData']
    characterData = shotGene['charactersData']
    fxData = shotGene['fxData']
    frameEnd = shotGene['shotData']['sg_cut_out']

    # Initialize scene
    scenePath = hou.hipFile.path()


    # SETUP SCENE generall
    hou.playbar.setFrameRange(frameStart, int(frameEnd))
    hou.playbar.setPlaybackRange(frameStart, int(frameEnd))

    """
    # [Environment] + [Render objects]
    if environmentData:
        ENV = importHDA(sceneRoot, environmentData['hda_name'], environmentData['code'])
        ENV.setPosition([nodeDistance_x, 0])

        # Add Material lib HDA
        # mat_data = environmentData['materials']
        # ML = sceneRoot.createNode(mat_data['hda_name'], mat_data['name'])
        # ML.setPosition([0, 0])
        # Add lights HDA
        # lit_data = environmentData['lights']
        # LIT = sceneRoot.createNode(lit_data['hda_name'], lit_data['name'])
        # LIT.setPosition([0, -nodeDistance_y])


    # [Characters]
    if characterData:
        for n, character in enumerate(characterData):
            CHAR = dna.createContainer(sceneRoot, characterData[n]['code'], mb=1)
            CHAR.setPosition([2*dna.nodeDistance_x, n*dna.nodeDistance_y])

    # [FX]
    if fxData:
        for n, FX in enumerate(fxData):
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

def createHip(fileType, sequenceNumber=None, shotNumber=None, assetName=None, catch=None): # pathScene=None
    '''
    Create asset/shot Houdini scene.

    :param fileType: type of created scene, Asset, Render, Animation etc
    :param catch: determinate if procedure were run for the firs time,
                  or it returns user reply from SNV class
    :return:
    '''

    print '>> Saving {} hip file...'.format(fileType)
    """
    # Build path to 001 version
    if catch==None:
        # SHOTS scenes
        if fileType == fileTypes['animationScene'] or fileType == fileTypes['renderScene']:
            pathScene = buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)
        # ASSETS scenes
        else:
            pathScene = buildFilePath('001', fileType, assetName=assetName)

    if snv(pathScene, 'createHip', catch):
        print 'A'
    else:
        print B''
    """


    # First time run
    if catch == None:
        # Build path to 001 version
        # SHOTS scenes
        if fileType == fileTypes['animationScene'] or fileType == fileTypes['renderScene']:
            pathScene = buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber)
        # ASSETS scenes
        else:
            pathScene = buildFilePath('001', fileType, assetName=assetName)

        # Start new Houdini session without saving current
        hou.hipFile.clear(suppress_save_prompt=True)

        # Check if file exists
        if not os.path.exists(pathScene):
            # Create FOLDER for HIP
            sceneLocation = analyzeFliePath(pathScene)['fileLocation']
            if not os.path.exists(sceneLocation):
                os.makedirs(sceneLocation)
            # Save first version if NOT EXISTS
            hou.hipFile.save(pathScene)
            print '>> Hip created: {}'.format(pathScene.split('/')[-1])
            return True
        else:
            # If 001 version exists, get latest existing version
            pathScene = buildPathLatestVersion(pathScene)
            # Run Save Next Version dialog if EXISTS
            winSNV = SNV(fileType, sequenceNumber, shotNumber, assetName, pathScene)
            if winSNV.exec_():
                return True
            else:
                return False

    # Run from SNV class: return user choice = SAVE NEXT VERSION
    elif catch == 'SNV':
        # Save latest version
        pathScene = buildPathNextVersion(buildPathLatestVersion(
            buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber, assetName=assetName)))
        hou.hipFile.save(pathScene)
        print '>> Hip saved with a latest version: {}'.format(pathScene.split('/')[-1])

    # Run from SNV class: return user choice = OVERWRITE
    elif catch == 'OVR':
        # Overwrite existing file
        pathScene = buildPathLatestVersion(
            buildFilePath('001', fileType, sequenceNumber=sequenceNumber, shotNumber=shotNumber, assetName=assetName))
        hou.hipFile.save(pathScene)
        print '>> Hip overwrited: {}'.format(pathScene.split('/')[-1])

    # Save current scene
    hou.hipFile.save()

    print '>> Saving {} hip file done!'.format(fileType)


def snv(filePath, parentName, catch=None):

    # First time run
    if catch == None:
        # Start new Houdini session without saving current
        hou.hipFile.clear(suppress_save_prompt=True)

        # Check if file exists
        if not os.path.exists(filePath):
            # Create FOLDER for HIP
            fileLocation = analyzeFliePath(filePath)['fileLocation']
            if not os.path.exists(fileLocation):
                os.makedirs(fileLocation)
            # Save first version if NOT EXISTS
            hou.hipFile.save(filePath)
            print '>> Hip created: {}'.format(filePath.split('/')[-1])
            return True
        else:
            # If 001 version exists, get latest existing version
            filePath = buildPathLatestVersion(filePath)
            # Run Save Next Version dialog if EXISTS
            winSNV = SNV2(filePath, parentName) # fileType, sequenceNumber, shotNumber, assetName,
            if winSNV.exec_():
                return True
            else:
                return False

    # Run from SNV class: return user choice = SAVE NEXT VERSION
    elif catch == 'SNV':
        # Save latest version
        filePath = buildPathNextVersion(buildPathLatestVersion(filePath))
        hou.hipFile.save(filePath)
        print '>> Hip saved with a latest version: {}'.format(filePath.split('/')[-1])

    # Run from SNV class: return user choice = OVERWRITE
    elif catch == 'OVR':
        # Overwrite existing file
        filePath = buildPathLatestVersion(filePath)
        hou.hipFile.save(filePath)
        print '>> Hip overwrited: {}'.format(filePath.split('/')[-1])

    # Save current scene
    hou.hipFile.save()


# UNSORTED
def createFolder(filePath):
    '''
    Create folder for a FILE if not exists
    !!! Does not support FOLDER paths (without file name) !!!
    filePath = P:/PROJECTS/NSI/PROD/3D/geo/SHOTS/010/SHOT_340/CAM/CAM_E010_S340.hipnc
    :param filePath: full path to a file
    :return:
    '''

    fileLocation = analyzeFliePath(filePath)['fileLocation']
    if not os.path.exists(fileLocation):
        os.makedirs(fileLocation)

# UI
class SNV(QtWidgets.QDialog):
    def __init__(self, fileType, sequenceNumber, shotNumber, assetName, pathScene):
        # Setup UI
        super(SNV, self).__init__()
        self.fileType = fileType # RND, ANM etc. To return back to CS object
        self.sequenceNumber = sequenceNumber
        self.shotNumber = shotNumber
        self.assetName = assetName
        ui_file = '{}/saveNextVersion_Warning.ui'.format(folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)

        # Setup label
        message = 'File exists!\n{}'.format(analyzeFliePath(pathScene)['fileName'])
        self.ui.lab_message.setText(message)

        # Setup window properties
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.ui)
        self.setLayout(mainLayout)
        self.resize(320, 60)  # resize window
        self.setWindowTitle('Create Sequences')  # Title Main window
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)

        # Setup buttons
        self.ui.btn_SNV.clicked.connect(self.SNV)
        self.ui.btn_SNV.clicked.connect(self.close)
        self.ui.btn_OVR.clicked.connect(self.OVR)
        self.ui.btn_OVR.clicked.connect(self.close)
        self.ui.btn_OVR.clicked.connect(self.close)
        self.ui.btn_ESC.clicked.connect(self.close)


    def SNV(self):
        createHip(self.fileType, self.sequenceNumber, self.shotNumber, self.assetName, catch='SNV')
        self.done(256) # return value to createHip() winSNV.exec_()

    def OVR(self):
        createHip(self.fileType, self.sequenceNumber, self.shotNumber, self.assetName, catch='OVR')
        self.done(256) # return value to createHip() winSNV.exec_()

class SNV2(QtWidgets.QDialog):
    def __init__(self, filePath, parentName):
        # Setup UI
        super(SNV2, self).__init__()
        self.filePath = filePath
        self.parentName = parentName # Name of the function from which SNV was launched
        ui_file = '{}/saveNextVersion_Warning.ui'.format(folderUI)
        self.ui = QtUiTools.QUiLoader().load(ui_file, parentWidget=self)
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        # Setup label
        message = 'File exists!\n{}'.format(analyzeFliePath(self.filePath )['fileName'])
        self.ui.lab_message.setText(message)

        # Setup buttons
        self.ui.btn_SNV.clicked.connect(self.SNV)
        self.ui.btn_SNV.clicked.connect(self.close)
        self.ui.btn_OVR.clicked.connect(self.OVR)
        self.ui.btn_OVR.clicked.connect(self.close)
        self.ui.btn_OVR.clicked.connect(self.close)
        self.ui.btn_ESC.clicked.connect(self.close)

    def SNV(self):
        eval("{}(None, pathScene=self.filePath, catch='SNV')".format(self.parentName))
        self.done(256)  # return value to parentName function winSNV.exec_()

    def OVR(self):
        eval("{}(None, pathScene=self.filePath, catch='OVR')".format(self.parentName))
        self.done(256)  # return value to parentName function winSNV.exec_()

