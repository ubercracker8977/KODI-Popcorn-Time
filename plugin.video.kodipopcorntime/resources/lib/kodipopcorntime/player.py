#!/usr/bin/python
import os, sys, xbmc, xbmcgui, xbmcplugin
import xml.etree.ElementTree as ET
from urllib import quote
from contextlib import contextmanager, closing
from torrent2http import State, Engine, MediaType
from kodipopcorntime.path import RESOURCES_PATH, CACHE_DIR
from kodipopcorntime.utils import SafeDialogProgress
from kodipopcorntime.msg import AnErrorOccurred, log, notify
from kodipopcorntime.plugin import plugin

__addon__ = sys.modules['__main__'].__addon__

class OverlayText(object):
    _window = ''
    _label = ''
    _shown = False
    _background = ''

    def __init__(self):
        x, y, w, h = self._calculate_the_size()

        self._window = xbmcgui.Window(12005)
        self._label = xbmcgui.ControlLabel(x, y, w, h, '', alignment=0x00000002 | 0x00000004)
        self._background = xbmcgui.ControlImage(x, y, w, h, os.path.join(RESOURCES_PATH, "media", "black.png"))
        self._background.setColorDiffuse("0xD0000000")

    def open(self):
        if not self._shown:
            self._window.addControls([self._background, self._label])
            self._shown = True

    def close(self):
        if self._shown:
            self._shown = False
            self._window.removeControls([self._background, self._label])

    def isShowing(self):
        return self._shown

    def setText(self, text):
        if self._shown:
            self._label.setLabel(text)

    def _calculate_the_size(self):
        # get skin resolution
        tree = ET.parse(os.path.join(xbmc.translatePath("special://skin/"), "addon.xml"))
        res = tree.findall("./extension/res")[0]
        viewport_w = int(res.attrib["width"])
        viewport_h = int(res.attrib["height"])
        # Adjust size based on viewport, we are using 1080p coordinates
        w = int(int(1920.0 * 0.7) * viewport_w / 1920.0)
        h = int(150 * viewport_h / 1088.0)
        x = (viewport_w - w) / 2
        y = (viewport_h - h) / 2
        return x, y, w, h

