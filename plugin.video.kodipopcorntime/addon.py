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
