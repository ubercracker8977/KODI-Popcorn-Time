#!/usr/bin/python
import os, re, xbmc, traceback, sys
from kodipopcorntime.threads import Thread
__addon__ = sys.modules['__main__'].__addon__

_id = __addon__.getAddonInfo('id')
if __addon__.getSetting("debug") == 'true':
    _lognames = [
        u'  DEBUG: ',
        u'   INFO: ',
        u' NOTICE: ',
        u'WARNING: ',
        u'  ERROR: ',
        u'  FATAL: '
    ]
    _loglevel = [xbmc.LOGNONE, xbmc.LOGNONE, xbmc.LOGNONE, xbmc.LOGNONE, xbmc.LOGNONE, xbmc.LOGNONE]
else:
    _lognames = ['', '', '', '', '', '']
    _loglevel = [xbmc.LOGDEBUG, xbmc.LOGINFO, xbmc.LOGNOTICE, xbmc.LOGWARNING, xbmc.LOGERROR, xbmc.LOGFATAL]

class LOGLEVEL:
    DEBUG    = 0
    INFO     = 1
    NOTICE   = 2
    WARNING  = 3
    ERROR    = 4
    FATAL    = 5

def log(message, level=LOGLEVEL.DEBUG):
    if isinstance(message, str):
        message = unicode(message, errors='ignore')
    xbmc.log(msg=u'%s[%s] %s' %(_lognames[level], _id, message), level=_loglevel[level])

def log_error():
    xbmc.log(msg=u'%s[%s] %s' %(_lognames[LOGLEVEL.FATAL], _id, unicode(traceback.format_exc(), errors='ignore')), level=_loglevel[LOGLEVEL.FATAL])

class LogPipe(Thread):
    def __init__(self, logger):
        self._logger = logger
        self._read_fd, self._write_fd = os.pipe()
        super(LogPipe, self).__init__(target=self.run)

    def fileno(self):
        return self._write_fd

    def run(self):
        self._logger("Logging started")
        with os.fdopen(self._read_fd) as f:
            for line in iter(f.readline, ""):
                line = re.sub(r'^\d+/\d+/\d+ \d+:\d+:\d+ ', '', line)
                self._logger(line.strip())
                if self.stop.is_set():
                    break
        self._logger("Logging finished")

    def close(self):
        super(LogPipe, self).close()
