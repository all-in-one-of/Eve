'''
256 Pipeline Tools
DNA of EVE: common core to be used in misc modules

General notes.
Versions and publishing. Before we implement Shotgun and develop a publishing mechanizm with it
we will consider LATEST version of file published (which needs to be used).

'''

import os
import json
import glob

# DEFINE COMMON VARIABLES AND PATHS
# Pipeline items
pipelineName = 'Eve'
extensionHoudini = 'hiplc'
extensionRender = 'exr'
extensionFlipbook = 'jpg'
extensionCacheAnim = 'bgeo.sc'
extensionCamera = 'hiplc'


# FILE TYPES dictionary. Used for:
#   - define file name prefixes in file name patterns
#   - define file type in buildFilePath()
fileTypes = {'animationScene': 'ANM',
             'renderScene': 'RND',
             'renderSequence': 'EXR',
             'flipbookSequence': 'FBK',
             'cacheAnim': 'CAN',
             'cacheCamera': 'CAM'}

# Asset types
assetTypes = ['Character', 'Environment', 'Prop', 'FX']

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

filePathAnimation =       '{0}/scenes/ANIMATION/{1}/SHOT_{2}/{3}'          # Animation scene path
filePathRender =          '{0}/scenes/RENDER/{1}/SHOT_{2}/{3}'             # Render scene path
filePathSequenceRender =  '{0}/render/{1}/SHOT_{2}/{3}/{4}'                # Render sequence path
filePathSequenceCache =   '$JOB/geo/SHOTS/{0}/SHOT_{1}/{2}/GEO/{3}/{4}'    # Characters geometry cache path
filePathCamera =          '{0}/geo/SHOTS/{1}/SHOT_{2}/CAM/{3}'             # Camera ANM >> RND path

# HOUDINI SCENE CONTENT
# Currently string oriented.
# Another option is to use custom UID (node.setUserData()) for each node and save it in database. Potentially TBD.

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
                "sg_cut_out": 0,
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

    # Disassemble file path
    filePathData = analyzeFliePath(filePath)
    fileLocation= filePathData['fileLocation']
    fileCode = filePathData['fileCode']
    fileExtension = filePathData['fileExtension']

    listExisted = glob.glob('{0}{1}_*.{2}'.format(fileLocation, fileCode, fileExtension))
    fileVersionLatest = extractLatestVersionFile(listExisted)
    filePathLatestVersion = '{0}{1}_{2}.{3}'.format(fileLocation, fileCode, fileVersionLatest, fileExtension)

    # print 'dna.buildPathLatestVersion [filePathLatestVersion] = {}'.format(filePathLatestVersion)

    return filePathLatestVersion

def buildFilePath(version, fileType, scenePath=None, characterName=None, sequenceNumber=None, shotNumber=None):
    '''
    Generate and return a full path to a file <filePath> (string).
    Rely on # FILE NAMES AND PATHS PATTERNS
    There are 2 options to build a path:
        - based on Houdini scene name (in addition to file type and version)
        - based on Scene and Shot code (in addition to file type and version)

    :param version: version of the file
    :param fileType: type of file to generate (string), 'ANM', 'RND' etc
    :param scenePath: Full path to Houdini scene
    :param characterName: name of character asset
    :param sequenceNumber: Episode number (sequence number = sequence code) (010)
    :param shotNumber: Shot number (010)
    :return filePath: generated full path (string)
    '''

    if scenePath != None:
        filePathData = analyzeFliePath(scenePath)
        sequenceNumber = filePathData['sequenceNumber']
        shotNumber = filePathData['shotNumber']

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
        filePath = filePathSequenceCache.format(sequenceNumber, shotNumber, characterName, version, fileName)

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

def loadGenes(genesFile):
    return json.load(open(genesFile))

def checkExistsingEntity(genesFile, name):
    '''
    Check if entity (asset, shot, sequence) with provided name exist in database
    :param name:
    :return:
    '''

    genes = loadGenes(genesFile)
    for asset in genes:
        if asset['code'] == name:
            return True

def deleteAssets(genesFileAssets, assetNames):
    genesAssets = loadGenes(genesFileAssets)
    genesAssetFiltered = []
    for asset in genesAssets:
        if not asset['code'] in assetNames:
            genesAssetFiltered.append(asset)

    json.dump(genesAssetFiltered, open(genesFileAssets, 'w'), indent=4)

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

    if shotData == None:
        print '>> There is no data for shot E{0}_S{1}'.format(sequenceNumber, shotNumber)
    else:
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
            if assetData['code'] == asset['name']:
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

    if assetType == 'Environment':
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

def getShotGene(sequenceNumber, shotNumber, genesShots, genesAssets):
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
        environmentData = getAssetDataByType(assetsData, 'Environment')
        charactersData = getAssetDataByType(assetsData, 'Character')
        fxData = getAssetDataByType(assetsData, 'FX')

        shotGene['shotData'] = shotData
        # shotGene['assetsData'] = assetsData
        shotGene['environmentData'] = environmentData
        shotGene['charactersData'] = charactersData
        shotGene['fxData'] = fxData

        return shotGene

# SCENE MANIPULATIONS

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

    CONTAINER = parent.createNode('geo',name)

    # Display as bounding box
    CONTAINER.parm('viewportlod').set(bbox)

    # Set display flag
    CONTAINER.setDisplayFlag(disp)

    # Turn ON motion blur
    if mb is not None:
        CONTAINER.parm('geo_velocityblur').set(1)

    print '>>>> Created Container: {0}'.format(name)

    return CONTAINER

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
