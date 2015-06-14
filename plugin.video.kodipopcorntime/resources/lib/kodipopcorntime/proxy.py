from kodipopcorntime.caching import shelf

def update_proxies(identifier, proxieslist):
    with shelf("proxy.%s" %identifier, 31536000) as proxies:
        if not proxies or not all(x in proxies for x in proxieslist):
            proxies.update(proxieslist)
        return proxies

def set_default_proxy(identifier, default):
    with shelf("proxy.%s" %identifier, 31536000) as proxies:
        if default and default in proxies:
            proxies.remove(default)
            proxies.insert(0, default)
        return
