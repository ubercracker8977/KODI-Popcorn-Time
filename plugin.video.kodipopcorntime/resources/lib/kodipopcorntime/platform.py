#!/usr/bin/python
import sys, os
from kodipopcorntime.msg import AnErrorOccurred

class Platform:
    def __init__(self):
        self.arch = self.arch()
        self.system = self.system()

    def __str__(self):
        return "%s/%s" % (self.system, self.arch)

    @staticmethod
    def arch():
        if sys.platform.startswith('linux') and (os.uname()[4].startswith('arm') or os.uname()[4].startswith('aarch')):
            return 'arm'
        elif sys.maxsize > 2**32:
            return 'x64'
        else:
            return 'x86'

    @staticmethod
    def system():
        if sys.platform.startswith('linux'):
            if 'ANDROID_DATA' in os.environ:
                return 'android'
            else:
                return 'linux'
        elif sys.platform.startswith('win'):
            return 'windows'
        elif sys.platform.startswith('darwin'):
            return 'darwin'
        else:
            raise AnErrorOccurred(30302)
