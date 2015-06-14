import xbmc, os, threading
from kodipopcorntime.common import plugin, PLATFORM, CACHE_DIR
from contextlib import contextmanager, closing

LOCKS = {}

def shelf(filename, ttl=0):
    if ttl <= 0:
        return {}
    import shelve
    filename = os.path.join(CACHE_DIR, filename)
    with LOCKS.get(filename, threading.RLock()):
        with closing(shelve.open(filename, writeback=True)) as d:
            import time
            if not d:
                d.update({
                    "created_at": time.time(),
                    "data": {},
                })
            elif (time.time() - d["created_at"]) > ttl:
                d["data"] = {}
            return d["data"]
