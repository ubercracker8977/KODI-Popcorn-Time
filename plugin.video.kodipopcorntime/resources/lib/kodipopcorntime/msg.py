#!/usr/bin/python
import xbmc, sys, traceback

__addon__ = sys.modules['__main__'].__addon__

def notify(msg, title=None, delay=5000, image=''):
    if title is None:
        title = __addon__.getAddonInfo('name')
    xbmc.executebuiltin('XBMC.Notification("{msg}", "{title}", "{delay}", "{image}")'.format(msg=msg, title=title, delay=delay, image=image))

def log(msg, level=0):
    xbmc.log(msg='[{id}] {msg}'.format(id=__addon__.getAddonInfo("id"), msg=msg), level=level)

def log_traceback(level=0):
    for line in traceback.format_exc().split("\n"):
        if line:
            log(line, level)

class AnErrorOccurred(Exception):
    def __init__(self, errno):
        self.errno = errno

def errorNotify(number):
    msg = __addon__.getLocalizedString(number)
    notify(msg=msg, title=__addon__.getLocalizedString(30306), delay=8000)
    log(msg, xbmc.LOGERROR)
    log_traceback(xbmc.LOGERROR)

def torrentError(error):
    """
    :type error: Error
    """
    if error.code == error.UNKNOWN_PLATFORM:
        strerror = __addon__.getLocalizedString(30302)
    elif error.code == error.XBMC_HOME_NOT_DEFINED:
        strerror = __addon__.getLocalizedString(30309)
    elif error.code == error.NOEXEC_FILESYSTEM:
        strerror = error.message
    elif error.code == error.PROCESS_ERROR:
        strerror = __addon__.getLocalizedString(30303)
    elif error.code == error.BIND_ERROR:
        strerror = __addon__.getLocalizedString(30300)
    elif error.code == error.POPEN_ERROR:
        strerror = error.message
    elif error.code == error.REQUEST_ERROR:
        strerror = error.message
    elif error.code == error.INVALID_FILE_INDEX:
        strerror = error.message
    elif error.code == error.INVALID_DOWNLOAD_PATH:
        strerror = error.message
    elif error.code == error.TIMEOUT:
        strerror = error.message
    elif error.code == error.TORRENT_ERROR:
        strerror = __addon__.getLocalizedString(30308)
    elif error.code == error.CRASHED:
        strerror = __addon__.getLocalizedString(30311)
    notify(msg=strerror, title=__addon__.getLocalizedString(30312), delay=8000)
    log(error.message, xbmc.LOGERROR)
    log_traceback(xbmc.LOGERROR)

