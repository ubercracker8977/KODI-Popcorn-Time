#!/usr/bin/python
import os, xbmc, sys

__addon__ = sys.modules['__main__'].__addon__

def cacheDir():
    dir = xbmc.translatePath("special://profile/addon_data/%s/cache" % __addon__.getAddonInfo("id"))
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
CACHE_DIR = cacheDir()

RESOURCES_PATH = os.path.join(__addon__.getAddonInfo('path'), 'resources')

