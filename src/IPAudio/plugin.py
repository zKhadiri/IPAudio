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
from Components.config import config, ConfigInteger, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigSubsection ,ConfigText
from Components.ConfigList import ConfigList, ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from enigma import eConsoleAppContainer , getDesktop 
from Components.ServiceEventTracker import ServiceEventTracker
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from enigma import eDVBDB ,iPlayableService , iAudioTrackSelectionPtr
import os, time
import NavigationInstance
import subprocess


REDC =  '\033[31m'                                                              
ENDC = '\033[m'  
                                                               
def cprint(text):                                                               
    print(REDC+text+ENDC)
                                                                                
def to_unsigned(x):
    return x & 0xFFFFFFFF 
                                                                                
    
config.plugins.IPAudio = ConfigSubsection()
config.plugins.IPAudio.zap = ConfigYesNo(default=False)
config.plugins.IPAudio.running = ConfigText()
        
def kill_pid():
    if fileExists('/tmp/.ipaudio.pid'):
        file = open('/tmp/.ipaudio.pid','r')
        pid = file.read().strip()
        file.close()
        os.system('kill -9 {}'.format(pid))
        os.remove('/tmp/.ipaudio.pid')
        
            
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

class IPAudioSetup(Screen, ConfigListScreen):
    
    skin = """
		<screen name="IPAudioSetup" position="center,center" size="650,460" title="IPAudioSetup settings" backgroundColor="#16000000" flags="wfNoBorder">
		<widget foregroundColor="#00ffffff" backgroundColor="#16000000" position="15,10" size="620,300" name="config" scrollbarMode="showOnDemand" />
			<ePixmap position="100,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/red.png" alphatest="blend" />
            <ePixmap position="385,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" alphatest="blend" />
            <widget source="green_key" render="Label" position="385,388" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
            
		</screen>"""
  

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ["IPToSATSetup"]
        self.setup_title = (_("IPToSAT BY ZIKO V %s" % Ver))
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

        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("IPAudio BY ZIKO V %s" % Ver))
        

    def createSetup(self):
        self.list = [getConfigListEntry(_("Stop IPAudio on zap"), config.plugins.IPAudio.zap)]

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
    skin = """
		<screen name="IPAudio" position="center,center" size="762,562" title="IPAudio By ZIKO V {}" backgroundColor="#16000000" flags="wfNoBorder">
  			<widget source="Title" position="8,10" size="743,35" render="Label" font="Regular;26" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1"/>

  			<widget font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#16000000" halign="center" position="615,5" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
    				<convert type="ClockToText">Default</convert>
  			</widget>
            <ePixmap position="658,55" size="60,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/key_menu.png" alphatest="on" zPosition="5"/>
            <ePixmap name="red" position="394,490" zPosition="2" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/red.png" transparent="1" alphatest="on"/>     
            <ePixmap name="green" position="88,492" zPosition="2" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" transparent="1" alphatest="on"/>
            <widget name="key_green" position="88,492" size="225,60" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;19" transparent="1"/>
            <ePixmap name="green" position="88,492" zPosition="2" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/green.png" transparent="1" alphatest="on"/>
            <widget name="key_green" position="88,492" size="225,60" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;19" transparent="1"/>
            <widget name="key_red" position="394,490" size="225,60" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;19" transparent="1"/>
  			<widget name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" position="10,85" size="750,370" scrollbarMode="showOnDemand"/>
		</screen>""".format(Ver)

    def __init__(self, session):
        self.session = session
        
        list = []
        list.append(("CHANNEL_NAME", "URL"))
        
        if getPlaylist():
            playlist = getPlaylist()
            for channel in playlist['playlist']:
                list.append((str(channel['channel']), str(channel['url'])))

        self["config"] = MenuList(list)
        self.radioList = list
        Screen.__init__(self, session)
        self["key_green"] = Button(_("Remove apid"))
        #self["key_red"] = Button(_("Stop Audio IP Stream"))
        self["myActionMap"] = ActionMap(["OkCancelActions", "ColorActions","WizardActions","MenuActions"],
        {
            "ok": self.ok,
            "cancel": self.exit,
            #"red": self.stop,
            "green": self.remove_apid,
            #"menu":self.showsetup,
        }, -1)
        self.container = eConsoleAppContainer()
        self.origServiceDataBkpFile = '/etc/.orig_service_data.txt'
        

    def ok(self):
        kill_pid()
        index = self['config'].getSelectionIndex()
        url = self.radioList[index][1]
        cmd = 'gst-launch-1.0 playbin uri={} audio-sink="alsasink" volume=10.0 max-size-buffers=0 max-size-time=0 flags=0x32'.format(url)
        self.container.execute(cmd)
        pid = self.container.getPID()
        if pid:
            file = open('/tmp/.ipaudio.pid','w')
            file.write(str(pid))
            file.close()
        
        
    def RemoveAudioPid(self):
        self.getServiceData()
        self.updateLameDbServiceData()
        service = self.session.nav.getCurrentlyPlayingServiceReference()
        config.plugins.IPAudio.running.value = ':'.join(service.toString().split(':')[:11])
        config.plugins.IPAudio.running.save()
        self.reloadServiceAndBouquetList()
    
    def getServiceData(self):
        cur_ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        service = NavigationInstance.instance.getCurrentService()
        if service is not None:
            self.info = service.info()
            
        if cur_ref is not None:         
            extraParams = 'c:050001,C:0000'
            includeExtraParam = 'f:04'            
            cur_serv = cur_ref.toString().strip()

            cur_serv_tab = cur_serv.split(":")
            sid = cur_serv_tab[3].strip().zfill(4)
            transponder = cur_serv_tab[6].strip().zfill(8)
            self.sidId = sid + ':' + transponder
            
            name = ServiceReference(cur_ref).getServiceName()
            
        if self.info is not None:
            videoPid = self.getServiceInfoValue(iServiceInformation.sVideoPID)
            videoPid = self.getServiceInfoValue(iServiceInformation.sVideoPID)
            pcrPid = self.getServiceInfoValue(iServiceInformation.sPCRPID)
            provider = self.getServiceInfoValue(iServiceInformation.sProvider)            
            videoPidHex = self.convertDecimalToHex(videoPid, 6)
            pcrPidHex = self.convertDecimalToHex(pcrPid, 6)
            self.serviceData = 'p:' + str(provider.strip()) + ',c:' + videoPidHex + ',c:' + pcrPidHex + ',' + extraParams + ',' + includeExtraParam

        
    def convertDecimalToHex(self, decValue, size):
         return "{0:x}".format(decValue).zfill(size)    

    def updateLameDbServiceData(self):
        
        origServiceData = self.loadServiceDataFromBackupIfExists(self.origServiceDataBkpFile, 'r')
        self.logMe("origServiceData : " + origServiceData + "\n")
        if origServiceData != "":
            if self.sidId.lower() != origServiceData.split("$$$")[0]:
                updateServiceDataCmd = "/bin/sed -i '/" + origServiceData.split("$$$")[0] + "/ { n; n; s/.*/" + origServiceData.split("$$$")[1] + "/I; }' /etc/enigma2/lamedb"
                subprocess.call([updateServiceDataCmd], shell=True)
                self.reloadServiceAndBouquetList()
                self.logMe("zap rollback : " + updateServiceDataCmd + "\n")            
                
                self.backupServiceDataRetrievdFromLameDB()
                updateServiceDataCmd = "/bin/sed -i '/" + self.sidId.lower() + "/ { n; n; s/.*/" + self.serviceData + "/I; }' /etc/enigma2/lamedb"
                subprocess.call([updateServiceDataCmd], shell=True)
                self.reloadServiceAndBouquetList()
                self.logMe("zap Update : " + updateServiceDataCmd + "\n")
        else:
            self.backupServiceDataRetrievdFromLameDB()
            updateServiceDataCmd = "/bin/sed -i '/" + self.sidId.lower() + "/ { n; n; s/.*/" + self.serviceData + "/I; }' /etc/enigma2/lamedb"
            subprocess.call([updateServiceDataCmd], shell=True)
            self.reloadServiceAndBouquetList()
            self.logMe("Update new : " + updateServiceDataCmd + "\n")
        
    def logMe(self, info):
        logFile = open('/tmp/IPAudio.log', 'a')
        logFile.write('info : ' + str(info))
        logFile.close()

    def getServiceInfoValue(self, key):
	    if self.info:
	       v = self.info.getInfo(key)
	       if v == -2:
	           v = self.info.getInfoString(key)
	       return v
	    return ""

    def reloadServiceAndBouquetList(self):
        self.eDVBDB = eDVBDB.getInstance()
        self.eDVBDB.reloadServicelist()
        self.eDVBDB.reloadBouquets()
        

    def retriveServiceDataFromLameDB(self):
        searchServiceDataCmd = "/bin/sed -n '/" + self.sidId.lower() + "/{n;n;p}' /etc/enigma2/lamedb"
        serviceDataFromLameDB = subprocess.check_output(searchServiceDataCmd, shell=True);
        return serviceDataFromLameDB

    def backupServiceDataRetrievdFromLameDB(self):
        originaServiceDataFile = open(self.origServiceDataBkpFile, 'w')
        originaServiceDataFile.write(self.sidId.lower() + '$$$' + str(self.retriveServiceDataFromLameDB()))
        originaServiceDataFile.close()

    def loadServiceDataFromBackupIfExists(self, fileName, options):
        return self.readFromFileIfExists(fileName, options)
        
    def readFromFileIfExists(self, fileName, options):
        if fileExists(fileName):
            with open(fileName, options) as file:
                return file.read().replace('\n', '').strip()
        return ""


    def undoLameDbServiceDataChanges(self):
        self.logMe("Green-Key - Stop method executed (undoLameDbServiceDataChanges(self)) : " + "\n")
        kill_pid()
        origServiceData = self.loadServiceDataFromBackupIfExists(self.origServiceDataBkpFile, 'r')
        self.logMe("origServiceData : " + origServiceData + "\n")
        if origServiceData != "":
            updateServiceDataCmd = "/bin/sed -i '/" + origServiceData.split("$$$")[0] + "/ { n; n; s/.*/" + origServiceData.split("$$$")[1] + "/I; }' /etc/enigma2/lamedb"
            subprocess.call([updateServiceDataCmd], shell=True)
            time.sleep(1)
            os.remove(self.origServiceDataBkpFile)
            self.reloadServiceAndBouquetList()
            self.logMe("Go back to original settings : " + updateServiceDataCmd + "\n")    
        config.plugins.IPAudio.running.value = ""
        config.plugins.IPAudio.running.save()
        
    def remove_apid(self):
        self.RemoveAudioPid()
          
    def exit(self):
        self.close()


