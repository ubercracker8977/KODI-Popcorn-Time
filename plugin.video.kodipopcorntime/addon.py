#!/usr/bin/python
import sys, os, xbmcaddon
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
__addon__ = xbmcaddon.Addon()
from kodipopcorntime import main

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    main.run()
