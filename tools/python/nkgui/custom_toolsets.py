# Toolsets - based on Vitaly Musatov's Shared Toolsets: https://github.com/greenvfx/toolsets
import os
import sys
import nuke
import nukescripts
import posixpath
import random
import string


TOOLSETS_FOLDERNAME = 'toolsets'

this_dir = os.path.join(os.path.dirname(__file__))
if 'tools' in this_dir:
  base_dir = this_dir.split('tools')[0]
  toolsets_dir = os.path.join(base_dir, TOOLSETS_FOLDERNAME)


SHARED_TOOLSET_PATH = toolsets_dir
FILE_FILTER = None

def setSharedToolSetsPath(path):
  global SHARED_TOOLSET_PATH
  SHARED_TOOLSET_PATH = path

def addFileFilter(externalFilter):
  global FILE_FILTER
  FILE_FILTER = externalFilter

#def removeToolSets():
#  nodes = nuke.menu('Nodes')
#  nodes.removeItem("ToolSets")

class CreateToolsetsPanel(nukescripts.PythonPanel):
  def __init__(self, fullFilePath, rename):
    
    self.rename = rename
    self.fullFilePath = fullFilePath

    if rename == False:
      self.namePanel = 'Create ToolSet'
      self.nameOkButton = 'Create'
    else:
      self.namePanel = 'Rename ToolSet'
      self.nameOkButton = 'Rename'
    
    nukescripts.PythonPanel.__init__( self, self.namePanel, 'uk.co.thefoundry.Toolset')
    
    # CREATE KNOBS
    self.userFolders = []
    fullPath = SHARED_TOOLSET_PATH
    self.buildFolderList(fullPath, '')


    self.menuItemChoice = nuke.CascadingEnumeration_Knob('menuItemChoice','SharedToolSets menu', ['root'] + self.userFolders )
    self.menuItemChoice.setTooltip("The menu location that the ToolSet will appear in. Specify 'root' to place the SharedToolSets in the main SharedToolSets menu.")
    self.menuPath = nuke.String_Knob('itemName', 'Menu item:')
    self.menuPath.setFlag(0x00001000)  
    self.menuPath.setTooltip("ToolSet name. Use the '/' character to create a new submenu for this ToolSet, eg to create a ToolSet named 'Basic3D' and place it in a new submenu '3D', type '3D/Basic3D'. Once created the 3D menu will appear in the ToolSet menu.")
    self.okButton = nuke.PyScript_Knob (self.nameOkButton.lower(), self.nameOkButton)
    #self.okButton.setToolTip("Create a ToolSet from the currently selected nodes with the given name")
    self.okButton.setFlag(0x00001000)
    self.cancelButton = nuke.PyScript_Knob ('cancel', 'Cancel')
    self.space = nuke.Text_Knob("space", "", "")
    self.infoText = nuke.Text_Knob('infoText', '<span style="color:orange">/ - create submenus,</span>',  '<span style="color:orange">example: newMenu/myNewToolSet</span>')

    # ADD KNOBS
    self.addKnob(self.menuItemChoice)
    self.addKnob(self.menuPath)
    self.addKnob(self.okButton)
    self.addKnob(self.cancelButton)
    self.addKnob(self.space)
    self.addKnob(self.infoText)

    if rename == True:
      toolSetPath = fullFilePath.replace(SHARED_TOOLSET_PATH + "/", '') 
      toolSetPath = toolSetPath.replace(".nk", '') 
      self.menuPath.setValue(toolSetPath)

  #COMMENT:  BUILD A LIST Of PRE_CREATED FOLDER LOCATIONS
  def buildFolderList(self, fullPath, menuPath):
    filecontents = sorted(os.listdir(fullPath), key=str.lower)
    for group in filecontents:
      if os.path.isdir(os.path.join(fullPath, group)):
        self.userFolders.append(menuPath + group)
        self.buildFolderList(fullPath + '/' + group, menuPath + group + '/')              

  def createPreset(self):
    if self.renameCreateSharedToolset(str(self.menuPath.value()), False):
      self.finishModalDialog( True )
  
  def renamePreset(self):
    if self.renameCreateSharedToolset(str(self.menuPath.value()), True):
      self.finishModalDialog( True )
    
  def renameCreateSharedToolset(self, name, rename):
    ret = False
    
    nameList = name.split('/')
    fileName = nameList[-1]
    
    del nameList[-1]
    dirs = '/'.join(nameList)
    
    fullPath = posixpath.join(SHARED_TOOLSET_PATH, dirs)
    
    try:
      if not os.path.isdir(fullPath):
        os.makedirs( fullPath )
      
      filePath = posixpath.join(fullPath, fileName + '.nk')
      
      if not os.path.exists(filePath):
        if self.rename == True:
          os.rename(self.fullFilePath, filePath)
        else:
          # create way
          nuke.nodeCopy(filePath)

      elif nuke.ask('Overwrite existing \n %s?' % filePath):
        if self.rename == True:
          os.remove(filePath)
          os.rename(self.fullFilePath, filePath)
        else:
          # create way
          nuke.nodeCopy(filePath)

      ret = True
    except:
      ret = False
    return ret

  def getPresetPath(self):

    #COMMENT: Added a bit of usability. Let's preserve a toolset's name
    tempListToolsetName = self.menuPath.value().split('/')
    tempToolsetName = tempListToolsetName[-1]

    if str(self.menuItemChoice.value()) == "root":
      self.menuPath.setValue( ""+ tempToolsetName)
    else:
      self.menuPath.setValue(self.menuItemChoice.value() + "/" + tempToolsetName)

  def knobChanged( self, knob ):
    if knob == self.okButton:
      if self.rename == True:
        self.renamePreset()
      else:
        self.createPreset()
    elif knob == self.cancelButton:
      self.finishModalDialog( False )
    elif knob == self.menuItemChoice:
      self.getPresetPath()

