import sys, os, xbmc, traceback
from contextlib import contextmanager, closing
from importlib import import_module
from concurrent import futures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
from kodipopcorntime.common import plugin, PLATFORM, RESOURCES_PATH, AnErrorOccurred
from kodipopcorntime.utils import ensure_fanart, SafeDialogProgress
from kodipopcorntime.providers import PROVIDERS
from kodipopcorntime.magnet import from_meta_data
from kodipopcorntime.player import TorrentPlayer


if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        map(xbmc.log, traceback.format_exc().split("\n"))
        sys.exit(0)

if not PLATFORM.get('os'):
    plugin.notify(plugin.addon.getLocalizedString(30302), delay=15000)
    plugin.log.error(plugin.addon.getLocalizedString(30302))
    sys.exit(0)

LIMIT = 20
QUALITY = 'all'

@plugin.route("/")
@ensure_fanart
def index():
    try:
        items = []

        if len(PROVIDERS['movies']) == 1:
            sys_kwargs = { 
                'module': import_module(provider),
                'provider': PROVIDERS['movies'][0]
            }
            for item in sys_kwargs['module'].list():
                if not item.get("kodipopcorn_endpoint"):
                    continue
                kwargs = {}
                if item.get("kodipopcorn_kwargs"):
                    kwargs = item.pop('kodipopcorn_kwargs')
                item["path"] = plugin.url_for(item.pop('kodipopcorn_endpoint'), **kwargs.update(sys_kwargs))
                items.append(item)

        elif len(PROVIDERS['movies']) > 0:
            for provider in PROVIDERS:
                module = import_module(provider)
                item["path"] = plugin.url_for('list', provider=provider, module=module)
                items.append(module.INDEX)

        plugin.finish(items, update_listing=False)
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/list")
@ensure_fanart
@contextmanager
def list():
    try:
        kwargs, sys_kwargs = _filter_kwargs()
        for item in sys_kwargs['module'].list(**kwargs):
            if not item.get("kodipopcorn_endpoint"):
                continue
            kwargs = {}
            if item.get("kodipopcorn_kwargs"):
                kwargs = item.pop('kodipopcorn_kwargs')
            item["path"] = plugin.url_for(item.pop('kodipopcorn_endpoint'), **kwargs.update(sys_kwargs))
            yield item
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/browse/<provider>/<item>/<page>")
@ensure_fanart
@contextmanager
def browse(provider, item, page):
    try:
        kwargs, sys_kwargs = _filter_kwargs()
        content = 'movies'
        items = []
        with closing(SafeDialogProgress(delay_close=0)) as dialog:
            dialog.create(plugin.name)
            dialog.update(percent=0, line1=plugin.addon.getLocalizedString(30007))

            movies = sys_kwargs['module'].browse(item, page, **kwargs)

            jobs = len(movies)*2+1
            done = 1
            dialog.update(percent=int(done*100/jobs), line2=plugin.addon.getLocalizedString(30007))

            def on_future_done(future):
                done = done+1
                data = future.result()
                dialog.update(percent=int(done*100/jobs), line2="{prefix}{label}".format(prefix=data.get('kodipopcorn_subtitle', ''), label=data.get("label", '')))

            subtitle = import_module(PROVIDERS['subtitle.yify'])
            meta = import_module(PROVIDERS['meta.tmdb'])
            with futures.ThreadPoolExecutor(max_workers=2) as pool:
                subtitle_list = [pool.submit(subtitle.get, id=item.get("info", {}).get("code")).add_done_callback(on_future_done) for item in movies]
                meta_list = [pool.submit(meta.get, id=item.get("info", {}).get("code")).add_done_callback(on_future_done) for item in movies]
                while not all(future.done() for future in subtitle_list) and not all(future.done() for future in meta_list):
                    if dialog.iscanceled():
                        return
                    xbmc.sleep(100)

            subtitles = map(lambda future: future.result(), subtitle_list)
            metadata = map(lambda future: future.result(), meta_list)
            for i, movie in enumerate(movies):
                # Update the movie with subtitle and meta data
                movie.update(subtitles[i])
                movie.update(metadata[i])

                # Catcher content type and remove it from movie
                # NOTE: This is not the best way to dynamic set the content type, since the content type can not be set for each movie
                if movie.get("kodipopcorn_content"):
                    content = movie.pop('kodipopcorn_content')

                # Catcher quality, build magnet label and remove quality from movie
                quality=fQuality=''
                if movie.get("kodipopcorn_quality"):
                    quality = movie.pop('kodipopcorn_quality')
                    fQuality = " [{quality}]".format(quality=quality)

                # Build magnet label
                fYear = ''
                if movie.get("year"):
                    fYear = " ({year})".format(year=movie["year"])

                # Builds targets for the player
                kwargs = {}
                if movie.get("kodipopcorn_subtitle"):
                    kwargs['subtitle'] = movie.pop('kodipopcorn_subtitle')
                kwargs.update({
                    'url': from_meta_data(movie.pop('kodipopcorn_hash'), movie["label"]+fYear+fQuality),
                    'info': movie
                })

                # Update the final information for the movie
                if quality and not quality == '720p':
                    movie["label"] = "{label} ({quality})".format(label=movie["label"], quality=quality)
                movie["path"] = plugin.url_for('play', **kwargs)

                items.append(movie)
        if items:
            plugin.set_content(content)
            return items
        raise AnErrorOccurred(30307)
    except AnErrorOccurred as e:
        plugin.notify("{default} {strerror}".format(default=plugin.addon.getLocalizedString(30306), strerror=plugin.addon.getLocalizedString(e.errno)), delay=15000)
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/search")
def search():
    try:
        query = plugin.keyboard("", plugin.addon.getLocalizedString(30001))
        if query:
            kwargs, sys_kwargs = _filter_kwargs({
                'query': query,
                'page': 1
            })
            plugin.redirect(plugin.url_for("search_query", **kwargs.update(sys_kwargs)))
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/search/<query>/<page>")
@ensure_fanart
def search_query(query, page):
    try:
        kwargs, sys_kwargs = _filter_kwargs()
        return sys_kwargs['module'].search_query(query, page, **kwargs.update(sys_kwargs))
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/play")
def play():
    try:
        TorrentPlayer().init(**dict((k, v[0]) for k, v in plugin.request.args.items())).loop()
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

def _filter_kwargs(**kwargs):
    kwargs = dict((k, v[0]) for k, v in plugin.request.args.items()).update(kwargs)

    sys_kwargs['module'] = kwargs.pop('module')
    if kwargs.get('provider'):
        sys_kwargs['provider'] = kwargs.pop('provider')
    sys_kwargs.update({
        'limit': LIMIT,
        'quality': QUALITY
    })
    return [kwargs or {}, sys_kwargs]
