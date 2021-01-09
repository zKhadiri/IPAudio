from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Screens.InfoBar import MoviePlayer, InfoBar
from enigma import eServiceReference
from Components.MenuList import MenuList
from GlobalActions import globalActionMap
from keymapparser import readKeymap
from Components.config import ConfigSubsection, ConfigText ,config
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import eConsoleAppContainer , getDesktop 
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists
import os


REDC =  '\033[31m'                                                              
ENDC = '\033[m'                                                                 
                                                                                
def cprint(text):                                                               
    print(REDC+text+ENDC)
    


class IPAudioScreen(Screen):
    
    skin = """
		<screen name="IPAudio" position="center,center" size="762,562" title="IPAudio By ZIKO" backgroundColor="#16000000" flags="wfNoBorder">
  			<widget source="Title" position="8,10" size="743,35" render="Label" font="Regular;26" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1"/>

  			<widget font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#16000000" halign="center" position="615,5" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
    				<convert type="ClockToText">Default</convert>
  			</widget>
     
            <ePixmap name="green" position="210,525" zPosition="2" size="140,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" transparent="1" alphatest="on"/>
            <widget name="key_green" position="210,520" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;19" transparent="1"/>
  			<widget name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" position="10,85" size="750,370" scrollbarMode="showOnDemand"/>
		</screen>"""

    def __init__(self, session):
        self.session = session
        list = []
        list.append(("test", 1, "test"))
        self["config"] = MenuList(list)
        self.radioList = list
        Screen.__init__(self, session)
        self["key_green"] = Button(_("Stop Audio"))
        self["myActionMap"] = ActionMap(["SetupActions", "WizardActions", "MenuActions"],
        {
            "cancel": self.exit,
            "ok":self.ok,
            "save": self.stop,
        }, -1)
        self.container = eConsoleAppContainer()
        
    def ok(self):
        self.kill_pid()
        index = self['config'].getSelectionIndex()
        url = self.radioList[index][2]
        cmd = 'gst-launch-1.0 playbin uri={} audio-sink="alsasink" volume=10.0 max-size-buffers=0 flags=0x32'.format(url)
        self.container.execute(cmd)
        pid = self.container.getPID()
        if pid:
            file = open('/tmp/.ipaudio.pid','w')
            file.write(str(pid))
            file.close()
        
    def kill_pid(self):
        if fileExists('/tmp/.ipaudio.pid'):
            file = open('/tmp/.ipaudio.pid','r')
            pid = file.read().strip()
            file.close()
            os.remove('/tmp/.ipaudio.pid')
            os.system('kill -9 {}'.format(pid))

    def stop(self):
        self.kill_pid()
        
    def exit(self):
        self.close()


class IPAudio():
    
        def __init__(self):
            self.dialog = None

        def gotSession(self, session):
                self.session = session
                keymap = resolveFilename(
                    SCOPE_PLUGINS, "Extensions/IPAudio/keymap.xml")
                global globalActionMap
                readKeymap(keymap)
                globalActionMap.actions['audioSelection'] = self.ShowHide

        def ShowHide(self):
            self.session.open(IPAudioScreen)
            
            
def sessionstart(reason, session=None, **kwargs):
    if reason == 0:
        IPAudio().gotSession(session)
        

def main(session, **kwargs):
    session.open(IPAudioScreen)


def Plugins(**kwargs):
    Descriptors = []
    Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart))
    return Descriptors
