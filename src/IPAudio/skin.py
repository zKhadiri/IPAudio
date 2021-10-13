from Screens.Screen import Screen
from enigma import getDesktop
import os

def getDesktopSize():
	s = getDesktop(0).size()
	return (s.width(), s.height())


def isHD():
	desktopSize = getDesktopSize()
	return desktopSize[0] == 1280

def getversioninfo():
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

#### SKIN IPAudioSetup ICOON
if isHD():
	SKIN_IPAudioSetup_ICONE ="""
		<screen name="IPAudioSetup" position="center,center" size="850,400" title="IPAudio Setup" flags="wfNoBorder">
		<ePixmap position="0,0" zPosition="-1" size="850,400" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/setup_screen.png" alphatest="on" />
		<ePixmap position="10,335" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/red.png" alphatest="on" />
		<widget source="red_key" render="Label" position="50,345" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
		<ePixmap position="760,335" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/green.png" alphatest="on" />
		<widget source="green_key" render="Label" position="650,345" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
		<widget position="7,71" size="838,232" name="config" backgroundColor="#202020" foregroundColor="white" itemHeight="58" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/list_setup_pixmap.png" scrollbarMode="showNever" />
		<widget source="Title" position="350,17" size="360,35" render="Label" font="Regular;25" foregroundColor="#3b3b3d" backgroundColor="#16000000" transparent="1" />
		</screen>"""
else:	
	if os.path.exists('/var/lib/dpkg/status'):	
		SKIN_IPAudioSetup_ICONE = """
			<screen name="IPAudioSetup" position="center,center" size="1154,584" title="IPAudio Setup" flags="wfNoBorder">
			<ePixmap position="0,0" zPosition="-1" size="1154,584" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/setup_screen.png" alphatest="on" />
			<ePixmap position="10,500" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/red.png" alphatest="on" />
			<widget source="red_key" render="Label" position="58,510" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<ePixmap position="1060,500" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" alphatest="on" />
			<widget source="green_key" render="Label" position="940,510" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<widget position="8,107" size="1138,350" name="config" backgroundColor="#202020" foregroundColor="white" itemHeight="58" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_setup_pixmap.png" scrollbarMode="showNever" />
			<widget source="Title" position="455,32" size="251,45" render="Label" font="Regular;35" foregroundColor="#3b3b3d" backgroundColor="#16000000" transparent="1" />
			</screen>"""
	else:
		SKIN_IPAudioSetup_ICONE = """
			<screen name="IPAudioSetup" position="center,center" size="1154,584" title="IPAudio Setup" flags="wfNoBorder">
			<ePixmap position="0,0" zPosition="-1" size="1154,584" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/setup_screen.png" alphatest="on" />
			<ePixmap position="10,500" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/red.png" alphatest="on" />
			<widget source="red_key" render="Label" position="58,510" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<ePixmap position="1060,500" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" alphatest="on" />
			<widget source="green_key" render="Label" position="940,510" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<widget position="8,107" size="1138,350" name="config" backgroundColor="#202020" foregroundColor="white" itemHeight="58" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_setup_pixmap.png" font="Regular; 28" scrollbarMode="showNever" />
			<widget source="Title" position="455,32" size="251,45" render="Label" font="Regular;35" foregroundColor="#3b3b3d" backgroundColor="#16000000" transparent="1" />
			</screen>"""

#### SKIN IPAudioSetup Light

if isHD():
	SKIN_IPAudioSetup_Light = """
		<screen name="IPAudioSetup" position="center,center" size="850,400" title="IPAudio Setup" flags="wfNoBorder">
		<eLabel position="center,70" zPosition="-1" size="850,330" backgroundColor="#16000000"/>
		<eLabel position="0,0" zPosition="-1" size="850,70" backgroundColor="#77ffffff"/>
		<ePixmap position="10,350" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/red.png" alphatest="on" />
		<widget source="red_key" render="Label" position="50,360" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
		<ePixmap position="760,350" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/green.png" alphatest="on" />
		<widget source="green_key" render="Label" position="650,360" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
		<widget position="7,71" size="838,273" name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/list_setup_pixmap.png" scrollbarMode="showNever" />
		<widget source="Title" position="350,17" size="360,35" render="Label" font="Regular;25" foregroundColor="#00000000" backgroundColor="#77ffffff" transparent="1" />
		</screen>"""
