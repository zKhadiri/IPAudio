from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Screens.InfoBar import MoviePlayer, InfoBar
from enigma import eServiceReference, iServiceInformation
from Components.MenuList import MenuList
from GlobalActions import globalActionMap
try:
	from keymapparser import readKeymap
except:
	from Components.ActionMap import loadKeymap as readKeymap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigInteger, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigSubsection ,ConfigText ,configfile , ConfigDirectory
from Components.ConfigList import ConfigList, ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import eConsoleAppContainer , getDesktop , eTimer , eListboxPythonMultiContent , gFont , RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_VALIGN_CENTER , RT_WRAP
from Components.ServiceEventTracker import ServiceEventTracker
from Components.MultiContent import MultiContentEntryText
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from enigma import iPlayableService 
try:
	from enigma import eAlsaOutput
	HAVE_EALSA = True
except ImportError:
	HAVE_EALSA = False
from Plugins.Extensions.IPAudio.Console2 import Console2
import os, time ,sys
from Components.Sources.List import List
from Screens.Standby import TryQuitMainloop
from .skin import *

config.plugins.IPAudio = ConfigSubsection()
config.plugins.IPAudio.currentService = ConfigText()
config.plugins.IPAudio.sync = ConfigSelection(default="alsasink", choices = [
				("alsasink", _("alsasink")),
				("osssink", _("osssink")),
				("autoaudiosink", _("autoaudiosink")),
			])
config.plugins.IPAudio.skin = ConfigSelection(default='Icone', choices=[
				('Icone', _('Icone Skin')),
				('light', _('light Skin'))
			])
config.plugins.IPAudio.update = ConfigYesNo(default=True)
config.plugins.IPAudio.mainmenu = ConfigYesNo(default=False)
config.plugins.IPAudio.keepaudio = ConfigYesNo(default=False)
config.plugins.IPAudio.running = ConfigText()
config.plugins.IPAudio.lastidx = ConfigText()

REDC =  '\033[31m'
ENDC = '\033[m'

def cprint(text):                                                               
	print(REDC+text+ENDC)

def trace_error():
	import sys
	import traceback
	try:
		traceback.print_exc(file=sys.stdout)
		traceback.print_exc(file=open('/tmp/IPAudio.log', 'a'))
	except:
		pass
	
	
def getPlaylist():
	import json
	if fileExists('/etc/enigma2/ipaudio.json'):
		with open('/etc/enigma2/ipaudio.json', 'r')as f:
			try:
				return json.loads(f.read())
			except ValueError:
				trace_error()
	else:
		return None
	
def getversioninfo():
	import os
	currversion = '1.0'
	version_file = '/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/version'
	if os.path.exists(version_file):
		try:
			fp = open(version_file, 'r').readlines()
			for line in fp:
				if 'version' in line:
					currversion = line.split('=')[1].strip()
		except:
			pass
	return (currversion)

Ver = getversioninfo()

def get_Lecteur():
	Leteur = config.plugins.IPAudio.sync.value
	return Leteur

def is_compatible():
	if fileExists('/proc/stb/info/boxtype') and open('/proc/stb/info/boxtype').read().strip() in ('sf8008','sf8008m','viper4kv20','beyonwizv2','ustym4kpro','gbtrio4k','spider-x',):
		return True
	else:
		return False

def getDesktopSize():
	s = getDesktop(0).size()
	return (s.width(), s.height())


def isHD():
	desktopSize = getDesktopSize()
	return desktopSize[0] == 1280

class IPAudioSetup(Screen, ConfigListScreen):
	
	def __init__(self, session):
		Screen.__init__(self, session)
		if config.plugins.IPAudio.skin.value == 'Icone':
			self.skin = SKIN_IPAudioSetup_ICONE
		elif config.plugins.IPAudio.skin.value == 'light':
			self.skin = SKIN_IPAudioSetup_Light
		self.skinName = ["IPAudioSetup"]
		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel":self.keyCancel,
				"save":self.apply,
				"ok":self.apply,
			}, -2)
		self["green_key"] = StaticText(_("Save"))
		self["red_key"] = StaticText(_("Cancel"))
		self.configChanged = False
		self.createSetup()
		
	def createSetup(self):
		self.configChanged = True
		self.changeskin = config.plugins.IPAudio.skin.value
		self.list = [getConfigListEntry(_("Sync Audio using"), config.plugins.IPAudio.sync)]
		self.list.append(getConfigListEntry(_("Keep original channel audio"), config.plugins.IPAudio.keepaudio))
		self.list.append(getConfigListEntry(_("Enable/Disable online update"), config.plugins.IPAudio.update))
		self.list.append(getConfigListEntry(_("Show IPAudio in main menu"), config.plugins.IPAudio.mainmenu))
		self.list.append(getConfigListEntry(_("Select Your IPAudio Skin"), config.plugins.IPAudio.skin))
		self["config"].list = self.list
		self["config"].setList(self.list)
		
	def apply(self):
		for x in self["config"].list:
			if len(x)>1:
				x[1].save()
		configfile.save()
		self.close(True)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

