#!/usr/bin/python
from kodipopcorntime.caching import shelf

_default_ttl = 365 * 24 * 3600 # 1 year

def update_list(identifier, proxies):
    with shelf("proxy."+identifier, _default_ttl) as p:
        if not p or not all(x in p['proxies'] for x in proxies):
            p.update({'proxies':proxies})
        return p['proxies']

def set_default(identifier, proxy):
    with shelf("proxy."+identifier, _default_ttl) as p:
        p['proxies'].remove(proxy)
        p['proxies'].insert(0, proxy)
