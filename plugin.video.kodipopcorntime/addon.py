#!/usr/bin/python
import sys, os, xbmcaddon
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
__addon__ = xbmcaddon.Addon()

import simplejson, xbmc, traceback, xbmcgui, hashlib
from contextlib import closing
from torrent2http import Error
from concurrent import futures as conFutures
from kodipopcorntime.plugin import plugin
from kodipopcorntime.msg import AnErrorOccurred, errorNotify, torrentError, log_traceback, log
from kodipopcorntime.utils import ensure_fanart, SafeDialogProgress, cleanDictList
from kodipopcorntime.provider import PROVIDERS, call_provider
from kodipopcorntime.magnet import from_meta_data
from kodipopcorntime.player import Player
from kodipopcorntime.platform import Platform
from kodipopcorntime.caching import route, shelf

def _build_kwargs(base, add, **kwargs):
    base.update(add)
    if kwargs:
        base.update(kwargs)
    return base

def _get_kwargs(add={}):
    # Get kwargs
    kwargs = dict((k, v[0]) for k, v in plugin.request.args.items())
    # Add user kwargs
    kwargs.update(add)

    # Build system kwargs
    qualities_list = [
        ['720p'],
        ['1080p'],
        ['720p','1080p']
    ]
    qualities = qualities_list[int(__addon__.getSetting("quality"))]
    if int(__addon__.getSetting("play3d")) > 0 and int(__addon__.getSetting("quality")) > 0:
        qualities.append('3D')
    sys_kwargs = {
        'limit': 20,
        'qualities': qualities
    }
    provider = kwargs.get('provider', '')
    if provider:
        sys_kwargs['provider'] = provider

    # Secure the right system kwargs are in kwargs
    kwargs.update(sys_kwargs)

    return [kwargs, sys_kwargs]

def _isSettingsChanged():
    with shelf("addon.settings.old", 5000 * 3600) as settings_old:
        settings = [
            xbmc.getLanguage(xbmc.ISO_639_1),
            __addon__.getSetting('sub_language1'),
            __addon__.getSetting('sub_language2'),
            __addon__.getSetting('sub_language3'),
            __addon__.getSetting('hearing_impaired'),
            __addon__.getSetting('quality')
        ]
        if settings_old: 
            if all(s in settings_old['list'] for s in settings):
                return False
        settings_old.update({'list': settings})
    return True

def _shelf_mediainfo(type, item, provider, refresh):
    with shelf("mediainfo.{type}.{md5}".format(type=type, md5=hashlib.md5(simplejson.dumps(item)).hexdigest()), 24 * 3600) as mediainfo:
        if refresh:
            mediainfo.clear()
        if not mediainfo:
            mediainfo.update(cleanDictList(provider.get(item["info"]["code"], item["label"], item["info"]["year"])))
        return mediainfo

@plugin.route("/")
@ensure_fanart
def index():
    try:
        providers_count = len(PROVIDERS['movie'])
        if not providers_count > 0:
            raise AnErrorOccurred(30315)

        if providers_count == 1:
            sys_kwargs = _get_kwargs()[1]
            item = call_provider(PROVIDERS['movie'][0]).catalogs(**sys_kwargs)
            plugin.redirect(plugin.url_for(item.pop('endpoint'), **_build_kwargs(item.pop("kwargs", {}), sys_kwargs, **{'provider': PROVIDERS['movie'][0]})))
        # If we have more end one provider we createt a provider index
        else:
            sys_kwargs = _get_kwargs()[1]
            for provider in PROVIDERS['movie']:
                item = call_provider(provider).catalogs(**sys_kwargs)
                item["path"] = plugin.url_for(item.pop('endpoint'), **_build_kwargs(item.pop("kwargs", {}), sys_kwargs, **{'provider': provider}))
                yield item
    except AnErrorOccurred as e:
        errorNotify(e.errno)
    except:
        errorNotify(30308)

@plugin.route("/catalogs")
@ensure_fanart
def catalogs():
    try:
        kwargs, sys_kwargs = _get_kwargs()
        for item in call_provider(sys_kwargs['provider']).catalogs(**kwargs):
            item["path"] = plugin.url_for(item.pop('endpoint'), **_build_kwargs(item.pop("kwargs", {}), sys_kwargs))
            yield item
    except:
        errorNotify(30308)

