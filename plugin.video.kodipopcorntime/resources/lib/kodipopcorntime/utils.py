#!/usr/bin/python
import xbmcgui, zlib, xbmc, simplejson, sys, time, os, UserDict, httplib, errno, socket
from urlparse import urlparse
from urllib import urlencode
from contextlib import closing
from kodipopcorntime.exceptions import Error, HTTPError
from kodipopcorntime.logging import log, LOGLEVEL
from kodipopcorntime.settings import ISOTRANSLATEINDEX, addon as _settings
from kodipopcorntime.threads import FLock

__addon__ = sys.modules['__main__'].__addon__

class NOTIFYLEVEL:
    INFO = 0
    WARNING = 1
    ERROR = 2

def notify(messageID=0, message=None, level=NOTIFYLEVEL.INFO):
    delay = 3500
    if level == NOTIFYLEVEL.WARNING:
        image = _settings.warning_image
    elif level == NOTIFYLEVEL.ERROR:
        delay = 6000
        image = _settings.error_image
    else:
        image = _settings.info_image

    xbmc.executebuiltin('XBMC.Notification("%s", "%s", "%s", "%s")' %(messageID and __addon__.getLocalizedString(messageID) or message, _settings.name, delay, image))

class ListItem:
    '''
    xbmcswift2.listitem
    ------------------
    A wrapper for the xbmcgui.ListItem class. The class keeps track
    of any set properties that xbmcgui doesn't expose getters for.

    :modified: Diblo at 2015-08-15

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
    '''
    def __init__(self, label='', label2='', icon=None, thumbnail=None, path=None):
        self._listitem = xbmcgui.ListItem(label=label, label2=label2, iconImage=icon, thumbnailImage=thumbnail, path=path)
        # xbmc doesn't make getters available for these properties so we'll
        # keep track on our own
        self._icon = icon
        self._path = path
        self._thumbnail = thumbnail
        self._context_menu_items = []
        self.is_folder = True

    def __repr__(self):
        return ("<ListItem '%s'>" % self.label).encode('utf-8')

    def __str__(self):
        return ('%s (%s)' % (self.label, self.path)).encode('utf-8')

    def get_context_menu_items(self):
        '''Returns the list of currently set context_menu items.'''
        return self._context_menu_items

    def add_context_menu_items(self, items, replace_items=False):
        '''Adds context menu items. If replace_items is True all
        previous context menu items will be removed.
        '''
        for label, action in items:
            assert isinstance(label, basestring)
            assert isinstance(action, basestring)
        if replace_items:
            self._context_menu_items = []
        self._context_menu_items+items
        self._listitem.addContextMenuItems(items, replace_items)

    def get_label(self):
        '''Sets the listitem's label'''
        return self._listitem.getLabel()

    def set_label(self, label):
        '''Returns the listitem's label'''
        return self._listitem.setLabel(label)

    label = property(get_label, set_label)

    def get_label2(self):
        '''Returns the listitem's label2'''
        return self._listitem.getLabel2()

    def set_label2(self, label):
        '''Sets the listitem's label2'''
        return self._listitem.setLabel2(label)

    label2 = property(get_label2, set_label2)

    def is_selected(self):
        '''Returns True if the listitem is selected.'''
        return self._listitem.isSelected()

    def select(self, selected_status=True):
        '''Sets the listitems selected status to the provided value.
        Defaults to True.
        '''
        return self._listitem.select(selected_status)

    selected = property(is_selected, select)

    def set_info(self, type, info_labels):
        '''Sets the listitems info'''
        return self._listitem.setInfo(type, info_labels)

    def get_property(self, key):
        '''Returns the property associated with the given key'''
        return self._listitem.getProperty(key)

    def set_property(self, key, value):
        '''Sets a property for the given key and value'''
        return self._listitem.setProperty(key, value)

    def add_stream_info(self, stream_type, stream_values):
        '''Adds stream details'''
        return self._listitem.addStreamInfo(stream_type, stream_values)

    def get_icon(self):
        '''Returns the listitem's icon image'''
        return self._icon

    def set_icon(self, icon):
        '''Sets the listitem's icon image'''
        self._icon = icon
        return self._listitem.setIconImage(icon)

    icon = property(get_icon, set_icon)

    def get_thumbnail(self):
        '''Returns the listitem's thumbnail image'''
        return self._thumbnail

    def set_thumbnail(self, thumbnail):
        '''Sets the listitem's thumbnail image'''
        self._thumbnail = thumbnail
        return self._listitem.setThumbnailImage(thumbnail)

    thumbnail = property(get_thumbnail, set_thumbnail)

    def get_path(self):
        '''Returns the listitem's path'''
        return self._path

    def set_path(self, path):
        '''Sets the listitem's path'''
        self._path = path
        return self._listitem.setPath(path)

    path = property(get_path, set_path)

    def get_is_playable(self):
        '''Returns True if the listitem is playable, False if it is a
        directory
        '''
        return not self.is_folder

    def set_is_playable(self, is_playable):
        '''Sets the listitem's playable flag'''
        value = 'false'
        if is_playable:
            value = 'true'
        self.set_property('isPlayable', value)
        self.is_folder = not is_playable

    playable = property(get_is_playable, set_is_playable)

    def as_tuple(self):
        '''Returns a tuple of list item properties:
            (path, the wrapped xbmcgui.ListItem, is_folder)
        '''
        return self.path, self._listitem, self.is_folder

    def as_xbmc_listitem(self):
        '''Returns the wrapped xbmcgui.ListItem'''
        return self._listitem

    @classmethod
    def from_dict(cls, label=None, label2=None, icon=None, thumbnail=None,
                  path=None, selected=None, info=None, properties=None,
                  context_menu=None, replace_context_menu=False,
                  is_playable=None, info_type='video', stream_info=None):
        '''A ListItem constructor for setting a lot of properties not
        available in the regular __init__ method. Useful to collect all
        the properties in a dict and then use the **dct to call this
        method.
        '''
        listitem = cls(label, label2, icon, thumbnail, path)

        if selected is not None:
            listitem.select(selected)

        if info:
            listitem.set_info(info_type, info)

        if is_playable:
            listitem.set_is_playable(True)

        if properties:
            # Need to support existing tuples, but prefer to have a dict for
            # properties.
            if hasattr(properties, 'items'):
                properties = properties.items()
            for key, val in properties:
                listitem.set_property(key, val)

        if stream_info:
            for stream_type, stream_values in stream_info.items():
                listitem.add_stream_info(stream_type, stream_values)

        if context_menu:
            listitem.add_context_menu_items(context_menu, replace_context_menu)

        return listitem

