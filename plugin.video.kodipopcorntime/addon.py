import sys, os
import sys, os, xbmc, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
from kodipopcorntime.common import plugin, PLATFORM, RESOURCES_PATH, AnErrorOccurred
from kodipopcorntime.utils import ensure_fanart, SafeDialogProgress
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

from kodipopcorntime.providers import yify

# Cache TTLs
DEFAULT_TTL = 24 * 3600 # 24 hours
LIMIT = 20
QUALITY = 'all'

@plugin.route("/")
@ensure_fanart
def index():
    for provider in providers['movie']:
        yield {
            "label": provider['label'],
            "icon": path.join(RESOURCES_PATH, 'media', provider['icon']),
            "thumbnail": path.join(RESOURCES_PATH, 'media', provider['thumbnail']),
            "path": plugin.url_for(provider['path'])
        }
    return yify.list()

@plugin.route("/list/<provider>/<item>/<page>")
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)
@ensure_fanart
def list():
    return yify.list(item, page)
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/browse/<provider>/<item>/<page>")
#contents = ['files', 'songs', 'artists', 'albums', 'movies', 'tvshows', 'episodes', 'musicvideos']
@ensure_fanart
def browse(item, page):
    return yify.browse(item, page)
    try:

@plugin.route("/search/<provider>")
def search(provider):
    query = plugin.keyboard("", plugin.addon.getLocalizedString(30001))
    if query:
        Plugin.redirect(Plugin.url_for("search_query", provider=provider, query=query, page=1))

@plugin.route("/search/<provider>/<query>/<page>")
        raise AnErrorOccurred(30307)
    except AnErrorOccurred as e:
        plugin.notify("{default} {strerror}".format(default=plugin.addon.getLocalizedString(30306), strerror=plugin.addon.getLocalizedString(e.errno)), delay=15000)
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)
@ensure_fanart
def search_query(query, page):
    return yify.search_query(query, page)
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)
    try:
    except:
        plugin.notify("{default}".format(default=plugin.addon.getLocalizedString(30306)), delay=15000)

@plugin.route("/play/<uri>")
def play(uri):
    TorrentPlayer().init(uri, sub).loop()
