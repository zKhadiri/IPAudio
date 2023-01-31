from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Tools.BoundFunction import boundFunction
from GlobalActions import globalActionMap
try:
	from keymapparser import readKeymap
except:
	from Components.ActionMap import loadKeymap as readKeymap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSelectionNumber, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigInteger, ConfigSubsection ,ConfigText ,configfile ,NoSave
from Components.ConfigList import ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from enigma import eConsoleAppContainer , getDesktop  , eListboxPythonMultiContent , gFont , RT_HALIGN_LEFT, RT_VALIGN_CENTER , RT_WRAP
from Components.ServiceEventTracker import ServiceEventTracker
from Components.MultiContent import MultiContentEntryText
from Tools.Directories import fileExists
from enigma import iPlayableService, eTimer
try:
	from enigma import eAlsaOutput
	HAVE_EALSA = True
except ImportError:
	HAVE_EALSA = False
from Plugins.Extensions.IPAudio.Console2 import Console2
import os, time ,sys , json
from .skin import *
from sys import version_info
from collections import OrderedDict

PY3 = version_info[0] == 3
MAX_DELAY = 50

config.plugins.IPAudio = ConfigSubsection()
config.plugins.IPAudio.currentService = ConfigText()
config.plugins.IPAudio.player = ConfigSelection(default="gst1.0-ipaudio", choices = [
				("gst1.0-ipaudio", _("Gstreamer")),
				("ff-ipaudio", _("FFmpeg")),
			])
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
config.plugins.IPAudio.volLevel = ConfigSelectionNumber(default=1, stepwidth=1, min=1, max=10, wraparound=True)
config.plugins.IPAudio.tsDelay = ConfigInteger(default=5, limits=[1, MAX_DELAY])
config.plugins.IPAudio.playlist = ConfigSelection(choices = [("1", _("Press OK"))], default = "1")
config.plugins.IPAudio.running = ConfigYesNo(default=False)
config.plugins.IPAudio.lastidx = ConfigText()
config.plugins.IPAudio.lastplayed = NoSave(ConfigText())

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
		self.currentSkin = config.plugins.IPAudio.skin.value
		if self.currentSkin == 'Icone':
			self.skin = SKIN_IPAudioSetup_ICONE
		elif self.currentSkin == 'light':
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
		self.list = [getConfigListEntry(_("Player"), config.plugins.IPAudio.player)]
		if config.plugins.IPAudio.player.value == "gst1.0-ipaudio":
			self.list.append(getConfigListEntry(_("Sync Audio using"), config.plugins.IPAudio.sync))
			self.list.append(getConfigListEntry(_("External links volume level"), config.plugins.IPAudio.volLevel))
		self.list.append(getConfigListEntry(_("Keep original channel audio"), config.plugins.IPAudio.keepaudio))
		self.list.append(getConfigListEntry(_("TimeShift Delay"), config.plugins.IPAudio.tsDelay))
		self.list.append(getConfigListEntry(_("Remove/Reset Playlist"), config.plugins.IPAudio.playlist))
		self.list.append(getConfigListEntry(_("Enable/Disable online update"), config.plugins.IPAudio.update))
		self.list.append(getConfigListEntry(_("Show IPAudio in main menu"), config.plugins.IPAudio.mainmenu))
		self.list.append(getConfigListEntry(_("Select Your IPAudio Skin"), config.plugins.IPAudio.skin))
		self["config"].list = self.list
		self["config"].setList(self.list)
		
	def apply(self):
		current = self["config"].getCurrent()
		if current[1] == config.plugins.IPAudio.playlist:
			self.session.open(IPAudioPlaylist)
		else:
			for x in self["config"].list:
				if len(x)>1:
					x[1].save()
			configfile.save()
			if self.currentSkin != config.plugins.IPAudio.skin.value:
				self.close(True)
			else:
				self.close()

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.createSetup()

