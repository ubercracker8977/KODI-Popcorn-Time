#!/usr/bin/python
import xbmc, sys, os, socket, time, stat
from urlparse import urlparse
from kodipopcorntime.platform import Platform
from kodipopcorntime.exceptions import Error, ClassError, Notify
from kodipopcorntime.logging import log

__addon__ = sys.modules['__main__'].__addon__

SUBTITLE_ISO = [
    "sq",
    "ar",
    "bn",
    "pt-br",
    "bg",
    "zh",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "fa",
    "fi",
    "fr",
    "de",
    "el",
    "he",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "lt",
    "mk",
    "ms",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "sr",
    "sl",
    "es",
    "sv",
    "th",
    "tr",
    "ur",
    "vi"
]

ISOTRANSLATEINDEX = {
    "sq":    30201,
    "ar":    30202,
    "bn":    30203,
    "pt-br": 30204,
    "bg":    30205,
    "zh":    30206,
    "hr":    30207,
    "cs":    30208,
    "da":    30209,
    "nl":    30210,
    "en":    30211,
    "fa":    30212,
    "fi":    30213,
    "fr":    30214,
    "de":    30215,
    "el":    30216,
    "he":    30217,
    "hu":    30218,
    "id":    30219,
    "it":    30220,
    "ja":    30221,
    "ko":    30222,
    "lt":    30223,
    "mk":    30224,
    "ms":    30225,
    "no":    30226,
    "pl":    30227,
    "pt":    30228,
    "ro":    30229,
    "ru":    30230,
    "sr":    30231,
    "sl":    30232,
    "es":    30233,
    "sv":    30234,
    "th":    30235,
    "tr":    30236,
    "ur":    30237,
    "vi":    30238
}

PUBLIC_TRACKERS = [
    "udp://tracker.publicbt.com:80/announce",
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://tracker.istole.it:6969",
    "udp://tracker.coppersurfer.tk:80",
    "udp://open.demonii.com:1337",
    "udp://tracker.istole.it:80",
    "http://tracker.yify-torrents.com/announce",
    "udp://tracker.publicbt.com:80",
    "udp://tracker.openbittorrent.com:80",
    "udp://tracker.coppersurfer.tk:6969",
    "udp://exodus.desync.com:6969",
    "http://exodus.desync.com:6969/announce"
]

class _MetaClass(type):
    def __getattr__(cls, name):
        # Do we have a setting method
        if not hasattr(cls, '_%s' %name):
            raise AttributeError("type object '%s' has no attribute '%s'" %(cls.__name__, name))

        # Create setting
        getattr(cls, '_%s' %name)()

        # Return setting
        value = getattr(cls, name)
        log("(Settings) %s.%s is '%s'" %(cls.__name__, name, str(value)))
        return value

class _Base(object):
    def __new__(self, *args, **kw):
        raise ClassError("%s is a static class and cannot be initiated" % self.__name__)

class addon(_Base):
    class __metaclass__(_MetaClass):
        def _base_url(cls):
            cls.base_url = sys.argv[0]

        def _handle(cls):
            cls.handle = int(sys.argv[1])

        def _cur_uri(cls):
            cls.cur_uri = sys.argv[2][1:]

        def _language(cls):
            cls.language = xbmc.getLanguage(xbmc.ISO_639_1)

        def _cache_path(cls):
            _path = xbmc.translatePath("special://profile/addon_data/%s/cache" % cls.id)
            if not os.path.exists(_path):
                os.makedirs(_path)
                if not os.path.exists(_path):
                    raise Error("Unable to create cache directory %s" % _path, 30322)
            cls.cache_path = _path.encode(cls.fsencoding)

        def _resources_path(cls):
            cls.resources_path = os.path.join(__addon__.getAddonInfo('path'), 'resources')

        def _translate_term(cls):
            if __addon__.getSetting("search_translate") == 'true':
                cls.translate_term = True
            else:
                cls.translate_term = False

        def _debug(cls):
            if __addon__.getSetting("debug") == 'true':
                cls.debug = True
            else:
                cls.debug = False

        def _id(cls):
            cls.id = __addon__.getAddonInfo('id')

        def _name(cls):
            cls.name = __addon__.getAddonInfo('name')

        def _version(cls):
            cls.version = __addon__.getAddonInfo('version')

        def _fanart(cls):
            cls.fanart = __addon__.getAddonInfo('fanart')

        def _info_image(cls):
            cls.info_image = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'media', 'info.png')

        def _warning_image(cls):
            cls.warning_image = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'media', 'warning.png')

        def _error_image(cls):
            cls.error_image = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'media', 'error.png')

        def _limit(cls):
            cls.limit = 20

        def _fsencoding(cls):
            cls.fsencoding = sys.getfilesystemencoding() or 'utf-8'


