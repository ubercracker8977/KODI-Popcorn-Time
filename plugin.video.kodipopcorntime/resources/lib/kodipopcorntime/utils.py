#!/usr/bin/python
import os, xbmcgui, zlib, types, xbmc, urllib2, simplejson, sys
from urllib import urlencode
from contextlib import closing
from functools import wraps
from kodipopcorntime.msg import AnErrorOccurred, log
from kodipopcorntime import proxy

__addon__ = sys.modules['__main__'].__addon__

def url_get(domain, uri, params={}, headers={}, proxyid=None):
    querystring = ""
    if params:
        querystring = "".join(['?', urlencode(params)])
    if proxyid:
        log("(urllib2) Proxy domain is activated", xbmc.LOGDEBUG)
    for pd in (proxyid and proxy.update_list(proxyid, domain) or [domain]):
        url = "".join([pd, uri, querystring])

        req = urllib2.Request(url)
        log("(urllib2) (Request URL) "+url, xbmc.LOGDEBUG)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36")
        log("(urllib2) (Request header) User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36", xbmc.LOGDEBUG)
        req.add_header("Accept-Encoding", "gzip")
        log("(urllib2) (Request header) Accept-Encoding: gzip", xbmc.LOGDEBUG)
        for k, v in headers.items():
            req.add_header(k, v)
            log("(urllib2) (Request header) {key}: {val}".format(key=k, val=v), xbmc.LOGDEBUG)

        try:
            with closing(urllib2.urlopen(req, timeout=20)) as response:
                res = response.read()
                if response.headers.get("Content-Encoding", "") == "gzip":
                    log("(urllib2) The content is gzip compressed", xbmc.LOGDEBUG)
                    res = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(res)
                if res:
                    data = simplejson.loads(res)
                    if proxyid:
                        log("(urllib2) Proxy domain ({proxydomaine}) worked and will be given as first choice in the future".format(proxydomaine=pd), xbmc.LOGDEBUG)
                        proxy.set_default(proxyid, pd)
                    log("(urllib2) Done", xbmc.LOGDEBUG)
                    return data
                raise AnErrorOccurred(0)
        except urllib2.HTTPError as e:
            log("(urllib2) http error: ({url}) [{code}] {reason}".format(url=url, code=e.code, reason=e.reason), xbmc.LOGERROR)
        except ValueError as e:
            log("(urllib2) JSON error: {e} ({url})".format(e=e, url=url), xbmc.LOGERROR)
        except AnErrorOccurred as e:
            log("(urllib2) Empty or wrrong response: "+url, xbmc.LOGERROR)
        except:
            log("(urllib2) Unknown error: "+url, xbmc.LOGERROR)

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
                properties["fanart_image"] = __addon__.getAddonInfo("fanart")
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

def cleanDictList(DictList):
    if isinstance(DictList, dict):
        items = {}
        for v in [(key, cleanDictList(value)) for key, value in DictList.items() if value]:
            if v[1]:
                items[v[0]] = v[1]
        return items
    if isinstance(DictList, list):
        return [v for v in [cleanDictList(value) for value in DictList if value] if v]
    return DictList