class IPAudioScreen(Screen):
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		if config.plugins.IPAudio.skin.value == 'Icone':
			self.skin = SKIN_IPAudioScreen_ICONE
		elif config.plugins.IPAudio.skin.value == 'light':
			self.skin = SKIN_IPAudioScreen_Light
		self.choices = ['server1','c+fr','world','mixlr','playlist']
		self.plIndex = 0
		self['server'] = Label()
		self['sync'] = Label()
		self['sync'].setText('Audio sink : '+get_Lecteur())
		self["list"] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		if isHD():
			self["list"].l.setItemHeight(50)
			self["list"].l.setFont(0, gFont('Regular', 20))
		else:
			self["list"].l.setItemHeight(58)
			self["list"].l.setFont(0, gFont('Regular', 28))
		self["key_green"] = Button(_("Reset Audio"))
		self["myActionMap"] = ActionMap(["OkCancelActions", "ColorActions","WizardActions","MenuActions"],
		{
			"ok": self.ok,
			"cancel": self.exit,
			"green": self.resetAudio,
			"right":self.right,
			"left":self.left,
			"menu":self.Config_lctr,
		}, -1)
		self.alsa = None
		if HAVE_EALSA:
			self.alsa = eAlsaOutput.getInstance()       
		self.container = eConsoleAppContainer()
		self.Audiocontainer = eConsoleAppContainer()
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		if config.plugins.IPAudio.update.value:
			self.checkupdates()
		self.onShown.append(self.onWindowShow)

	def onWindowShow(self):
		self.onShown.remove(self.onWindowShow)
		if config.plugins.IPAudio.lastidx.value:
			last_playlist,last_channel = map(int,config.plugins.IPAudio.lastidx.value.split(','))
			self.plIndex = last_playlist
			self.changePlaylist()
			self["list"].moveToIndex(last_channel)
		else:
			self.setPlaylist()
  
	def checkupdates(self):
		try:
			from twisted.web.client import getPage, error
			url = 'http://linuxsat5.webhop.info/ipaudio/installer.sh'
			getPage(str.encode(url), headers={b'Content-Type': b'application/x-www-form-urlencoded'}).addCallback(self.getData).addErrback(self.addErrback)
		except:
			pass

	def getData(self, data):
		data = data.encode("utf-8")
		if data:
			lines=data.split("\n")
			for line in lines:
				if line.startswith("version"):
				   self.new_version = line.split("=")[1]
				if line.startswith("description"):
				   self.new_description = line.split("=")[1]
				   break
		if float(Ver) == float(self.new_version) or float(Ver)>float(self.new_version):
			pass
		else :
			new_version = self.new_version
			new_description = self.new_description
			self.session.openWithCallback(self.installupdate, MessageBox, _('New version %s is available.\n\n%s.\n\nDo you want to install it now.' % (self.new_version, self.new_description)), MessageBox.TYPE_YESNO)

	def installupdate(self,answer=False):
		if answer:
			cmdlist = []
			cmdlist.append('wget -q "--no-check-certificate" http://linuxsat5.webhop.info/ipaudio/installer.sh -O - | /bin/sh')
			self.session.open(Console2, title='Update IPAudio', cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)

	def myCallback(self,result=None):
		return

	def getMixlerUrls(self):
		try:
			from twisted.web.client import getPage, error
			url = 'http://linuxsat5.webhop.info/mixlr'
			getPage(str.encode(url), headers={b'Content-Type': b'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.addErrback)
		except:
			pass
			
	def addErrback(self,error=None):
		pass
		
	def parseData(self, data):
		list = []
		data = data.decode("utf-8")
		for line in data.split('\n'):
			list.append((str(line.split('||')[0]), line.split('||')[1]))
			self["list"].l.setList([])
			self["list"].l.setList(self.iniMenu(list))
			self["list"].show()
			self.radioList = list
			
	def right(self):
		self['sync'].setText('Audio sink : '+get_Lecteur())
		self.plIndex +=1
		self.changePlaylist()
		
	def left(self):
		self['sync'].setText('Audio sink : '+get_Lecteur())
		self.plIndex -=1
		self.changePlaylist()
		
	def changePlaylist(self):
		if self.plIndex > (len(self.choices)-1):
		   self.plIndex = 0
		if self.plIndex < 0:
		   self.plIndex = len(self.choices)-1
		self.setPlaylist()
		
		
	def setPlaylist(self):
		if self.choices[self.plIndex] == 'world':
			list = []
			list.append(('BS YSF BACKUP (During live games only)', '-ys'))
			list.append(('BS MT BACKUP (During live games only)', '-mt'))
			self["list"].l.setList(self.iniMenu(list))
			self["list"].show()
			self.radioList = list
			self["server"].setText('World of enigma2')
   
		elif self.choices[self.plIndex] == 'c+fr':
			list = []
			list.append(('c+', '-bs1'))
			list.append(('c+sport', '-bs2'))
			list.append(('bs1 fr', '-bs3'))
			list.append(('bs2 fr', '-bs4'))
			list.append(('bs3 fr', '-bs5'))
			self["list"].l.setList(self.iniMenu(list))
			self["list"].show()
			self.radioList = list
			self["server"].setText('C+FR')

		elif self.choices[self.plIndex] == 'server1':
			list = []
			list.append(('BS1 PREM', '-en8'))
			list.append(('BS2 PREM', '-en9'))
			list.append(('BS3 PREM', '-en10'))
			list.append(('BS1 XTRA', '-xt1'))
			list.append(('BS2 XTRA', '-xt2'))
			list.append(('BS1', '-en1'))
			list.append(('BS2', '-en2'))
			list.append(('BS3', '-en3'))
			list.append(('BS4', '-en4'))
			list.append(('BS5', '-en5'))
			list.append(('BS6', '-en6'))
			list.append(('BS7', '-en7'))
			self["list"].l.setList(self.iniMenu(list))
			self.radioList = list
			self["list"].show()
			self["server"].setText('Server A')

		elif self.choices[self.plIndex] == 'mixlr':
			self.getMixlerUrls()
			self["server"].setText('Mixlr')
		
		elif self.choices[self.plIndex] == 'playlist':
			if getPlaylist():
				playlist = getPlaylist()
				list = []
				for channel in playlist['playlist']:
					list.append((str(channel['channel']), str(channel['url'])))
				self["list"].l.setList(self.iniMenu(list))
				self["list"].show()
				self.radioList = list
				self["server"].setText('Custom Playlist')
			else:
				self["list"].hide()
				self["server"].setText('Cannot load playlist')
	
	def iniMenu(self,sList):
		res = []
		gList = []
		for elem in sList:
				if isHD():
					res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER |RT_WRAP, text='', color=16753920, color_sel=15657130, border_width=3, border_color=806544))
					res.append(MultiContentEntryText(pos=(5, 2), size=(580, 50), font=0, color=16777215,color_sel=16777215, backcolor_sel=None, flags=RT_VALIGN_CENTER | RT_HALIGN_LEFT, text=str(elem[0])))
				else:
					res.append(MultiContentEntryText(pos=(0, 0), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER |RT_WRAP, text='', color=16753920, color_sel=15657130, border_width=3, border_color=806544))
					res.append(MultiContentEntryText(pos=(5, 7), size=(580, 50), font=0, color=16777215,color_sel=16777215, backcolor_sel=None, flags=RT_VALIGN_CENTER | RT_HALIGN_LEFT, text=str(elem[0])))
				gList.append(res)
				res = []
		return gList

	def ok(self):
		if fileExists('/usr/bin/gst1.0-ipaudio'):
			index = self['list'].getSelectionIndex()
			self.url = self.radioList[index][1]
			config.plugins.IPAudio.lastidx.value = '{},{}'.format(self.plIndex,index)
			config.plugins.IPAudio.lastidx.save()
			cmd = 'gst1.0-ipaudio "{}" {}'.format(self.url,config.plugins.IPAudio.sync.value)
			self.runCmdAndSaveProcessIdToFile(cmd, '/tmp/.ipaudio.pid', 'w')
		else:
			self.session.open(MessageBox, _("Cannot play url, gst1.0-ipaudio is missing !!"), MessageBox.TYPE_ERROR,timeout=5)
		
	def audio_start(self):
		if fileExists('/dev/dvb/adapter0/audio10'):
			self.session.nav.stopService()
			cmd = 'mv /dev/dvb/adapter0/audio10 /dev/dvb/adapter0/audio0'
			self.Audiocontainer.execute(cmd)
			self.session.nav.playService(self.lastservice)
		elif config.plugins.IPAudio.running.value == "1" and is_compatible():
			cmd = 'gst1.0-ipaudio Unmute'
			self.container.execute(cmd)
	
	def resetAudio(self):
		self.kill_pid()
		if not self.alsa:
			self.audio_start()

	def runCmdAndSaveProcessIdToFile(self, cmd, pidFile, option):
		if is_compatible() and not config.plugins.IPAudio.keepaudio.value:
			if not fileExists('/tmp/.ipaudio.pid'):
				self.Audiocontainer.execute('gst1.0-ipaudio Mute')
				self.container.execute(cmd)
				config.plugins.IPAudio.running.value = "1"
				config.plugins.IPAudio.running.save()
			else:
				self.kill_pid()
				self.container.execute(cmd)
				config.plugins.IPAudio.running.value = "1"
				config.plugins.IPAudio.running.save()
		elif self.alsa:
			self.kill_pid()
			self.alsa.stop()
			self.alsa.close()
			self.container.execute(cmd)
			config.plugins.IPAudio.running.value = "1"
			config.plugins.IPAudio.running.save()
		elif config.plugins.IPAudio.keepaudio.value:
			self.kill_pid()
			self.container.execute(cmd)
			config.plugins.IPAudio.running.value = "1"
			config.plugins.IPAudio.running.save()
		else:
			if not fileExists('/tmp/.ipaudio.pid') and fileExists('/dev/dvb/adapter0/audio0'):
				self.session.nav.stopService()
				self.Audiocontainer.execute('mv /dev/dvb/adapter0/audio0 /dev/dvb/adapter0/audio10')
				self.container.execute(cmd)
				self.session.nav.playService(self.lastservice)
				config.plugins.IPAudio.running.value = "1"
				config.plugins.IPAudio.running.save()
			elif fileExists('/tmp/.ipaudio.pid'):
				self.kill_pid()
				self.container.execute(cmd)
				config.plugins.IPAudio.running.value = "1"
				config.plugins.IPAudio.running.save()
			
		if self.container.running():
			pid = self.container.getPID()
			file = open(pidFile, option)
			file.write(str(pid))
			file.close()
			
	def kill_pid(self):
		if fileExists('/tmp/.ipaudio.pid'):
			os.system('killall -9 gst1.0-ipaudio >/dev/null 2>&1')
			os.remove('/tmp/.ipaudio.pid')
			if self.container.running():
				self.container.kill()

	def readFromFileIfExists(self, fileName, options):
		if fileExists(fileName):
			with open(fileName, options) as file:
				return file.read().replace('\n', '').strip()
		return ""
	
	def Config_lctr(self):
		self.session.openWithCallback(self.exit, IPAudioSetup)
		
	def exit(self,ret=False):
		if self.Audiocontainer.running():
			self.Audiocontainer.kill()
		self.close()
		