class Cache(UserDict.DictMixin):
    def __init__(self, filename, ttl=0, readOnly=False, last_changed=0):
        self._path      = os.path.join(_settings.cache_path, filename)
        self._readOnly  = readOnly
        self._db        = {}
        self._lock      = FLock(self._path)

        if os.path.isfile(self._path):
            with open(self._path, "r") as _o:
                self._db = _o.read()

        if self._readOnly:
            self._lock.unLock(self._path)

        if self._db:
            self._db = simplejson.loads(self._db)

        if not self._db or not ttl == 0 and (time.time() - self._db["created_at"]) > ttl or self._db["created_at"] < last_changed:
            self._db = {
                "created_at": time.time(),
                "data": {}
            }

    def __enter__(self):
        return self

    def __contains__(self, key):
        return key in self._db['data']

    def has_key(self, key):
        return key in self._db['data']

    def __getitem__(self, key):
        return self._db['data'][key]

    def get(self, key, default=None):
        try:
            return self._db['data'][key]
        except KeyError:
            sys.exc_clear()
            return default

    def copy(self):
        return self._db['data']

    def __setitem__(self, key, value):
        self._db['data'][key] = value

    def extendKey(self, key, value):
        try:
            self._db['data'][key] = self._db['data'][key] + value
        except KeyError:
            sys.exc_clear()
            self._db['data'][key] = value

    def __delitem__(self, key):
        del self._db['data'][key]

    def trunctate(self, data={}):
        self._db['data'] = dict(data)

    def __iter__(self):
        for k in self._db['data'].keys():
            yield k

    def keys(self):
        return self._db['data'].keys()

    def __len__(self):
        return len(self._db['data'])

    def __nonzero__(self):
        if len(self._db['data']) > 0:
            return True
        return False

    def __str__(self):
        return str(self._db['data'])

    def format(self):
        return self._build_str(self._db['data'])

    def _build_str(self, cache, level=0):
        pieces = []
        tabs = ""
        for i in xrange(level):
            tabs = tabs+'\t'
        joinStr = '%s\t, %s\t\n' %(tabs, tabs)
        if isinstance(cache, dict):
            for key, value in cache.items():
                pieces.append("'%s': %s" %(key, self._build_str(value), level+1))
            return '%s{\n%s\t%s\n%s}\n' %(tabs, tabs, joinStr.join(pieces), tabs)
        elif isinstance(cache, list):
            for value in cache:
                pieces.append('%s' %(self._build_str(value), level+1))
            return '%s[\n%s\t%s\n%s]\n' %(tabs, tabs, joinStr.join(pieces), tabs)
        return str(cache)

    def __exit__(self, *exc_info):
        self.close()
        return not exc_info[0]

    def __del__(self):
        if hasattr(self, '_db'):
            self.close()

    def close(self):
        if not self._readOnly and self._db:
            with open(self._path, "w") as _o:
                _o.write(simplejson.dumps(self._db, encoding='UTF-8'))
            self._lock.unLock(self._path)
        self._lock = None
        self._db   = {}

