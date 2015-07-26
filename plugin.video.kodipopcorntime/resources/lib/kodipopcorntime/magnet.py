#!/usr/bin/python
from urlparse import parse_qs
from urllib import urlencode

_public_trackers = [
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
    "http://exodus.desync.com:6969/announce",
]

def from_meta_data(torrent_hash, dn):
    return "magnet:?xt=urn:btih:%s&%s" % (torrent_hash, urlencode({'dn' : dn, 'tr': _public_trackers}, doseq=True))