class _MetaClass2(_MetaClass):
    def _mediaType(cls):
        cls.mediaType = cls.__name__

    def _lastchanged(cls):
        cls.lastchanged = cls.subtitle_lastchanged > cls.metadata_lastchanged and cls.subtitle_lastchanged or cls.metadata_lastchanged

    def _subtitle_lastchanged(cls):
        _name =  cls.__name__
        _time = str(time.time())

        _tmp = str(cls.preferred_subtitles)
        if not _tmp == __addon__.getSetting('%s_preferred_subtitles' %_name):
            __addon__.setSetting("%s_preferred_subtitles" %_name, _tmp)
            __addon__.setSetting("%s_subtitle_lastchanged" %_name, _time)

        _tmp = str(cls.prioritere_impaired)
        if not _tmp == __addon__.getSetting('%s_hearing_impaired_old' %_name):
            __addon__.setSetting("%s_hearing_impaired_old" %_name, _tmp)
            __addon__.setSetting("%s_subtitle_lastchanged" %_name, _time)

        _tmp = str(cls.subtitles_provider)
        if not _tmp == __addon__.getSetting('%s_subtitle_provider_old' %_name):
            __addon__.setSetting("%s_subtitle_provider_old" %_name, _tmp)
            __addon__.setSetting("%s_subtitle_lastchanged" %_name, _time)

        cls.subtitle_lastchanged = float(__addon__.getSetting("%s_subtitle_lastchanged" %_name) or 0.0)

    def _metadata_lastchanged(cls):
        _name =  cls.__name__
        _time = str(time.time())

        _tmp = str(cls.metadata_provider)
        if not _tmp == __addon__.getSetting('%s_metadata_provider_old' %_name):
            __addon__.setSetting("%s_metadata_provider_old" %_name, _tmp)
            __addon__.setSetting("%s_metadata_lastchanged" %_name, _time)

        if not addon.language == __addon__.getSetting('%s_syslang_old' %_name):
            __addon__.setSetting("%s_syslang_old" %_name, addon.language)
            __addon__.setSetting("%s_metadata_lastchanged" %_name, _time)

        cls.metadata_lastchanged = float(__addon__.getSetting("%s_metadata_lastchanged" %_name) or 0.0)

    def _preferred_subtitles(cls):
        if cls.subtitles_provider:
            cls.preferred_subtitles = [SUBTITLE_ISO[int(__addon__.getSetting('%s_subtitle_language1' %cls.__name__))-1]]
            if not __addon__.getSetting('%s_subtitle_language2' %cls.__name__) == '0':
                cls.preferred_subtitles.append(SUBTITLE_ISO[int(__addon__.getSetting('%s_subtitle_language2' %cls.__name__))-1])
                if not __addon__.getSetting('%s_subtitle_language3' %cls.__name__) == '0':
                    cls.preferred_subtitles.append(SUBTITLE_ISO[int(__addon__.getSetting('%s_subtitle_language3' %cls.__name__))-1])
        else:
            cls.preferred_subtitles = []

    def _prioritere_impaired(cls):
        if not __addon__.getSetting('%s_subtitle_language1' %cls.__name__) == '0' and __addon__.getSetting("hearing_impaired") == 'true':
            cls.prioritere_impaired = True
        else:
            cls.prioritere_impaired = False

    def _proxies(cls):
        p = []
        domains = __addon__.getSetting("%s_proxies" %cls.__name__).split(',')
        # Evaluate user domains
        for domain in reversed(domains):
            if not domain[:4] == 'http' and not domain[:2] == '//':
                domain = "http://"+domain
            d = urlparse(domain)
            if d.netloc:
                p.append(u"%s://%s/%s" %(d.scheme, d.netloc, d.path))
        cls.proxies = p

    def _qualities(cls):
        _quality = __addon__.getSetting("%s_quality" %cls.__name__)
        if _quality == '0':
            _qualities = ['720p']
        else:
            _qualities = ['720p','1080p']
        if not cls.play3d == 0:
            _qualities.append('3D')
        cls.qualities = _qualities

    def _play3d(cls):
        if not __addon__.getSetting("%s_quality" %cls.__name__) == '0':
            cls.play3d = int(__addon__.getSetting("%s_play3d"  %cls.__name__))
        else:
            cls.play3d = 0

    def _download_path(cls):
        _path = xbmc.translatePath(__addon__.getSetting("%s_download_path"  %cls.__name__))

        if _path:
            if _path.lower().startswith("smb://"):
                if not platform.system == "windows":
                    raise Notify("Downloading to an unmounted network share is not supported (%s)" % _path, 30319, 0)
                _path.replace("smb:", "").replace("/", "\\")

            if not os.path.isdir(_path):
                raise Notify('Download path does not exist (%s)' % _path, 30310, 1)

            cls.download_path = _path.encode(addon.fsencoding)
        else:
            cls.download_path = addon.cache_path

    def _delete_files(cls):
        if cls.keep_files or cls.keep_complete or cls.keep_incomplete:
            cls.delete_files = False
        else:
            cls.delete_files = True

    def _keep_files(cls):
        if __addon__.getSetting("%s_keep_files" %cls.__name__) == 'true' and not cls.keep_complete and not cls.keep_incomplete:
            cls.keep_files = True
        else:
            cls.keep_files = False

    def _keep_complete(cls):
        if not __addon__.getSetting("%s_keep_incomplete" %cls.__name__) == 'false' and __addon__.getSetting("%s_keep_complete" %cls.__name__) == 'true':
            cls.keep_complete = True
        else:
            cls.keep_complete = False

    def _keep_incomplete(cls):
        if __addon__.getSetting("%s_keep_incomplete" %cls.__name__) == 'true' and __addon__.getSetting("%s_keep_complete" %cls.__name__) == 'false':
            cls.keep_incomplete = True
        else:
            cls.keep_incomplete = False

    def _torrent_options(cls):
        binary = "torrent2http"
        if Platform.system == 'windows':
            binary = "torrent2http.exe"
        binary_path = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'bin', "%s_%s" %(Platform.system, Platform.arch), binary).encode(addon.fsencoding)

        if not os.path.isfile(binary_path):
            raise Error("torrent2http binary (%s) was not found at path %s" % (os.path.dirname(binary_path), binary), 30320)

        if Platform.system == "android":
            log("Trying to copy torrent2http to ext4, since the sdcard is noexec", LOGLEVEL.INFO)
            android_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(xbmc.translatePath('special://xbmc')))), "files", __addon__.getAddonInfo('id'), binary).encode(addon.fsencoding)
            if not os.path.exists(os.path.dirname(android_path)):
                os.makedirs(os.path.dirname(android_path))
            if not os.path.exists(android_path) or int(os.path.getmtime(android_path)) < int(os.path.getmtime(binary_path)):
                shutil.copy2(binary_path, android_path)
            binary_path = android_path

        if not os.path.isfile(binary_path):
            raise Error("torrent2http binary was not found at path %s" % os.path.dirname(binary_path), 30320)

        st = os.stat(binary_path)
        os.chmod(binary_path, st.st_mode | stat.S_IEXEC)
        if not st.st_mode & stat.S_IEXEC:
            raise Error("Cannot make %s executable, ensure partition is in exec mode\n%s" % (binary, os.path.dirname(binary_path)), 30321)

        download_kbps = int(__addon__.getSetting("download_kbps"))
        if download_kbps <= 0:
            download_kbps = -1

        upload_kbps = int(__addon__.getSetting("upload_kbps"))
        if upload_kbps <= 0:
            upload_kbps = -1
        elif upload_kbps < 15:
            raise Notify('Max Upload Rate must be above 15 Kilobytes per second.', 30324, 1)
            __addon__.setSetting('upload_kbps', '15')
            upload_kbps = 15

        trackers = __addon__.getSetting('trackers')
        if trackers:
            trackers = ",".join(trackers.split(',')+PUBLIC_TRACKERS)
        else:
            trackers = ",".join(PUBLIC_TRACKERS)

        debug = __addon__.getSetting("debug")
        
        kwargs = {
            '--file-index':             0,
            '--dl-path':                cls.download_path,
            '--connections-limit':      int(__addon__.getSetting('connections_limit')),
            '--dl-rate':                download_kbps,
            '--ul-rate':                upload_kbps,
            '--enable-dht':             __addon__.getSetting('enable_dht'),
            '--enable-lsd':             __addon__.getSetting('enable_lsd'),
            '--enable-natpmp':          __addon__.getSetting('enable_natpmp'),
            '--enable-upnp':            __addon__.getSetting('enable_upnp'),
            '--enable-scrape':          __addon__.getSetting('enable_scrape'),
            '--encryption':             int(__addon__.getSetting('encryption')),
            '--show-stats':             debug,
            '--files-progress':         debug,
            '--overall-progress':       debug,
            '--pieces-progress':        debug,
            '--listen-port':            int(__addon__.getSetting('listen_port')),
            '--random-port':            __addon__.getSetting('use_random_port'),
            '--keep-complete':          str(cls.keep_complete).lower(),
            '--keep-incomplete':        str(cls.keep_incomplete).lower(),
            '--keep-files':             str(cls.keep_files).lower(),
            '--max-idle':               300,
            '--no-sparse':              'false',
            #'--resume-file':            None,
            '--user-agent':             'torrent2http/1.0.1 libtorrent/1.0.3.0 kodipopcorntime/%s' %addon.version,
            #'--state-file':             None,
            '--enable-utp':             __addon__.getSetting('enable_utp'),
            '--enable-tcp':             __addon__.getSetting('enable_tcp'),
            '--debug-alerts':           debug,
            '--torrent-connect-boost':  int(__addon__.getSetting('torrent_connect_boost')),
            '--connection-speed':       int(__addon__.getSetting('connection_speed')),
            '--peer-connect-timeout':   int(__addon__.getSetting('peer_connect_timeout')),
            '--request-timeout':        20,
            '--min-reconnect-time':     int(__addon__.getSetting('min_reconnect_time')),
            '--max-failcount':          int(__addon__.getSetting('max_failcount')),
            '--dht-routers':            __addon__.getSetting('dht_routers') or None,
            '--trackers':               trackers
        }

        args = [binary_path]
        for k, v in kwargs.iteritems():
            if v == 'true':
                args.append(k)
            elif v == 'false':
                args.append("%s=false" % k)
            elif v is not None:
                args.append(k)
                if isinstance(v, str):
                    args.append(v.decode('utf-8').encode(addon.fsencoding))
                else:
                    args.append(str(v))

        cls.torrent_options = args