class IPAudio(Screen):
	
	def __init__(self,session):
		Screen.__init__(self, session)
		self.session = session
		self.IPAudiocontainer = eConsoleAppContainer()
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
			iPlayableService.evEnd: self.__evEnd,
			iPlayableService.evStopped: self.__evEnd,
		})
	
	def kill_pid(self):
		if fileExists('/tmp/.ipaudio.pid'):
			os.system('killall -9 gst1.0-ipaudio >/dev/null 2>&1')
			os.remove('/tmp/.ipaudio.pid')

	def __evEnd(self):
		if fileExists('/dev/dvb/adapter0/audio10') and config.plugins.IPAudio.running.value == '1':
			self.kill_pid()
			self.IPAudiocontainer.execute('mv /dev/dvb/adapter0/audio10 /dev/dvb/adapter0/audio0')
			config.plugins.IPAudio.running.value = '0'
			config.plugins.IPAudio.running.save()
		elif config.plugins.IPAudio.running.value == '1' and config.plugins.IPAudio.keepaudio.value or HAVE_EALSA:
			self.kill_pid()
		else:
			if config.plugins.IPAudio.running.value == '1' and is_compatible():
				self.kill_pid()
				self.IPAudiocontainer.execute('gst1.0-ipaudio Unmute')
				config.plugins.IPAudio.running.value = '0'
				config.plugins.IPAudio.running.save()
		
	def gotSession(self):
		keymap = resolveFilename(SCOPE_PLUGINS, "Extensions/IPAudio/keymap.xml")
		global globalActionMap
		readKeymap(keymap)
		globalActionMap.actions['IPAudioSelection'] = self.ShowHide
		
	def ShowHide(self):
		self.session.open(IPAudioScreen)
		
def sessionstart(reason, session=None, **kwargs):
	if reason == 0:
		IPAudio(session).gotSession()
		
def main(session, **kwargs):
	session.open(IPAudioScreen)

def showInmenu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("IPAudio", main, "IPAudio", 1)]
	else:
		return []

def Plugins(**kwargs):
	Descriptors = []
	Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart))
	if config.plugins.IPAudio.mainmenu.value:
		Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_MENU], fnc=showInmenu))
	Descriptors.append(PluginDescriptor(name="IPAudio", description="Listen to your favorite commentators",icon="logo.png",where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
	return Descriptors
