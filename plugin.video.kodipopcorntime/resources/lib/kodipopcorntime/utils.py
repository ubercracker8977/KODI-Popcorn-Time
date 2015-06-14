import os, xbmcgui, urllib, urllib2, zlib, types, xbmc
try:
    import simplejson as json
except ImportError:
    import json
from contextlib import closing
from functools import wraps
from subprocess import Popen, PIPE
from kodipopcorntime.common import plugin, AnErrorOccurred

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36"

def first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

def url_get(url, params={}, headers={}):
    if params:
        url = "".join([url, "?", urlencode(params)])

    req = urllib2.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept-Encoding", "gzip")
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with closing(urllib2.urlopen(req)) as response:
            data = response.read()
            if response.headers.get("Content-Encoding", "") == "gzip":
                return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)
            return data
            return data and json.loads(data) or {}
    except urllib2.HTTPError, e:
        strerror = "http error: ({url}) [{code}] {reason}".format(url=url, code=e.code, reason=e.reason)
    except:
        strerror = "Unknown error: {url}".format(url=url)
    raise AnErrorOccurred(30304, strerror)

def ensure_fanart(fn):
    """Makes sure that if the listitem doesn't have a fanart, we properly set one."""
    @wraps(fn)
    def _fn(*a, **kwds):
        items = fn(*a, **kwds)
        if items is None:
            return
        if isinstance(items, types.GeneratorType):
            items = list(items)
        for item in items:
            properties = item.setdefault("properties", {})
            if not properties.get("fanart_image"):
                properties["fanart_image"] = plugin.addon.getAddonInfo("fanart")
        return items
    return _fn

# Sometimes, when we do things too fast for XBMC, it doesn't like it.
# Sometimes, it REALLY doesn't like it.
# This class is here to make sure we are slow enough.
class SafeDialogProgress(xbmcgui.DialogProgress):
    def __init__(self, delay_create=1000, delay_close=1000):
        self._delay_create = delay_create
        self._delay_close = delay_close

    def create(self, *args, **kwargs):
        xbmc.sleep(self._delay_create)
        super(SafeDialogProgress, self).create(*args, **kwargs)

    def close(self, *args, **kwargs):
        xbmc.sleep(self._delay_close)
        super(SafeDialogProgress, self).close(*args, **kwargs)

def get_mount_filesystem(mount_point):
    for line in Popen(["/system/bin/mount"], stdout=PIPE).stdout:
        dev, mp, fs, opts, _, _ = line.split(" ")
        if mount_point == mp:
            return fs

def get_mount_point(path):
    path = os.path.realpath(os.path.abspath(path))
    while path != os.path.sep:
        if os.path.ismount(path):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    return path

def get_path_fs(path):
    return get_mount_filesystem(get_mount_point(path))