# NUKESCRIPT FUNCTIONS    
def renameToolset(fullFilePath):
  p = CreateToolsetsPanel(fullFilePath, True)
  p.showModalDialog()
  rootPath = SHARED_TOOLSET_PATH
  checkForEmptyToolsetDirectories(rootPath)
  refreshToolsetsMenu()
  print fullFilePath
    
def addToolsetsPanel():
  res = False
  if nuke.nodesSelected() == True:
    res = CreateToolsetsPanel(None, False).showModalDialog()
    #COMMENT: now force a rebuild of the menu
    refreshToolsetsMenu()
  else:
    nuke.message("No nodes are selected")
  return res  
  
def deleteToolset(rootPath, fileName):
  if nuke.ask('Are you sure you want to delete ToolSet %s?' %fileName):
    os.remove(fileName)
    #COMMENT: if this was the last file in this directory, the folder will need to be deleted.
    # Walk the directory tree from the root and recursively delete empty directories
    checkForEmptyToolsetDirectories(rootPath)
    #COMMENT: now force a rebuild of the menu
    refreshToolsetsMenu()

def checkForEmptyToolsetDirectories(currPath):
  removed = True
  while removed == True:
    removed = False
    for root, dirs, files in os.walk(currPath):
      if files == [] and dirs == []:
        if root != SHARED_TOOLSET_PATH:
          os.rmdir(root)
          removed = True
        
def refreshToolsetsMenu():  
  toolbar = nuke.menu("Nodes")
  m = toolbar.findItem("toolsets")
  if m != None:
    m.clearMenu()
    createToolsetsMenu(toolbar)

def createToolsetsMenu(toolbar):
  m = toolbar.addMenu(name = "toolsets", icon = "Glint.png")
  m.addCommand("Create", "custom_toolsets.addToolsetsPanel()", "", icon="ToolsetCreate.png")
  m.addCommand("-", "", "")
  if populateToolsetsMenu(m, False):
    m.addCommand("-", "", "")  
    n = m.addMenu("Modify")
    populateToolsetsMenu(n, True)
  m.addCommand('Refresh', 'custom_toolsets.refreshToolsetsMenu()')

def traversePluginPaths(m, delete, allToolsetsList, isLocal):
  ret = False
  fullPath = SHARED_TOOLSET_PATH
  if createToolsetMenuItems(m, fullPath, fullPath, delete, allToolsetsList, isLocal):
      ret = True
  return ret

def populateToolsetsMenu(m, delete):
  ret = False
  allToolsetsList = []
  #COMMENT: now do shared toolsets like the local .nuke  
  if traversePluginPaths(m, delete, allToolsetsList, True):
    ret = True
  return ret   