else:	
	if os.path.exists('/var/lib/dpkg/status'):	
		SKIN_IPAudioSetup_Light = """
			<screen name="IPAudioSetup" position="center,center" size="1154,584" title="IPAudio Setup" flags="wfNoBorder">
			<ePixmap position="0,0" zPosition="-1" size="1154,584" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/setup_screen.png" alphatest="on" />
			<<ePixmap position="10,520" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/red.png" alphatest="on" />
			<widget source="red_key" render="Label" position="58,530" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<ePixmap position="1060,520" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" alphatest="on" />
			<widget source="green_key" render="Label" position="940,530" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<widget position="8,107" size="1138,410" name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" itemHeight="68" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_setup_pixmap.png" scrollbarMode="showNever" />
			<widget source="Title" position="455,32" size="251,45" render="Label" font="Regular;35" foregroundColor="#00000000" backgroundColor="#77ffffff" transparent="1" />
			</screen>"""
	else:
		SKIN_IPAudioSetup_Light = """
			<screen name="IPAudioSetup" position="center,center" size="1154,584" title="IPAudio Setup" flags="wfNoBorder">
			<eLabel position="center,108" zPosition="-1" size="1154,584" backgroundColor="#16000000"/>
			<eLabel position="center,0" zPosition="-1" size="1154,104" backgroundColor="#77ffffff"/>
			<ePixmap position="10,520" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/red.png" alphatest="on" />
			<widget source="red_key" render="Label" position="58,530" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<ePixmap position="1060,520" zPosition="1" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" alphatest="on" />
			<widget source="green_key" render="Label" position="940,530" zPosition="2" size="165,30" font="Regular; 26" halign="center" valign="center" transparent="1" />
			<widget position="8,107" size="1138,410" name="config" foregroundColor="#00ffffff" backgroundColor="#16000000" itemHeight="68" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_setup_pixmap.png" font="Regular; 32" scrollbarMode="showNever" />
			<widget source="Title" position="455,32" size="251,45" render="Label" font="Regular;35" foregroundColor="#00000000" backgroundColor="#77ffffff" transparent="1" />
			</screen>"""

#### SKIN IPAudioScreen ICOON
if isHD():
	SKIN_IPAudioScreen_ICONE="""
		<screen name="IPAudio" position="center,center" size="1280,720" title="IPAudio By ZIKO V {}" backgroundColor="#ffffffff" flags="wfNoBorder">
		<ePixmap position="0,0" zPosition="-1" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/bg_screen_hd.png" alphatest="on" />
		<ePixmap position="54,151" zPosition="2" size="447,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/list_1pixmap.png" alphatest="on" />
		<ePixmap position="458,170" zPosition="2" size="39,15" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/left_right_zap.png" alphatest="on" />
		<widget source="Title" position="141,72" size="360,35" render="Label" font="Regular;25" foregroundColor="#3b3b3d" backgroundColor="#16000000" transparent="1" />
		<widget font="Regular;30" foregroundColor="#3b3b3d" backgroundColor="#16000000" halign="center" position="637,63" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
	  		<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="server" font="Regular;22" foregroundColor="white" backgroundColor="#16000000" position="207,162" size="289,55" transparent="1" zPosition="5" />
		<ePixmap name="green" position="58,246" zPosition="2" size="60,45" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/green.png" transparent="1" alphatest="on" />
		<widget name="key_green" position="40,255" size="250,30" valign="center" halign="center" zPosition="4" foregroundColor="white" backgroundColor="#202020" font="Regular;16" transparent="1" />
		<widget name="list" foregroundColor="white" backgroundColor="#202020" position="518,110" size="404,465" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/list_2pixmap.png" scrollbarMode="showNever" zPosition="2" />
		<ePixmap position="448,255" size="50,18" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/key_menu.png" alphatest="on" zPosition="5" />
		<widget name="sync" foregroundColor="white" backgroundColor="#252525" position="56,282" size="443,17" font="Regular;15" />
  		</screen>""".format(Ver)
else:		
	SKIN_IPAudioScreen_ICONE="""
		<screen name="IPAudio" position="center,center" size="1920,1080" title="IPAudio By ZIKO V {}" backgroundColor="#ffffffff" flags="wfNoBorder">
		<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/bg_screen_fullhd.png" alphatest="on" />
		<ePixmap position="85,247" zPosition="2" size="666,58" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_1pixmap.png" alphatest="on" />
		<ePixmap position="695,268" zPosition="2" size="52,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/left_right_zap.png" alphatest="on" />
		<widget source="Title" position="274,115" size="425,40" render="Label" font="Regular;30" foregroundColor="#3b3b3d" backgroundColor="white" transparent="1" />
		<widget font="Regular;35" foregroundColor="#3b3b3d" backgroundColor="white" halign="center" position="1015,108" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
	  		<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="server" font="Regular;32" foregroundColor="white" backgroundColor="#16000000" position="200,255" size="400,40" halign="center" valign="center" transparent="1" zPosition="5" />
		<ePixmap name="green" position="86,375" zPosition="2" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" transparent="1" alphatest="on" />
		<widget name="key_green" position="100,385" size="250,30" valign="center" halign="center" zPosition="4" foregroundColor="white" backgroundColor="#202020" font="Regular;19" transparent="1" />
		<widget name="list" foregroundColor="white" backgroundColor="#202020" position="783,177" size="599,699" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_2pixmap.png" scrollbarMode="showNever" zPosition="2" />
		<ePixmap position="689,387" size="60,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/key_menu.png" alphatest="on" zPosition="5" />
		<widget name="sync" foregroundColor="white" backgroundColor="#252525" position="86,418" size="667,28" font="Regular;20" />
  		</screen>""".format(Ver)