# Sometimes, when we do things too fast for XBMC, it doesn't like it.
# Sometimes, it REALLY doesn't like it.
# This class is here to make sure we are slow enough.
class SafeDialogProgress(xbmcgui.DialogProgress):
    def __init__(self):
        self._mentions = 0
        self._counter  = 0
        super(SafeDialogProgress, self).__init__()

    def create(self, *args, **kwargs):
        time.sleep(0.750)
        super(SafeDialogProgress, self).create(*args, **kwargs)

    def set_mentions(self, number):
        """ set jobs for progress """
        self._mentions = number

    def update(self, count=0, line1='', line2='', line3='', fixValue=0):
        percent = 0
        self._counter = self._counter+count
        if self._mentions:
            percent = int(self._counter*100/self._mentions)
            if percent > 100:
                percent = 100
        super(SafeDialogProgress, self).update(percent, line1=line1, line2=line2, line3=line3)

    def __del__(self):
        if hasattr(self, '_counter'):
            super(SafeDialogProgress, self).close()

class Dialog(xbmcgui.Dialog):
    def yesno(self, line1, line2='', line3='', heading='', nolabel='', yeslabel='', autoclose=0):
        if heading:
            heading  = __addon__.getLocalizedString(heading)
        else:
            heading  = _settings.name
        if line2:
            line2    = __addon__.getLocalizedString(line2)
        if line3:
            line3    = __addon__.getLocalizedString(line3)
        if nolabel:
            nolabel  = __addon__.getLocalizedString(nolabel)
        if yeslabel:
            yeslabel = __addon__.getLocalizedString(yeslabel)

        return super(Dialog, self).yesno(heading, __addon__.getLocalizedString(line1), line2, line3, nolabel, yeslabel, autoclose)

def cleanDictList(DictList):
    if isinstance(DictList, dict):
        return dict((k, v) for k, v in dict((key, cleanDictList(value)) for key, value in DictList.items() if value).items() if v)
    if isinstance(DictList, list):
        return [v for v in [cleanDictList(value) for value in DictList if value] if v]
    return DictList

def isoToLang(iso):
    translateID = ISOTRANSLATEINDEX.get(iso)
    if translateID:
        return __addon__.getLocalizedString(translateID)
    return None

def build_magnetFromMeta(torrent_hash, dn):
    return "magnet:?xt=urn:btih:%s&%s" % (torrent_hash, urlencode({'dn' : dn}, doseq=True))

def get_free_port(port=5001):
    """
    Check we can bind to localhost with a specified port
    On failer find a new TCP port that can be used for binding
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
        s.close()
    except socket.error:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
            s.close()
        except socket.error:
            raise Error("Can not find a TCP port to bind torrent2http", 30300)
    return port