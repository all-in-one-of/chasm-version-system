import os
import os.path
import ConfigParser
import time
import node

class VersionedNode(node.Node):
	"""
	ABSTRACT. Inherits from Node. Representative of a project category folder.
	
	@author: Morgan Strong, Brian Kingery
	"""
	
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Define Functions	
	#Load versioning information
	def __loadMetaData(self, dirInfoFileName):
		parser = ConfigParser.ConfigParser()
		parser.read(os.path.join(self._fullPath, dirInfoFileName))
		if not parser.has_section("Versioning"):
			raise Exception("File corrupted: " + os.path.join(self._fullPath, dirInfoFileName))
		
		if parser.has_option("Versioning", "LatestVersion"):
			self._latestVersion = parser.get("Versioning", "LatestVersion")
		if parser.has_option("Versioning", "Locked"):
			self._locked = (parser.get("Versioning", "Locked") == "True")
		if parser.has_option("Versioning", "LastCheckoutTime"):
			self._lastCheckoutTime = time.strptime(parser.get("Versioning", "LastCheckoutTime"), "%a, %d %b %Y %I:%M:%S %p")
		if parser.has_option("Versioning", "LastCheckoutUser"):
			self._lastCheckoutUser = parser.get("Versioning", "LastCheckoutUser")
		if parser.has_option("Versioning", "LastCheckinTime"):
			self._lastCheckinTime = time.strptime(parser.get("Versioning", "LastCheckinTime"), "%a, %d %b %Y %I:%M:%S %p")
		if parser.has_option("Versioning", "LastCheckinUser"):
			self._lastCheckinUser = parser.get("Versioning", "LastCheckinUser")
	
	def checkIntegrity(self):
		if not os.path.exists(self._fullPath + "/src") or \
				not os.path.exists(os.path.join(self._fullPath, "inst")) or \
				not os.path.islink(os.path.join(self._fullPath, "inst", "latest")) or \
				not os.path.islink(os.path.join(self._fullPath, "inst", "stable")):
			raise Exception("Versioned Folder: " + self._fullPath + " is missing a critical folder/link.")
		if not os.path.exists(os.path.join(self._fullPath, "src", "v"+str(self._latestVersion))):
			raise Exception("Versioned Folder: " + self._name + "'s latest version number doesn't match any folder name in src.")
		return True
	
	def _loadChildren(self):
		#Load src and inst here...
		#May not need to do anything, but should at least override _loadChildren
		#from Node.
		return
	
# >>>>>>>>>>>>>>>>>>>>>>>>>>>> API Functions
	def getLatestVersion(self):
		return self._latestVersion
	
	def isLocked(self):
		return self._locked
	
	def getLastCheckoutTime(self):
		if isinstance(self._lastCheckoutTime, time.struct_time):
			return time.strftime("%a, %d %b %Y %I:%M:%S %p", self._lastCheckoutTime)
		else:
			return ""
	
	def getLastCheckoutUser(self):
		return self._lastCheckoutUser
	
	def getLastCheckinTime(self):
		if isinstance(self._lastCheckinTime, time.struct_time):
			return time.strftime("%a, %d %b %Y %I:%M:%S %p", self._lastCheckinTime)
		else:
			return ""
	
	def getLastCheckinUser(self):
		return self._lastCheckinUser
	
	def setLatestVersion(self, x):
		if not isinstance(x, int):
			raise Exception("The version number must be an integer.")
		else:
			self._latestVersion = x
	
	def setLocked(self, x):
		if not isinstance(x, bool):
			raise Exception("The node must be locked with a boolean.")
		else:
			self._locked = x
	
	def setLastCheckoutTime(self, x):
		if isinstance(x, str):
			self._lastCheckoutTime = time.strptime(x, "%a, %d %b %Y %I:%M:%S %p")
		elif isinstance(x, time.struct_time):
			self._lastCheckoutTime = x
		else:
			raise Exception("A time must be given as a time.struct_time or a string with the format: Thu, 28 Jun 2001 2:17:15 PM")
	
	def setLastCheckoutUser(self, x):
		if not isinstance(x, str):
			raise Exception("A user must be a string.")
		else:
			self._lastCheckoutUser = x
	
	def setLastCheckinTime(self, x):
		if isinstance(x, str):
			self._lastCheckinTime = time.strptime(x, "%a, %d %b %Y %I:%M:%S %p")
		elif isinstance(x, time.struct_time):
			self._lastCheckinTime = x
		else:
			raise Exception("A time must be given as a time.struct_time or a string with the format: Thu, 28 Jun 2001 2:17:15 PM")
	
	def setLastCheckinUser(self, x):
		if not isinstance(x, str):
			raise Exception("A user must be a string.")
		else:
			self._lastCheckinUser = x
		

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Initialize Node	
	#Constructor
	def __init__(self, path, dirInfoFileName):
		#Initialize basic variables
		super(VersionedNode, self).__init__(path)
		
		#Initialize VersionedNode variables.
		self._latestVersion = -1
		self._locked = False
		self._lastCheckoutTime = None
		self._lastCheckoutUser = ""
		self._lastCheckinTime = None
		self._lastCheckinUser = ""
		
		self.__loadMetaData(dirInfoFileName)
	
	def test(self):
		raise notImplementedError