class IPAudioScreen(Screen):
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		if config.plugins.IPAudio.skin.value == 'Icone':
			self.skin = SKIN_IPAudioScreen_ICONE
		elif config.plugins.IPAudio.skin.value == 'light':
			self.skin = SKIN_IPAudioScreen_Light
		self.choices = list(self.getHosts())
		self.plIndex = 0
		self['server'] = Label()
		self['sync'] = Label()
		self['sync'].setText('Audio sink : {}   TS Delay: {}'.format(get_Lecteur(), config.plugins.IPAudio.tsDelay.value))
		self["list"] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		if isHD():
			self["list"].l.setItemHeight(50)
			self["list"].l.setFont(0, gFont('Regular', 20))
		else:
			self["list"].l.setItemHeight(58)
			self["list"].l.setFont(0, gFont('Regular', 28))
		self["key_green"] = Button(_("Reset Audio"))
		self["IPAudioAction"] = ActionMap(["IPAudioActions"],
		{
			"ok": self.ok,
			"ok_long": boundFunction(self.ok, long=True),
			"cancel": boundFunction(self.exit, True),
			"green": self.resetAudio,
			"right":self.right,
			"left":self.left,
			"menu":self.Config_lctr,
			"pause":self.pause,
			"delayUP":self.delayUP,
			"delayDown":self.delayDown,
		}, -1)
		self.alsa = None
		self.guide = dict()
		if HAVE_EALSA:
			self.alsa = eAlsaOutput.getInstance()       
		self.container = eConsoleAppContainer()
		self.timeShiftTimer = eTimer()
		try:
			self.timeShiftTimer.callback.append(self.unpauseService)
		except:
			self.timeShiftTimer_conn = self.timeShiftTimer.timeout.connect(self.unpauseService)
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		if config.plugins.IPAudio.update.value:
			self.checkupdates()
		self.onLayoutFinish.append(self.getGuide)
		self.onShown.append(self.onWindowShow)

	def getTimeshift(self):
		service = self.session.nav.getCurrentService()
		return service and service.timeshift()

	def pause(self):
		global delay
		if config.plugins.IPAudio.running.value:
			ts = self.getTimeshift()
			if ts is not None and not ts.isTimeshiftEnabled():
				ts.startTimeshift()
				ts.activateTimeshift()
				self.timeShiftTimer.start(config.plugins.IPAudio.tsDelay.value * 1000)
				delay = config.plugins.IPAudio.tsDelay.value
			elif ts is not None and ts.isTimeshiftEnabled() and not self.timeShiftTimer.isActive():
				if delay <= config.plugins.IPAudio.tsDelay.value:
					service = self.session.nav.getCurrentService()
					pauseable = service.pause()
					if pauseable:
						pauseable.pause()
						self.timeShiftTimer.start(((config.plugins.IPAudio.tsDelay.value) - delay) * 1000)
					delay = config.plugins.IPAudio.tsDelay.value
				if delay > config.plugins.IPAudio.tsDelay.value:
					ts.stopTimeshift()
					ts.startTimeshift()
					ts.activateTimeshift()
					self.timeShiftTimer.start(((config.plugins.IPAudio.tsDelay.value)) * 1000)
					delay = config.plugins.IPAudio.tsDelay.value

	def unpauseService(self):
		self.timeShiftTimer.stop()
		service = self.session.nav.getCurrentService()
		pauseable = service.pause()
		if pauseable:
			pauseable.unpause()

	def delayUP(self):
		if config.plugins.IPAudio.tsDelay.value < MAX_DELAY:
			config.plugins.IPAudio.tsDelay.value += 1
			config.plugins.IPAudio.tsDelay.save()
			self['sync'].setText('Audio sink : {}   TS Delay: {}'.format(get_Lecteur(), config.plugins.IPAudio.tsDelay.value))

	def delayDown(self):
		if config.plugins.IPAudio.tsDelay.value > 1:
			config.plugins.IPAudio.tsDelay.value -= 1
			config.plugins.IPAudio.tsDelay.save()
			self['sync'].setText('Audio sink : {}   TS Delay: {}'.format(get_Lecteur(), config.plugins.IPAudio.tsDelay.value))

	def getHosts(self):
		hosts = resolveFilename(SCOPE_PLUGINS, "Extensions/IPAudio/hosts.json")
		self.hosts = None
		if fileExists(hosts):
			hosts = open(hosts,'r').read()
			self.hosts = json.loads(hosts, object_pairs_hook=OrderedDict)
			for host in self.hosts:
				yield host
		
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
		url = 'http://ipkinstall.ath.cx/ipaudio/installer-ffmpeg.sh'
		self.callUrl(url,self.checkVer)

	def checkVer(self, data):
		if PY3:
			data = data.decode("utf-8")
		else:
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
			cmdlist.append('wget -q "--no-check-certificate" http://ipkinstall.ath.cx/ipaudio/installer-ffmpeg.sh -O - | /bin/sh')
			self.session.open(Console2, title='Update IPAudio', cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)

	def myCallback(self,result=None):
		return

	def callUrl(self,url,callback):
		try:
			from twisted.web.client import getPage
			getPage(str.encode(url), headers={b'Content-Type': b'application/x-www-form-urlencoded'}).addCallback(callback).addErrback(self.addErrback)
		except:
			pass

	def getMixlerUrls(self):
		url = 'http://ipkinstall.ath.cx/mixlr'
		self.callUrl(url,self.parseData)
			
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
		self.plIndex +=1
		self.changePlaylist()
		
	def left(self):
		self.plIndex -=1
		self.changePlaylist()
		
	def changePlaylist(self):
		if self.plIndex > (len(self.choices)-1):
			self.plIndex = 0
		if self.plIndex < 0:
			self.plIndex = len(self.choices)-1
		self.setPlaylist()
		
	def setPlaylist(self):
		current = self.choices[self.plIndex]
		if current in self.hosts:
			if current == 'Mixlr Sport':
				self.getMixlerUrls()
				self["server"].setText(str(current))
			elif current == 'Custom Playlist':
				if getPlaylist():
					playlist = getPlaylist()
					list = []
					for channel in playlist['playlist']:
						list.append((str(channel['channel']), str(channel['url'])))
					if len(list) > 0:
						self["list"].l.setList(self.iniMenu(list))
						self["list"].show()
						self.radioList = list
						self["server"].setText('Custom Playlist')
					else:
						self["list"].hide()
						self["server"].setText('Playlist is empty')
				else:
					self["list"].hide()
					self["server"].setText('Cannot load playlist')
			else:
				list = []
				for cmd in self.hosts[current]['cmds']:
					list.append((cmd.split('|')[0], cmd.split('|')[1]))
				list = self.checkINGuide(list)
				self["list"].l.setList(self.iniMenu(list))
				self["list"].show()
				self.radioList = list
				self["server"].setText(str(current))
	
	def checkINGuide(self, entries):
		for idx,entry in enumerate(entries):
			if entry[0] in self.guide:
				entries[idx] = (self.guide[entry[0]]['prog'], entry[1])
		return entries
		
	def getGuide(self):
		url = 'http://ipkinstall.ath.cx/ipaudio/epg.json'
		self.callUrl(url,self.parseGuide)
		
	def parseGuide(self,data):
		if PY3:
			data = data.decode("utf-8")
		else:
			data = data.encode("utf-8")
		self.guide = json.loads(data)
		if self.guide != {}:
			self.setPlaylist()
  
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

	def ok(self, long=False):
		if fileExists('/usr/bin/{}'.format(config.plugins.IPAudio.player.value)):
			if long:
				self.url = 'http://127.0.0.1:8001/{}'.format(self.lastservice.toString())
				config.plugins.IPAudio.lastplayed.value = "e2_service"
			else:
				index = self['list'].getSelectionIndex()
				self.url = self.radioList[index][1]
				config.plugins.IPAudio.lastplayed.value = self.url
				config.plugins.IPAudio.lastidx.value = '{},{}'.format(self.plIndex,index)
				config.plugins.IPAudio.lastidx.save()
			if config.plugins.IPAudio.player.value == "gst1.0-ipaudio":
				cmd = 'gst1.0-ipaudio "{}" {}'.format(self.url,config.plugins.IPAudio.sync.value)
				if self.choices[self.plIndex] == 'Custom Playlist' and not long:
					cmd += ' {}'.format(config.plugins.IPAudio.volLevel.value)
			else:
				cmd = 'ff-ipaudio "{}"'.format(self.url)
			self.runCmdAndSaveProcessIdToFile(cmd, '/tmp/.ipaudio.pid', 'w')
		else:
			self.session.open(MessageBox, _("Cannot play url, {} is missing !!".format(config.plugins.IPAudio.player.value)), MessageBox.TYPE_ERROR,timeout=5)
		
	def audio_start(self):
		if fileExists('/dev/dvb/adapter0/audio10'):
			os.rename('/dev/dvb/adapter0/audio10','/dev/dvb/adapter0/audio0')
			self.session.nav.stopService()
			self.session.nav.playService(self.lastservice)
		elif config.plugins.IPAudio.running.value and is_compatible():
			cmd = '{} Unmute'.format(config.plugins.IPAudio.player.value)
			self.container.execute(cmd)
			config.plugins.IPAudio.running.value = False
			config.plugins.IPAudio.running.save()
	
	def resetAudio(self):
		self.kill_pid()
		if not self.alsa:
			self.audio_start()

	def runCmdAndSaveProcessIdToFile(self, cmd, pidFile, option):
		if is_compatible() and not config.plugins.IPAudio.keepaudio.value:
			if not fileExists('/tmp/.ipaudio.pid'):
				self.container.execute('{} Mute && {}'.format(config.plugins.IPAudio.player.value, cmd))
				config.plugins.IPAudio.running.value = True
				config.plugins.IPAudio.running.save()
			else:
				self.kill_pid()
				self.container.execute(cmd)
				config.plugins.IPAudio.running.value = True
				config.plugins.IPAudio.running.save()
		elif self.alsa:
			self.kill_pid()
			self.alsa.stop()
			self.alsa.close()
			self.container.execute(cmd)
			config.plugins.IPAudio.running.value = True
			config.plugins.IPAudio.running.save()
		elif config.plugins.IPAudio.keepaudio.value:
			self.kill_pid()
			self.container.execute(cmd)
			config.plugins.IPAudio.running.value = True
			config.plugins.IPAudio.running.save()
		else:
			if not fileExists('/tmp/.ipaudio.pid') and fileExists('/dev/dvb/adapter0/audio0'):
				self.session.nav.stopService()
				os.rename('/dev/dvb/adapter0/audio0','/dev/dvb/adapter0/audio10')
				self.container.execute(cmd)
				self.session.nav.playService(self.lastservice)
				config.plugins.IPAudio.running.value = True
				config.plugins.IPAudio.running.save()
			elif fileExists('/tmp/.ipaudio.pid'):
				self.kill_pid()
				self.container.execute(cmd)
				config.plugins.IPAudio.running.value = True
				config.plugins.IPAudio.running.save()
			
		if self.container.running():
			pid = self.container.getPID()
			file = open(pidFile, option)
			file.write(str(pid))
			file.close()
			
	def kill_pid(self):
		if fileExists('/tmp/.ipaudio.pid'):
			os.system('killall -9 {} >/dev/null 2>&1'.format(config.plugins.IPAudio.player.value))
			os.remove('/tmp/.ipaudio.pid')
			if self.container.running():
				self.container.kill()
				
	def Config_lctr(self):
		self.session.openWithCallback(self.exit, IPAudioSetup)
		
	def exit(self,ret=False):
		if ret and not self.timeShiftTimer.isActive():
			self.close()

