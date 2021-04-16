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
from keymapparser import readKeymap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigInteger, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigSubsection ,ConfigText ,configfile , ConfigDirectory
from Components.ConfigList import ConfigList, ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import eConsoleAppContainer , getDesktop , eTimer , eListboxPythonMultiContent , gFont
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from enigma import iPlayableService 
from Plugins.Extensions.IPAudio.Console2 import Console2
import os ,sys

config.plugins.IPAudio = ConfigSubsection()
config.plugins.IPAudio.currentService = ConfigText()
config.plugins.IPAudio.sync = ConfigSelection(default="alsasink", choices = [
                ("alsasink", _("alsasink")),
                ("osssink", _("osssink")),
            ])
config.plugins.IPAudio.update = ConfigYesNo(default=True)
config.plugins.IPAudio.mainmenu = ConfigYesNo(default=False)
config.plugins.IPAudio.running = ConfigText()

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
    if fileExists('/proc/stb/info/boxtype') and open('/proc/stb/info/boxtype').read().strip() in ('sf8008','sf8008m','viper4kv20','beyonwizv2','ustym4kpro','gbtrio4k',):
        return True
    else:
        return False

class IPAudioSetup(Screen, ConfigListScreen):
    
    skin = """
        <screen name="IPAudioSetup" position="center,center" size="650,460" title="IPAudioSetup settings" flags="wfNoBorder">
            <widget position="15,10" size="620,300" name="config" scrollbarMode="showOnDemand" />
                <ePixmap position="100,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/red.png" alphatest="blend" />
            <widget source="red_key" render="Label" position="100,388" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
            <ePixmap position="385,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" alphatest="blend" />
            <widget source="green_key" render="Label" position="385,388" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
		</screen>"""
  
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ["IPAudioSetup"]
        self.setup_title = _("IPAudioSetup BY ZIKO V %s" % Ver)
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
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        
    def layoutFinished(self):
        self.setTitle(_("IPAudio BY ZIKO V %s" % Ver))
        
    def createSetup(self):
        self.list = [getConfigListEntry(_("Sync Audio using"), config.plugins.IPAudio.sync)]
        self.list.append(getConfigListEntry(_("Enable/Disable online update"), config.plugins.IPAudio.update))
        self.list.append(getConfigListEntry(_("Show IPAudio in main menu"), config.plugins.IPAudio.mainmenu))
        self["config"].list = self.list
        self["config"].setList(self.list)
        
    def apply(self):
        for x in self["config"].list:
            x[1].save()
        self.close()
        
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

