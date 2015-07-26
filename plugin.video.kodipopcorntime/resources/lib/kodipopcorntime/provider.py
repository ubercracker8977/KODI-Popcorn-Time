#!/usr/bin/python
import os, pkgutil
from kodipopcorntime.path import RESOURCES_PATH

def list_providers():
    providers = {'movie':[],'meta':[],'subtitle':[]}
    for _, name, _ in pkgutil.iter_modules([os.path.join(RESOURCES_PATH, 'lib', 'kodipopcorntime', 'providers')]):
        s = name.split('_')
        if not len(s) == 2 or s[0] not in ['movie', 'meta', 'subtitle']:
            continue
        providers[s[0]].append(name)
        providers[name] = name
    return providers

PROVIDERS = list_providers()

def call_provider(provider):
    provider = "kodipopcorntime.providers." + provider
    mod = __import__(provider)
    components = provider.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