#### SKIN IPAudioScreen Light
if isHD():
	SKIN_IPAudioScreen_Light="""
		<screen name="IPAudio" position="center,center" size="1280,720" title="IPAudio By ZIKO V {}" backgroundColor="#ffffffff" flags="wfNoBorder">
		<eLabel position="512,131" zPosition="-1" size="420,500" backgroundColor="#16000000"/>
		<eLabel position="35,131" zPosition="-1" size="470,178" backgroundColor="#16000000"/>
		<eLabel position="35,64" zPosition="-1" size="470,66" backgroundColor="#77ffffff"/>
		<eLabel position="512,64" zPosition="1" size="420,66" backgroundColor="#77ffffff"/>
		<ePixmap position="458,170" zPosition="2" size="39,15" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/left_right_zap.png" alphatest="on" />
		<widget source="Title" position="141,82" size="360,35" render="Label" font="Regular;25" foregroundColor="#00000000" backgroundColor="#77ffffff" transparent="1" />
		<widget font="Regular;30" foregroundColor="#00000000" backgroundColor="#77ffffff" halign="center" position="637,82" render="Label" size="143,35" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
	  		<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="server" font="Regular;22" foregroundColor="#00ffffff" backgroundColor="#16000000" position="207,162" size="289,55" transparent="1" zPosition="5" />
		<ePixmap name="green" position="58,246" zPosition="2" size="60,45" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/green.png" transparent="1" alphatest="on" />
		<widget name="key_green" position="55,255" size="250,30" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;16" transparent="1" />
		<widget name="list" foregroundColor="#00ffffff" backgroundColor="#16000000" position="518,135" size="404,465" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/list_2pixmap.png" scrollbarMode="showNever" zPosition="2" />
		<ePixmap position="448,255" size="50,18" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/HD/key_menu.png" alphatest="on" zPosition="5" />
		<widget name="sync" foregroundColor="#00ffffff" backgroundColor="#16000000" position="56,285" size="443,22" font="Regular;18" />
  		</screen>""".format(Ver)
else:
	SKIN_IPAudioScreen_Light="""
		<screen name="IPAudio" position="center,center" size="1920,1080" title="IPAudio By ZIKO V {}" backgroundColor="#ffffffff" flags="wfNoBorder">
		<eLabel position="775,171" zPosition="-1" size="614,708" backgroundColor="#16000000"/>
		<eLabel position="85,171" zPosition="-1" size="666,280" backgroundColor="#16000000"/>
		<eLabel position="85,99" zPosition="-1" size="666,66" backgroundColor="#77ffffff"/>
		<eLabel position="775,99" zPosition="1" size="614,66" backgroundColor="#77ffffff"/>
		<ePixmap position="695,270" zPosition="2" size="52,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/left_right_zap.png" alphatest="on" />
		<widget source="Title" position="274,115" size="425,40" render="Label" font="Regular;30" foregroundColor="#00000000" backgroundColor="#77ffffff" transparent="1" />
		<widget font="Regular;35" foregroundColor="#00000000" backgroundColor="#77ffffff" halign="center" position="1015,108" render="Label" size="143,52" source="global.CurrentTime" transparent="1" valign="center" zPosition="5">
	  		<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="server" font="Regular;32" foregroundColor="#00ffffff" backgroundColor="#16000000" position="161,255" size="523,55" transparent="1" zPosition="5" />
		<ePixmap name="green" position="86,375" zPosition="2" size="80,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/green.png" transparent="1" alphatest="on" />
		<widget name="key_green" position="140,385" size="250,30" valign="center" halign="center" zPosition="4" foregroundColor="#00ffffff" backgroundColor="#16000000" font="Regular;25" transparent="1" />
		<widget name="list" foregroundColor="#00ffffff" backgroundColor="#16000000" position="783,177" size="599,699" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/list_2pixmap.png" scrollbarMode="showNever" zPosition="2" />
		<ePixmap position="689,387" size="60,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/IPAudio/icons/FHD/key_menu.png" alphatest="on" zPosition="5" />
		<widget name="sync" foregroundColor="#00ffffff" backgroundColor="#16000000" position="86,418" size="660,28" font="Regular;26" />
  		</screen>""".format(Ver)
