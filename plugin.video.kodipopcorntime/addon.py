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
            if not item.get("kodipopcorn_endpoint"):
                continue
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/browse/<provider>/<item>/<page>")
@ensure_fanart
@contextmanager
def browse(provider, item, page):
    try:


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
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/search/<query>/<page>")
@ensure_fanart
def search_query(query, page):
    return yify.search_query(query, page)
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/play")
def play():
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