class IPAudioScreen(Screen):

    skin="""<screen name="IPAudio" position="center,center" size="762,562" title="IPAudio By ZIKO V {}" backgroundColor="#16000000" flags="wfNoBorder" zPosition="4">
                <widget source="Title" position="8,10" size="743,35" render="Label" font="Regular;26" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" />
                <widget font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#16000000" halign="center" position="615,5" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
                <convert type="ClockToText">Default</convert>
                </widget>  
                <ePixmap name="green" position="210,525" zPosition="2" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" transparent="1" alphatest="on" />
                <widget name="key_green" position="210,520" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;19" transparent="1" />
                <widget name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" position="10,85" size="750,370" scrollbarMode="showOnDemand" />
                <widget name="status" foregroundColor="#00ffffff" backgroundColor="#16000000" position="15,462" size="724,28" font="Regular;24" />
                <ePixmap position="658,55" size="60,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/key_menu.png" alphatest="on" zPosition="5"/>	
                <widget name="Lecteur" foregroundColor="#00ffffff" backgroundColor="#16000000" position="15,488" size="724,28" font="Regular;24" />
            </screen>""".format(Ver)
				
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.choices = ['playlist']
        self.plIndex = 0
        self['status'] = Label()
        self['Lecteur'] = Label()
        self['Lecteur'].setText('Audio sink : '+get_Lecteur())
        self["config"] = MenuList([])
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
        self.container = eConsoleAppContainer()
        self.Audiocontainer = eConsoleAppContainer()
        self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
        self.setPlaylist()
        if config.plugins.IPAudio.update.value:
            self.checkupdates()

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

    def right(self):
        self['Lecteur'].setText('Audio sink : '+get_Lecteur())
        self.plIndex +=1
        self.changePlaylist()
        
    def left(self):
        self['Lecteur'].setText('Audio sink : '+get_Lecteur())
        self.plIndex -=1
        self.changePlaylist()
        
    def changePlaylist(self):
        if self.plIndex > (len(self.choices)-1):
           self.plIndex = 0
        if self.plIndex < 0:
           self.plIndex = len(self.choices)-1
        self.setPlaylist()
        
    def setPlaylist(self):
        if self.choices[self.plIndex] == 'playlist':
            if getPlaylist():
                playlist = getPlaylist()
                list = []
                for channel in playlist['playlist']:
                    list.append((str(channel['channel']), str(channel['url'])))
                self["config"].l.setList(list)
                self["config"].show()
                self.radioList = list
                self["status"].setText('Custom Playlist')
            else:
                self["config"].hide()
                self["status"].setText('Cannot load playlist')

    def ok(self):
        if fileExists('/usr/bin/ipplayer') and fileExists('/usr/bin/ipplayer-os'):
            index = self['config'].getSelectionIndex()
            self.url = self.radioList[index][1]
            if config.plugins.IPAudio.sync.value == 'alsasink':
                cmd = 'ipplayer "{}"'.format(self.url)
            elif config.plugins.IPAudio.sync.value == 'osssink':
                cmd = 'ipplayer-os "{}"'.format(self.url)
            self.runCmdAndSaveProcessIdToFile(cmd, '/tmp/.ipaudio.pid', 'w')
        else:
            self.session.open(MessageBox, _("Cannot play url, ipplayer is missing !!"), MessageBox.TYPE_ERROR,timeout=5)
        
    def audio_start(self):
        if fileExists('/dev/dvb/adapter0/audio10'):
            self.session.nav.stopService()
            cmd = 'mv /dev/dvb/adapter0/audio10 /dev/dvb/adapter0/audio0'
            self.Audiocontainer.execute(cmd)
            self.session.nav.playService(self.lastservice)
        elif config.plugins.IPAudio.running.value == "1" and is_compatible():
            cmd = 'ipplayer -u'
            self.container.execute(cmd)
    
    def resetAudio(self):
        self.kill_pid()
        self.audio_start()

    def runCmdAndSaveProcessIdToFile(self, cmd, pidFile, option):
        if is_compatible():
            if not fileExists('/tmp/.ipaudio.pid'):
                self.Audiocontainer.execute('ipplayer -m')
                self.container.execute(cmd)
                config.plugins.IPAudio.running.value = "1"
                config.plugins.IPAudio.running.save()
            else:
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
            if config.plugins.IPAudio.sync.value == 'alsasink':
                os.system('killall -9 ipplayer >/dev/null 2>&1')
            else:
                os.system('killall -9 ipplayer-os >/dev/null 2>&1')
            os.remove('/tmp/.ipaudio.pid')
            if self.container.running():
                self.container.kill()

    def readFromFileIfExists(self, fileName, options):
        if fileExists(fileName):
            with open(fileName, options) as file:
                return file.read().replace('\n', '').strip()
        return ""
    
    def Config_lctr(self):
        self.session.open(IPAudioSetup)
        
    def exit(self):
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
            if config.plugins.IPAudio.sync.value == 'alsasink':
                os.system('killall -9 ipplayer >/dev/null 2>&1')
            else:
                os.system('killall -9 ipplayer-os >/dev/null 2>&1')
            os.remove('/tmp/.ipaudio.pid')

    def __evEnd(self):
        if fileExists('/dev/dvb/adapter0/audio10') and config.plugins.IPAudio.running.value == '1':
            self.kill_pid()
            self.IPAudiocontainer.execute('mv /dev/dvb/adapter0/audio10 /dev/dvb/adapter0/audio0')
            config.plugins.IPAudio.running.value = '0'
            config.plugins.IPAudio.running.save()
        else:
            if config.plugins.IPAudio.running.value == '1' and is_compatible():
                self.kill_pid()
                self.IPAudiocontainer.execute('ipplayer -u')
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
    Descriptors.append(PluginDescriptor(name="IPAudio {}".format(Ver), description="Listen to your favorite commentators",icon="logo.png",where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
    return Descriptors