class Player(xbmc.Player):
    item = {}
    progressSleepTime = 50
    progressed = 0
    overlay = None

    def onPlayBackResumed(self):
        self.overlay.close()

    def onPlayBackPaused(self):
        self.overlay.open()

    def onPlayBackStopped(self):
        self.overlay.close()

    def _get_status_lines(self, status=None):
        if status is not None and not status == '':
            if status.state in [State.FINISHED, State.SEEDING]:
                return [
                    __addon__.getLocalizedString(30022),
                    __addon__.getLocalizedString(30008).format(download_rate=status.download_rate,upload_rate=status.upload_rate),
                   ' '
                ]
            return [
                __addon__.getLocalizedString(30021),
                __addon__.getLocalizedString(30008).format(download_rate=status.download_rate,upload_rate=status.upload_rate),
                __addon__.getLocalizedString(30015).format(num_seeds=status.num_seeds, progress=status.progress)
            ]

        return [
            __addon__.getLocalizedString(30016),
            ' ',
            ' '
        ]

    def _calculate_free_space(self, download_path):
        import ctypes
        from kodipopcorntime.platform import Platform
        
        if Platform.system() == 'windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(download_path), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value 
        else:
            st = os.statvfs(download_path)
            return st.f_bavail * st.f_frsize

    def _calculate_progress(self, movieTime, status, filestatus):
        if not status == '' and not filestatus == '' and status.download_rate > 0:
            needSizeInProcent = 0.02
            if int(movieTime):
                time = (filestatus.size/(status.download_rate*0.7*1024))
                if time > movieTime:
                    needSizeInProcent = (time-movieTime)/movieTime
            self.progressed = self.progressed+(99/((filestatus.size*needSizeInProcent)/((status.download_rate*0.8*1024)/1000)))*self.progressSleepTime

    def play(self, uri, item, subtitle=None, subtitle_provider=None):
        #
        torrent2http_options = {
            "uri": str(uri),
            # Files
            "download_path": xbmc.validatePath(xbmc.translatePath(__addon__.getSetting("download_path"))) or CACHE_DIR,
            "keep_files": __addon__.getSetting("keep_files") == 'true' and True or False,
            "keep_complete": __addon__.getSetting("keep_complete") == 'true' and True or False,
            "keep_incomplete": __addon__.getSetting("keep_incomplete") == 'true' and True or False,
            # Network
            "download_kbps": int(__addon__.getSetting("download_kbps")) or 0,
            "upload_kbps":  int(__addon__.getSetting("upload_kbps")) or 0,
            "connections_limit": int(__addon__.getSetting("connections_limit")) or 200,
            "encryption": int(__addon__.getSetting("encryption")) or 1,
            # Port
            "listen_port": int(__addon__.getSetting("listen_port")) or 6881,
            "use_random_port": __addon__.getSetting("use_random_port") == 'true' and True or False,
            # Peers
            "torrent_connect_boost": int(__addon__.getSetting("torrent_connect_boost")) or 50,
            "connection_speed": int(__addon__.getSetting("connection_speed")) or 50,
            "peer_connect_timeout": int(__addon__.getSetting("peer_connect_timeout")) or 15,
            "min_reconnect_time": int(__addon__.getSetting("min_reconnect_time")) or 60,
            "max_failcount": int(__addon__.getSetting("max_failcount")) or 3,
            # Features
            "enable_tcp": __addon__.getSetting("enable_tcp") == 'true' and False or True,
            "enable_dht": __addon__.getSetting("enable_dht") == 'true' and False or True,
            "enable_lsd": __addon__.getSetting("enable_lsd") == 'true' and False or True,
            "enable_utp": __addon__.getSetting("enable_utp") == 'true' and False or True,
            "enable_scrape": __addon__.getSetting("enable_scrape") == 'true' and True or False,
            "enable_upnp": __addon__.getSetting("enable_upnp") == 'true' and False or True,
            "enable_natpmp": __addon__.getSetting("enable_natpmp") == 'true' and False or True,
            # Additional
            "trackers": not __addon__.getSetting("trackers") == "" and __addon__.getSetting['trackers'].split(',') or None,
            "dht_routers": not __addon__.getSetting("dht_routers") == "" and __addon__.getSetting['dht_routers'].split(',') or None,
            # Log / Debug
            "log_stats": __addon__.getSetting("debug") == 'true' and True or False,
            "debug_alerts": __addon__.getSetting("debug_alerts") == 'true' and True or False,
            # Bin
            "binaries_path": os.path.join(RESOURCES_PATH, 'bin')
        }
        # List item
        self.item = item

        ###
        if torrent2http_options['download_kbps'] <= 0:
            torrent2http_options['download_kbps'] = None

        if torrent2http_options['upload_kbps'] <= 0:
            torrent2http_options['upload_kbps'] = None
        elif torrent2http_options['upload_kbps'] < 15:
            notify(__addon__.getLocalizedString(30313))
            torrent2http_options['upload_kbps'] = 15
            __addon__.setSetting('upload_kbps', '15')
        downloadpath = os.path.dirname(xbmc.validatePath(xbmc.translatePath(__addon__.getSetting("download_path"))))
        free_space = self._calculate_free_space(downloadpath)

        log('(Player) Start the torrent2http file', xbmc.LOGDEBUG)
        with closing(Engine(**torrent2http_options)) as engine:
            # Start engine and instruct torrent2http to begin download first file
            engine.start(0)

            log('(Player) Pre-Loading the movie', xbmc.LOGDEBUG)
            ready = False
            with closing(SafeDialogProgress(delay_create=0)) as dialog:
                dialog.create(self.item['info']['title'])
                dialog.update(self.progressed, *self._get_status_lines())

                file_id = None
                while not xbmc.abortRequested and not dialog.iscanceled():
                    xbmc.sleep(self.progressSleepTime)

                    # Get status
                    status = engine.status()
                    # Check if there is loading error and raise exception 
                    engine.check_torrent_error(status)

                    # We need a file id
                    if file_id is None:
                        # Get torrent files list, filtered by video file type only
                        files = engine.list(media_types=[MediaType.VIDEO])
                        if files is None:
                            continue
                        # Torrent has no video files
                        if not files:
                            raise AnErrorOccurred(30316)
                        # Select first matching file                    
                        file_id = files[0].index
                        file_status = files[0]

                    # Get file status
                    file_status = engine.file_status(file_id)
                    if not file_status:
                        continue

                    if file_status.size > free_space:
                        notify (__addon__.getLocalizedString(30323) + downloadpath);
                        log('(Player) Not enough space on filesystem. ' + str(file_status.size / 1024 / 1024) + 'MB needed, ' + str(free_space / 1024 /1024) + ' MB available in ' + downloadpath, xbmc.LOGDEBUG)
                        break

                    if status.state == State.DOWNLOADING:
                        self._calculate_progress(int(self.item['info'].get('duration', 0)), status, file_status)
                        if self.progressed >= 100:
                            ready = True
                            break
                        dialog.update(int(self.progressed), *self._get_status_lines(status))
                        continue

                    if status.state in [State.FINISHED, State.SEEDING]:
                        ready = True
                        break

                if ready:
                    log('(Player) Finished with pre-loading the movie', xbmc.LOGDEBUG)
                    # Download subtitle
                    if subtitle:
                        log('(Player) Download subtitle', xbmc.LOGDEBUG)
                        dialog.update(99, *[__addon__.getLocalizedString(30019), ' ', ' '])
                        path = file_status.save_path
                        subtitle = subtitle_provider.download(subtitle, os.path.dirname(path), ".".join([os.path.splitext(os.path.basename(path))[0], self.item['stream_info']['subtitle']['language']]))
                    dialog.update(100, *[__addon__.getLocalizedString(30020), ' ', ' '])
                elif xbmc.abortRequested or dialog.iscanceled():
                    log('(Player) Pre-Loading was canceled or interrupted', xbmc.LOGDEBUG)

            if ready:
                # Resolve URL to XBMC
                self.item.update({"path": file_status.url})

                # Starts the playback
                log('(Player) Start the playback', xbmc.LOGDEBUG)
                #xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.item)
                plugin.set_resolved_url(self.item)
                for _ in xrange(60):
                    if not self.isPlaying():
                        xbmc.sleep(1000)
                        continue

                    if subtitle:
                        log('(Player) Adds the subtitle to the player', xbmc.LOGDEBUG)
                        self.setSubtitles(subtitle)

                    # Wait for the playback to finish
                    log('(Player) Wait for the playback to finish', xbmc.LOGDEBUG)
                    with closing(OverlayText()) as self.overlay:
                        while not xbmc.abortRequested and self.isPlaying():
                            if self.overlay.isShowing():
                                self.overlay.setText("\n".join(self._get_status_lines(engine.status())))
                            xbmc.sleep(100)

                    log('(Player) Playback is finished', xbmc.LOGDEBUG)
                    if subtitle and torrent2http_options["keep_files"] == False and torrent2http_options["keep_complete"] == False and torrent2http_options["keep_incomplete"] == False:
                        # Delete subtitle
                        log('(Player) Delete subtitle', xbmc.LOGDEBUG)
                        subtitle_provider.remove(subtitle)
                    break
                else:
                    log('(Player) Playback is terminated due to timeout', xbmc.LOGERROR)
