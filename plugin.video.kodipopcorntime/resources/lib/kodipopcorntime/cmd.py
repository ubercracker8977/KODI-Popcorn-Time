#!/usr/bin/python
import os, glob, xbmcgui, sys
from kodipopcorntime.plugin import plugin
from kodipopcorntime.msg import notify
from kodipopcorntime.path import CACHE_DIR

__addon__ = sys.modules['__main__'].__addon__

def clear_cache():
    for directory in [CACHE_DIR, plugin.storage_path]:
        for dbfile in glob.glob(os.path.join(directory, "*.db")):
            os.remove(dbfile)
    for file in glob.glob(CACHE_DIR + '/*'):
        os.remove(file)
    notify(__addon__.getLocalizedString(30301))

def clear_content():
    import shutil, xbmc
    for file in glob.glob(os.path.join(xbmc.validatePath(xbmc.translatePath(__addon__.getSetting("download_path"))), "*")):
        shutil.rmtree(file, True)
    notify(__addon__.getLocalizedString(30322))

def reset_torrent_settings():
    if xbmcgui.Dialog().yesno(heading=__addon__.getLocalizedString(30012), line1=__addon__.getLocalizedString(30013), line2=__addon__.getLocalizedString(30014)):
        # Files
        __addon__.setSetting("keep_files", 'false')
        __addon__.setSetting("keep_complete", 'false')
        __addon__.setSetting("keep_incomplete", 'false')
        # Network
        __addon__.setSetting("connections_limit", '200')
        __addon__.setSetting("encryption", '1')
        # Port
        __addon__.setSetting("listen_port", '6881')
        __addon__.setSetting("use_random_port", 'false')
        # Peers
        __addon__.setSetting("torrent_connect_boost", '50')
        __addon__.setSetting("connection_speed", '50')
        __addon__.setSetting("peer_connect_timeout", '15')
        __addon__.setSetting("min_reconnect_time", '60')
        __addon__.setSetting("max_failcount", '3')
        # Features
        __addon__.setSetting("enable_tcp", 'true')
        __addon__.setSetting("enable_dht", 'true')
        __addon__.setSetting("enable_lsd", 'true')
        __addon__.setSetting("enable_utp", 'true')
        __addon__.setSetting("enable_scrape", 'false')
        __addon__.setSetting("enable_upnp", 'true')
        __addon__.setSetting("enable_natpmp", 'true')
        # Additional
        __addon__.setSetting("trackers", '')
        __addon__.setSetting("dht_routers", '')
        # Log / Debug
        __addon__.setSetting("debug_alerts", 'true')
        __addon__.setSetting("log_stats", 'true')
        notify(__addon__.getLocalizedString(30314))