def randomStringDigits(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

#COMMENT: wrapper around loadToolset
def toolsetLoader(fullFileName):
    if FILE_FILTER != None:
        data = fileFilter(fullFileName, FILE_FILTER)
        # SAVING TEMPORAL TOOLSET | instead of 
        #QApplication.clipboard().setText(data)
        #nuke.nodePaste("%clipboard%") is craching with big files BUG
        randomPostfix = randomStringDigits(10)
        randomName = posixpath.join( SHARED_TOOLSET_PATH , "temp_toolset_%s.nk" % randomPostfix)
        saveTempToolSet = open(randomName,"w+")
        saveTempToolSet.write(data)
        saveTempToolSet.close()
        nuke.loadToolset(randomName)
        os.remove(randomName)
    else:
        nuke.loadToolset(fullFileName)
    return True

#COMMENT: modify file before loading 
def fileFilter(fileName, filterFunc):
    with open(fileName) as f:
        content = f.readlines()
    modifiedContentList = []
    for line in content:
        if "file" in line:
            line = filterFunc(line)
        modifiedContentList.append(line)
    modifiedContent = "".join(modifiedContentList)
    return modifiedContent

#COMMENT: Main function, construct menuName
def createToolsetMenuItems(m, rootPath, fullPath, delete, allToolsetsList, isLocal):
  #TODO: CLEAN THIS FUNCTION

  filecontents = sorted(os.listdir(fullPath), key=str.lower)
  excludePaths = nuke.getToolsetExcludePaths()
  #COMMENT: First list all directories
  retval = False
  if filecontents != []:
    for group in filecontents:
      newPath = "/".join([fullPath, group])
      ignore = False
      if newPath.find(".svn") != -1:
        ignore = True
      else:
        for i in excludePaths:
          i = i.replace('\\', '/')
          if newPath.find(i) != -1:
            ignore = True
            break
      if os.path.isdir(newPath) and not ignore:
        menuName = group
        if isLocal and (menuName in allToolsetsList):
          menuName = "[user] " + menuName
        elif not isLocal:
          allToolsetsList.append(menuName)
        n = m.addMenu(menuName)
        retval = createToolsetMenuItems(n, rootPath, "/".join([fullPath, group]), delete, allToolsetsList, isLocal)
        #COMMENT: if we are deleting, and the sub directory is now empty, delete the directory also
        if delete and os.listdir(fullPath)==[]:
          os.rmdir(fullPath)
    # Now list individual files
    for group in filecontents:
      fullFileName = "/".join([fullPath, group])
      if not os.path.isdir(fullFileName):
        
        #COMMENT: delete file with an extention ".nk~" created by edit.
        if ".nk~" in group:
          os.remove(fullFileName)
        
        extPos = group.find(".nk")
        if extPos != -1 and extPos == len(group) - 3:
          group = group.replace('.nk', '')
          if delete:
            subM = m.addMenu(group)
            subM.addCommand("Edit", 'nuke.scriptOpen("%s")' % fullFileName, "")
            subM.addCommand("Rename", 'custom_toolsets.renameToolset("%s")' % fullFileName, "")
            subM.addCommand("-", "", "")
            subM.addCommand("Delete", 'custom_toolsets.deleteToolset("%s", "%s")' % (rootPath, fullFileName), "")
            retval = True
          else:
            #COMMENT: get the filename below toolsets
            i = fullFileName.find("toolsets/")
            if i != -1:
              subfilename = fullFileName[i:]
            else:
              #COMMENT: should never happen, but just in case ...
              subfilename = fullfilename
            if isLocal and (subfilename in allToolsetsList):
              #COMMENT: if we've already appended [user] to the menu name, don't need it on the filename
              if (i != -1) and subfilename[len("toolsets/"):].find("/") == -1:
                group = "[user] " + group
            elif not isLocal:
              allToolsetsList.append(subfilename)

            #TODO: get ref module name, now it is static linking
            #current_module = sys.modules[__name__]
            #print current_module
            m.addCommand(group, 'custom_toolsets.toolsetLoader("%s")' %  fullFileName, "")            
            retval = True
  return retval

createToolsetsMenu(nuke.menu('Nodes'))
refreshToolsetsMenu()