"""
Methods not bound to an instance of the class:
"""
def getNullReference():
	"""@returns: The path to the .nullReference file used for symlinks"""
	if not os.path.exists(os.path.join(node.Project().getProjectDir(), '.nullReference')):
		nullRef = open(os.path.join(node.Project().getProjectDir(), '.nullReference'), "w")
		nullRef.write("#This is a null reference for symlinks.\n#Nothing has been installed.")
		nullRef.close()
	return os.path.join(node.Project().getProjectDir(), '.nullReference')

def updateConfigFile(filePath, configParser):
	"""
	Will update the config file specified by filePath with the contents of configParser
	@precondition: filePath is a valid path
	@precondition: confgParser is an instance of ConfigParser()
	"""
	with open(filePath, 'wb') as configFile:
		configParser.write(configFile)

def createNodeInfoFile(dirPath):
	"""
	Creates the .nodeInfo file in the directory specified by dirPath.
	The Node:Type must be set by concrete nodes
	@precondition: dirPath is a valid directory
	@postcondition: All sections/tags are created and set except "Type".
		"Type" must be set by concrete nodes.
	"""
	username = node.Project().getUserName()
	timestamp = time.strftime("%a, %d %b %Y %I:%M:%S %p", time.gmtime())
	
	nodeInfo = ConfigParser.ConfigParser()
	nodeInfo.add_section('Node')
	nodeInfo.set('Node', 'Type', '')
	
	nodeInfo.add_section('Versioning')
	nodeInfo.set('Versioning', 'LatestVersion', '0')
	nodeInfo.set('Versioning', 'Locked', 'False')
	nodeInfo.set('Versioning', 'LastCheckoutTime', timestamp)
	nodeInfo.set('Versioning', 'LastCheckoutUser', username)
	nodeInfo.set('Versioning', 'LastCheckinTime', timestamp)
	nodeInfo.set('Versioning', 'LastCheckinUser', username)
	
	updateConfigFile(os.path.join(dirPath, ".nodeInfo"), nodeInfo)

def createOnDisk(path, name):
	node.createOnDisk(path, name)
	newPath = os.path.join(path, name)
	os.mkdir(os.path.join(newPath, 'src'))
	os.mkdir(os.path.join(newPath, 'src', 'v0'))
	os.mkdir(os.path.join(newPath, 'inst'))
	#os.symlink(os.path.join(newPath, 'inst', 'null'), os.path.join(newPath, 'inst', 'latest'))
	#os.symlink(os.path.join(newPath, 'inst', 'null'), os.path.join(newPath, 'inst','stable'))
	os.symlink(os.path.join(newPath, 'inst', getNullReference()), os.path.join(newPath, 'inst', 'latest'))
	os.symlink(os.path.join(newPath, 'inst', getNullReference()), os.path.join(newPath, 'inst','stable'))
	
	createNodeInfoFile(newPath)