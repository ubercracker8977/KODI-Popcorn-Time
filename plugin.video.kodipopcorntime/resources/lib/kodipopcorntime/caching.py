#!/usr/bin/python
import os, threading, shelve, time
from kodipopcorntime.path import CACHE_DIR
from contextlib import contextmanager, closing

_locks = {}

@contextmanager
def shelf(filename, ttl=300):
    if ttl > 0:
        path = os.path.join(CACHE_DIR, filename)
        with _locks.get(path, threading.RLock()):
            with closing(shelve.open(path, writeback=True)) as d:
                if not d or (time.time() - d["created_at"]) > ttl:
                    d.update({
                        "created_at": time.time(),
                        "data": {}
                    })
                yield d["data"]
    else:
        yield {}

def route(filename, ttl=300):
    if ttl > 0:
        path = os.path.join(CACHE_DIR, filename)
        with _locks.get(path, threading.RLock()):
            with closing(shelve.open(path, writeback=True)) as d:
                if not d:
                    d.update({
                        "created_at": time.time(),
                        "data": [],
                    })
                elif (time.time() - d["created_at"]) > ttl:
                    d["data"] = []
                yield d["data"]
    else:
        yield []
