import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import sys
which = sys.argv[1]

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

if which == "commands":
    path = xbmcvfs.translatePath('special://home/addons/script.tvguide.fullscreen/commands.txt')
elif which == "autoplaywith":
    path = xbmcvfs.translatePath('special://home/addons/script.tvguide.fullscreen/resources/playwith/readme.txt')
f = xbmcvfs.File(path,"rb")
data = f.read()
dialog = xbmcgui.Dialog()
dialog.textviewer('Help', data)