class _Base2(_Base):
    @classmethod
    def get_torrent_options(self, magnet, port):
        args = ['--uri', magnet, '--bind', '127.0.0.1:%s' %port]
        for i in xrange(4):
            if isinstance(args[i], str):
                args[i] = args[i].decode('utf-8')
            args[i] = args[i].encode(addon.fsencoding)
        return self.torrent_options+args

class movies(_Base2):
    class __metaclass__(_MetaClass2):
        def _provider(cls):
            cls.provider = load_provider('movies_yify')

        def _metadata_provider(cls):
            provider = __addon__.getSetting('movies_metadata_provider')
            if not provider == '0':
                _list = ['metadata_tmdb']
                cls.metadata_provider = load_provider('movies.%s' % _list[int(provider)-1])
            else:
                cls.metadata_provider = None

        def _subtitles_provider(cls):
            provider = __addon__.getSetting('movies_subtitle_provider')
            if not provider == '0' and not __addon__.getSetting('movies_subtitle_language1') == '0':
                _list = ['subtitle_yify']
                cls.subtitles_provider = load_provider('movies.%s' % _list[int(provider)-1])
            else:
                cls.subtitles_provider = None

class tvshows(_Base2):
    class __metaclass__(_MetaClass2):
        def _provider(cls):
            """cls.provider = cls.load_provider('tvshows_xxxx')"""
            cls.provider = None

        def _metadata_provider(cls):
            provider = __addon__.getSetting('tvshows_metadata_provider')
            if not provider == '0':
                _list = []
                cls.metadata_provider = cls.load_provider('tvshows.%s' % _list[int(provider)-1])
            else:
                cls.metadata_provider = None

        def _subtitles_provider(cls):
            provider = __addon__.getSetting('tvshows_subtitle_provider')
            if not provider == '0' and not __addon__.getSetting('tvshows_subtitle_language1') == '0':
                _list = []
                cls.subtitles_provider = cls.load_provider('tvshows.%s' % _list[int(provider)-1])
            else:
                cls.subtitles_provider = None

def load_provider(module):
    provider = "kodipopcorntime.providers.%s" % module
    mod = __import__(provider)
    for comp in provider.split('.')[1:]:
        mod = getattr(mod, comp)
    return mod
