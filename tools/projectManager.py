'''
256 Pipeline tools
EVE - Houdini pipeline for VFX production

Create folder structure for the project and copy pipeline files into it
'''

# Common modules import
import os
import sys
import shutil
import webbrowser

# Py Side import
from PySide.QtGui import *
from PySide import QtUiTools, QtCore

# COMMON SCRIPT VARIABLES
rootPipeline = os.path.dirname(os.path.dirname(__file__)).replace('\\','/')
DOCS = 'https://github.com/kiryha/Eve/wiki/'
# Folder names to skip when run copyTree
filterFolders = ['.dev', '.git', '.idea', 'hips']
# File names to skip when run copyTree
filterFiles = []
uiFile_main = 'P:/Eve/ui/projectManager_main.ui'
uiFile_warning = 'P:/Eve/ui/projectManager_warning.ui'
houdiniBuild = '17.0.459'

# PROJECT FOLDER STRUCTURE
# Shots structure
SHOTS = [
    ['010',[
        ['SHOT_010', []],
        ['SHOT_020', []]
    ]]
        ]
# Assets structure
ASSETS = [
    ['CHARACTERS', []],
    ['ENVIRONMENTS', []],
    ['PROPS', []],
    ['STATIC', []]
        ]
# Types structure
TYPES = [
    ['ASSETS', ASSETS],
    ['SHOTS', SHOTS]
    ]
# Formats structure
FORMATS = [
    ['ABC', []],
    ['GEO', []],
    ['FBX', []]
    ]
# Folders structure
FOLDERS = [
    ['EDIT', [
        ['OUT', []],
        ['PROJECT', []]
    ]],
    ['PREP', [
        ['ART', []],
        ['SRC', []],
        ['PIPELINE', []],
        ]],
    ['PROD', [
        ['2D', [
            ['COMP', SHOTS],
            ['RENDER', SHOTS]
        ]],
        ['3D', [
            ['lib', [
                ['ANIMATION', []],
                ['MATERIALS', ASSETS] # Or TYPES ?
            ]],
            ['fx',TYPES],
            ['caches',TYPES],
            ['hda', [
                ['ASSETS', ASSETS],
                ['FX', TYPES],
             ]],
            ['render', SHOTS],
            ['scenes', [
                ['ASSETS', ASSETS],
                ['ANIMATION', SHOTS],
                ['FX', TYPES],
                ['LAYOUT', SHOTS],
                ['LOOKDEV', TYPES],
                ['RENDER', SHOTS]
            ]],
            ['textures', TYPES],
        ]],
    ]]
    ]


# WARNING WINDOW
class Warning(QWidget):
    '''
    Warning window.
    Show existing project path,
    send back to a parent class (CreateProject.createProject function) user choice (OK or NO)
    '''
    def __init__(self, parent, message):
        super(Warning, self).__init__()

        # SETUP UI
        ui_file = QtCore.QFile(uiFile_warning)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.window = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()

        self.parent = parent
        self.lab_warning = self.window.findChild(QLabel, 'lab_warning')
        self.lab_warning.setText('Folder <{0}> exists!'.format(message))
        self.btn_proceed = self.window.findChild(QPushButton, 'btn_proceed')
        self.btn_cancel = self.window.findChild(QPushButton, 'btn_cancel')

        # SETUP FUNCTIONALITY
        self.btn_proceed.clicked.connect(self.proceed)
        self.btn_proceed.clicked.connect(self.window.close)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_cancel.clicked.connect(self.window.close)

    def proceed(self):
        # PROCEED button
        ProjectManager.createProject(self.parent, 'OK')

    def cancel(self):
        # CANCEL button
        ProjectManager.createProject(self.parent, 'NO')