class IPAudioPlaylist(IPAudioScreen):

	def __init__(self,session):
		IPAudioScreen.__init__(self, session)
		if config.plugins.IPAudio.skin.value == 'Icone':
			self.skin = SKIN_IPAudioPlaylist_ICONE
		elif config.plugins.IPAudio.skin.value == 'light':
			self.skin = SKIN_IPAudioPlaylist_Light
		self["key_green"] = Button(_("Remove Link"))
		self["key_red"] = Button(_("Reset Playlist"))
		self["IPAudioAction"] = ActionMap(["IPAudioActions"],
		{
			"cancel": self.exit,
			"green": self.keyGreen,
			"red": self.keyRed,
		}, -1)
		self.onLayoutFinish = []
		self.onShown = []
		self.loadPlaylist()

	def loadPlaylist(self):
		playlist = getPlaylist()
		if playlist:
			list = []
			for channel in playlist['playlist']:
				try:
					list.append((str(channel['channel']), str(channel['url'])))
				except KeyError:pass
			if len(list) > 0:
				self["list"].l.setList(self.iniMenu(list))
				self["server"].setText('Custom Playlist')
			else:
				self["list"].hide()
				self["server"].setText('Playlist is empty')
		else:
			self["list"].hide()
			self["server"].setText('Cannot load playlist')

	def keyRed(self):
		playlist = getPlaylist()
		if playlist:
			playlist['playlist'] = []
			with open("/etc/enigma2/ipaudio.json", 'w')as f:
				json.dump(playlist, f , indent = 4)
			self.loadPlaylist()

	def keyGreen(self):
		playlist = getPlaylist()
		if playlist:
			if len(playlist['playlist']) > 0:
				index = self['list'].getSelectionIndex()
				currentPlaylist = playlist["playlist"]
				del currentPlaylist[index]
				playlist['playlist'] = currentPlaylist
				with open("/etc/enigma2/ipaudio.json", 'w')as f:
					json.dump(playlist, f , indent = 4)
				self.loadPlaylist()

	def exit(self):
		self.close()
	
