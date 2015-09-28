#!/usr/bin/python
import sys, threading, time

class Thread(threading.Thread):
    def __init__(self, target=None):
        self._target   = target or self.run
        self._exc_info = []

        super(Thread, self).__init__(target=self.___run)
        self.daemon = False
        self.stop = threading.Event()
        self.start()

    def __enter__(self):
        return self

    def ___run(self):
        try:
            self._target()
        except:
            self._exc_info = sys.exc_info()
            self.close()

    def checkError(self):
        return len(self._exc_info) > 0

    def raiseAnyError(self):
        if self._exc_info: 
            raise self._exc_info[0], self._exc_info[1], self._exc_info[2]

    def __exit__(self, *exc_info):
        self.close()
        return not exc_info[0]

    def __del__(self):
        if hasattr(self, 'stop'):
            self.close()

    def close(self):
        if not self.stop.is_set():
            self.stop.set()

class FLock:
    _locks = {}
    def __init__(self, file):
        if not FLock._locks.get(file):
            FLock._locks[file] = False
        while FLock._locks[file]:
            time.sleep(0.100)
        if FLock._locks[file]:
            raise RuntimeError("cannot acquired lock")
        FLock._locks[file] = True

    def unLock(self, file):
        if not FLock._locks[file]:
            raise RuntimeError("cannot release un-acquired lock")
        FLock._locks[file] = False