# MAIN MODULE
class ProjectManager(QWidget):
    '''
    Create Project MAIN MODULE
    Set project name and location in UI, create folder structure, copy pipeline files
    '''

    # GLOBAL VARIABLES
    shots = {} # '010': ['SHOT_010', 'SHOT_020']
    assets = {'CHARACTERS': [], 'ENVIRONMENTS': [], 'PROPS': [], 'STATIC':[]}

    def __init__(self):
        super(ProjectManager, self).__init__()
        # SETUP UI
        ui_file = QtCore.QFile(uiFile_main)
        ui_file.open(QtCore.QFile.ReadOnly)
        self.window = QtUiTools.QUiLoader().load(ui_file)
        ui_file.close()

        self.act_docs = self.window.findChild(QAction, 'act_docs')
        self.act_help = self.window.findChild(QAction, 'act_help')
        self.btn_setFolder = self.window.findChild(QPushButton, 'btn_setFolder')
        self.lin_name = self.window.findChild(QLineEdit, 'lin_name')
        self.lab_path = self.window.findChild(QLabel, 'lab_path')
        self.lin_options = self.window.findChild(QLineEdit, 'lin_options')
        self.btn_create = self.window.findChild(QPushButton, 'btn_create')


        self.lab_path.setText('C:')
        self.lin_name.setText('MY_PROJECT')
        self.lin_options.setText(houdiniBuild)

        # SETUP COMMON VARIABLES
        self.projectFolder = None # Project location
        self.projectName = None # Project name

        # SETUP FUNCTIONALITY
        self.act_docs.triggered.connect(lambda:  self.help(DOCS))
        self.act_help.triggered.connect(lambda:  self.help('{0}Tools#project-manager'.format(DOCS)))
        self.btn_create.clicked.connect(self.createProject)
        self.btn_setFolder.clicked.connect(self.selectProjectFolder)

        self.lin_name.textChanged.connect(self.updateProjectPath)
        self.buildProjectPath()

    def help(self, URL):
        '''
        Open pipeline documentation in web browser
        '''
        webbrowser.open(URL)

    def selectProjectFolder(self):
        '''
        Let user to select project location
        '''
        self.projectFolder = QFileDialog.getExistingDirectory(self, 'Select folder to store the project', 'C:/').replace('\\', '/')
        self.lab_path.setText(self.projectFolder)
        self.buildProjectPath() # Update path in UI

    def buildProjectPath(self):
        '''
        Create a string with full path to a project (project location + project name)
        '''
        self.projectFolder = self.lab_path.text() # Get project location
        self.updateProjectPath() # Set path in UI

    def updateProjectPath(self):
        '''
        Modify project path string in UI when user change NAME
        '''
        projectName = self.lin_name.text().replace(' ', '_') # Get project name from UI
        self.lab_path.setText('{0}/{1}'.format(self.projectFolder, projectName)) # Build full project path and update UI

    def createFolder(self, path):
        '''
        Create folder from input path
        :param path: Path to create folder (C:/TEMP)
        '''
        if not os.path.exists(path):
            os.makedirs(path)

    def createFolders(self, pathRoot, list):
        '''
        Recursively build folder structure based on template (folders list)
        :param pathRoot:
        :param list:
        :return:
        '''

        if list:
            for folder in list:
                folderName = folder[0]
                path = '{}/{}'.format(pathRoot, folderName)
                self.createFolder(path)
                self.createFolders(path, folder[1])

    def copyTree(self, SRC, NEW):
        '''
        Copy all folder content RECURSION.
        SRC - source folder to copy from
        NEW - destination to copy all content from SRC
        '''
        if not os.path.exists(NEW):
            os.makedirs(NEW)
        for item in os.listdir(SRC):
            src = os.path.join(SRC, item).replace('\\', '/')
            new = os.path.join(NEW, item).replace('\\', '/')
            if os.path.isdir(src):
                folder = item.split('/')[-1]
                if not folder in filterFolders:
                    self.copyTree(src, new)
            else:
                if not item in filterFiles:
                    if not os.path.exists(new):
                        shutil.copy2(src, new)

    def createProject_HDD(self, projectRoot):
        '''
        Create project on HDD and copy/create pipeline files:
            - Houdini launcher
            - database (genes)
            - houdini settings
        :return:
        '''

        # Create nested folder structure
        self.createFolders(projectRoot, FOLDERS)

        # Create Houdini launcher
        launcherNamePY_SRC = '{}/src/runHoudini.py'.format(rootPipeline)
        launcherNamePY_DST = '{}/PREP/PIPELINE/runHoudini.py'.format(projectRoot)
        launcherNameBAT_DST = '{}/PREP/PIPELINE/runHoudini.bat'.format(projectRoot)

        launcherPY_SRC = open(launcherNamePY_SRC, 'r')
        launcherPY_DST = open(launcherNamePY_DST, 'w')
        launcherBAT_DST = open(launcherNameBAT_DST, 'w')

        # PY
        for line in launcherPY_SRC:
            # Edit per project variables
            if line.startswith('rootPipeline ='):
                line = "rootPipeline = '{}'\n".format(rootPipeline)
            elif line.startswith('build ='):
                line = "build = '{}'\n".format(self.lin_options.text())

            launcherPY_DST.write(line)

        # BAT
        launcherBAT_DST.write('"C:\Python27\python.exe" %cd%\\runHoudini.py')

        launcherPY_SRC.close()
        launcherPY_DST.close()
        launcherBAT_DST.close()

        # Create genes


        # Copy Houdini prefs
        self.copyTree('{}/src/houdini'.format(rootPipeline), '{}/PREP/PIPELINE/houdini'.format(projectRoot))

        print '>> Folder structure with pipeline files created in {0}/'.format(projectRoot)

    def createProject(self, catchWarning = None):
        '''
        Create new project on HDD and in Shotgun:
        :param catchWarning: returned value from Warning class (OK or NO)
        '''

        projectRoot = self.lab_path.text()
        projectName = self.lin_name.text()

        # HDD
        # Create folder structure on HDD and copy pipeline files

        if os.path.exists(projectRoot):
            # If project folder already exists
            if catchWarning == None:
                # Run warning dialog
                self.warning = Warning(self, projectRoot)  # Run SNV window
                win = self.warning.window.show()

                if not win:  # Prevent script to run further before user reply in warning UI
                    return

            elif catchWarning == 'OK':
                # Create project structure on HDD in existing folder
                self.createProject_HDD(projectRoot)
            else:
                return
        else:
            # Create new project structure on HDD
            self.createFolder(projectRoot)
            self.createProject_HDD(projectRoot)

        # Report about creation
        print '>> Project creation complete!'
        print '>> Run Houdini with {0}/PREP/PIPELINE/runHoudini.bat and create a magic!'.format(projectRoot)

# Run Create Project script
app = QApplication([])
CP = ProjectManager()
CP.window.show()
app.exec_()
