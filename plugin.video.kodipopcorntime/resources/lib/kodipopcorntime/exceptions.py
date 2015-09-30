#!/usr/bin/python
class Notify(Exception):
    """
        This class are use for no fatal error.
        Normally, this means that the user must take action or similar to continue. Eg. Change a setting
    """
    def __init__(self, message, messageID, level=0):
        # An English explanation which is used for logging
        self.message = message

        # Message identifier which can be translated into a local language message to the user
        self.messageID = messageID

        self.level = level

    def __str__(self):
        return self.message

class Error(Exception):
    def __init__(self, tracebackStr, messageID):
        # An English explanation for use in traceback
        self.tracebackstr = tracebackStr

        # Message identifier which can be translated into a local language message to the user
        self.messageID = messageID

    def __str__(self):
        return self.tracebackstr

class ProxyError(Error):
    pass

class HTTPError(Error):
    pass

class TorrentError(Error):
    def __init__(self, tracebackStr, messageID=None):
        # An English explanation for use in traceback
        self.tracebackstr = tracebackStr

        # Message identifier which can be translated into a local language message to the user
        self.messageID = messageID or 30313

class ClassError(Exception):
    pass

class Abort(Exception):
    pass