@plugin.route("/browse/<provider>/<separate>/<page>")
@ensure_fanart
def browse(provider, separate, page):
    try:
        page = int(page)
        kwargs = _get_kwargs()[0]
        mediaprovider = call_provider(provider)

        with closing(SafeDialogProgress(delay_close=0)) as dialog:
            dialog.create(__addon__.getAddonInfo('name'))
            # Update progress
            dialog.update(0, line1=__addon__.getLocalizedString(30007))

            # Setting content type
            plugin.set_content(mediaprovider.provides)

            # Getting items
            result = None
            with conFutures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(mediaprovider.browse, *(separate, page), **kwargs)
                while not future.done():
                    if xbmc.abortRequested or dialog.iscanceled():
                        pool.shutdown(wait=False)
                        return
                    xbmc.sleep(100)
                result = future.result()

            if not result:
                raise AnErrorOccurred(30305)
            items = result.pop('items', [])
            if not items:
                raise AnErrorOccurred(30307)
            itemsCount = len(items)

            # Build status
            status = {
                'jobs': (itemsCount+1)*2,
                'done': 1
            }

            # Update progress
            dialog.update(int(status['done']*100/status['jobs']), line1=__addon__.getLocalizedString(30018))

            # Getting meta data and subtitles
            def on_status_update(future):
                data = future.result()
                status['done'] = status['done']+1
                if not data:
                    dialog.update(int(status['done']*100/status['jobs']))
                if data.get('stream_info', {}).get('subtitle', {}).get('language', None):
                    dialog.update(int(status['done']*100/status['jobs']), line1=data["label"], line2=u'{lang} subtitle'.format(lang=data['stream_info']['subtitle']['language']))
                else:
                    dialog.update(int(status['done']*100/status['jobs']), line1=data["label"], line2='Metadata')

            futures = []
            providers = {'metadata': call_provider(PROVIDERS['meta_tmdb']), 'subtitles': call_provider(PROVIDERS['subtitle_yify'])}
            refresh = _isSettingsChanged()
            with conFutures.ThreadPoolExecutor(max_workers=2) as pool:
                for item in items:
                    futures.append(pool.submit(_shelf_mediainfo, *('metadata', item, providers['metadata'], refresh,)))
                    futures.append(pool.submit(_shelf_mediainfo, *('subtitles', item, providers['subtitles'], refresh,)))
                [future.add_done_callback(on_status_update) for future in futures]
                while not all(future.done() for future in futures):
                    if xbmc.abortRequested or dialog.iscanceled():
                        pool.shutdown(wait=False)
                        return
                    xbmc.sleep(100)

            # Build item
            mediainfo = map(lambda i: i.result(), futures)
            for i in xrange(itemsCount):
                # Update item with mediainfo
                items[i].update(mediainfo[i*2]) # Metadata
                items[i].update(mediainfo[i*2+1]) # Subtitle

                # Set video width and hight
                width = 1920
                height = 1080
                if not items[i]['torrents'].get('1080p', None):
                    width = 1280
                    height = 720
                items[i].setdefault("stream_info", {}).setdefault("video", {}).update({"width": width, "height": height})
                
                # Create player url
                play_kwargs = {
                    'torrents': items[i].pop('torrents'),
                    'subtitle': items[i].pop('subtitle', None),
                    'item': items[i]
                }
                items[i]["path"] = plugin.url_for('play', **play_kwargs)

                # The item is now playable
                items[i]["is_playable"] = True

            # Add next page, but we stop at page 20... yes 20 pages sounds all right
            if page < int(result.get("pages", 1)) and page < 21:
                plugin.log.debug('(Main) page: '+str(page))
                items.append({
                    "label": '>> '+__addon__.getLocalizedString(30009),
                    "path": plugin.url_for('browse', **_build_kwargs(kwargs, {'provider':provider,'separate':separate,'page':page+1}))
                })

            # Update progress
            dialog.update(100, line1=__addon__.getLocalizedString(30017), line2=' ')

            return items

    except AnErrorOccurred as e:
        errorNotify(e.errno)
    except:
        errorNotify(30308)
    return

@plugin.route("/search")
def search():
    try:
        query = plugin.keyboard("", __addon__.getLocalizedString(30001))
        if query:
            plugin.redirect(plugin.url_for(item.pop('endpoint'), **_get_kwargs({'query': query, 'page': 1})[0]))
    except:
        errorNotify(30308)

@plugin.route("/search/<query>/<page>")
@ensure_fanart
def search_query(query, page):
    pass

@plugin.route("/play")
def play():
    try:
        kwargs = dict((k, v[0]) for k, v in plugin.request.args.items())

        play3d = False
        if kwargs['torrents'].get('3D') and int(__addon__.getSetting("play3d")) > 0:
            play3d = True
            if __addon__.getSetting("play3d") == '1':
                play3d = xbmcgui.Dialog().yesno(heading=__addon__.getLocalizedString(30010), line1=__addon__.getLocalizedString(30011))

        if play3d:
            url = from_meta_data(kwargs['torrents']['3D'], "quality 3D")
        elif kwargs['torrents'].get('1080p'):
            url = from_meta_data(kwargs['torrents']['1080p'], "quality 1080p")
        else:
            url = from_meta_data(kwargs['torrents']['720p'], "quality 720p")

        subtitle_provider = None
        if kwargs['subtitle']:
            subtitle_provider = call_provider(PROVIDERS['subtitle_yify'])

        Player().play(url, kwargs["item"], kwargs['subtitle'], subtitle_provider)

    except Error as e:
        torrentError(e)
    except AnErrorOccurred as e:
        errorNotify(e.errno)
    except:
        errorNotify(30308)

if __name__ == '__main__':
    try:
        Platform.system
    except AnErrorOccurred as e:
        errorNotify(e.errno)
        sys.exit(0)

    try:
        plugin.run()
    except Exception, e:
        log_traceback(4)
        sys.exit(0)