class IPAudio(Screen):
	
	def __init__(self,session):
		Screen.__init__(self, session)
		self.session = session
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
			iPlayableService.evEnd: self.__evEnd,
			iPlayableService.evStopped: self.__evEnd,
		})
	
	def kill_pid(self):
		if fileExists('/tmp/.ipaudio.pid'):
			os.system('killall -9 {} >/dev/null 2>&1'.format(config.plugins.IPAudio.player.value))
			os.remove('/tmp/.ipaudio.pid')

	def __evEnd(self):
		if not config.plugins.IPAudio.lastplayed.value == "e2_service":
			if fileExists('/dev/dvb/adapter0/audio10') and config.plugins.IPAudio.running.value:
				self.kill_pid()
				os.rename('/dev/dvb/adapter0/audio10','/dev/dvb/adapter0/audio0')
				config.plugins.IPAudio.running.value = False
				config.plugins.IPAudio.running.save()
			elif config.plugins.IPAudio.running.value and config.plugins.IPAudio.keepaudio.value or HAVE_EALSA:
				self.kill_pid()
			else:
				if config.plugins.IPAudio.running.value and is_compatible():
					self.kill_pid()
					os.system('{} Unmute'.format(config.plugins.IPAudio.player.value))
					config.plugins.IPAudio.running.value = False
					config.plugins.IPAudio.running.save()
		
	def gotSession(self):
		keymap = resolveFilename(SCOPE_PLUGINS, "Extensions/IPAudio/keymap.xml")
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