class IPAudio(Screen):
    
        def __init__(self,session):
            Screen.__init__(self, session)
            self.session = session
            self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
                iPlayableService.evStart: self.__evStart,
                iPlayableService.evTunedIn: self.__evStart,
                iPlayableService.evEnd: self.__evEnd,
                iPlayableService.evStopped: self.__evEnd,
            })
            self.ipaudio = False
            self.origServiceDataBkpFile = '/etc/.orig_service_data.txt'
        
        def __evStart(self):
            service = self.session.nav.getCurrentlyPlayingServiceReference()
            if fileExists(self.origServiceDataBkpFile) and config.plugins.IPAudio.running.value == ':'.join(service.toString().split(':')[:11]):
                self.ipaudio = True
                
        
        def __evEnd(self):
            if self.ipaudio:
                self.undoLameDbServiceDataChanges()
                self.ipaudio = False
                
             
        def loadServiceDataFromBackupIfExists(self, fileName, options):
            return self.readFromFileIfExists(fileName, options)
        
        
        def readFromFileIfExists(self, fileName, options):
            if fileExists(fileName):
                with open(fileName, options) as file:
                    return file.read().replace('\n', '').strip()
            return ""
           
        def reloadServiceAndBouquetList(self):
            self.eDVBDB = eDVBDB.getInstance()
            self.eDVBDB.reloadServicelist()
            self.eDVBDB.reloadBouquets()   
             
        def undoLameDbServiceDataChanges(self):
            kill_pid()
            origServiceData = self.loadServiceDataFromBackupIfExists(self.origServiceDataBkpFile, 'r')
            if origServiceData != "":
                updateServiceDataCmd = "/bin/sed -i '/" + origServiceData.split("$$$")[0] + "/ { n; n; s/.*/" + origServiceData.split("$$$")[1] + "/I; }' /etc/enigma2/lamedb"
                subprocess.call([updateServiceDataCmd], shell=True)
                os.remove(self.origServiceDataBkpFile)
                self.reloadServiceAndBouquetList() 
            config.plugins.IPAudio.running.value = ""
            config.plugins.IPAudio.running.save()
        
        def gotSession(self):
            keymap = resolveFilename(SCOPE_PLUGINS, "Extensions/IPAudio/keymap.xml")
            global globalActionMap
            readKeymap(keymap)
            globalActionMap.actions['audioSelection'] = self.ShowHide

        def ShowHide(self):
            self.session.open(IPAudioScreen)
            
            
def sessionstart(reason, session=None, **kwargs):
    if reason == 0:
        IPAudio(session).gotSession()
        

def main(session, **kwargs):
    session.open(IPAudioScreen)


def Plugins(**kwargs):
    Descriptors = []
    Descriptors.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart))
    Descriptors.append(PluginDescriptor(name="IPAudio", description="IPAudio",where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
    return Descriptors

