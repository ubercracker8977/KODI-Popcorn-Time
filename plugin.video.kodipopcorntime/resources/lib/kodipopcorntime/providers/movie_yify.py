try:
    from urlparse import urlparse
except:
    from urllib.parse import urlsplit as urlparse
from kodipopcorntime.proxy import update_proxies, set_default_proxy
PROXY_IDENTIFIER = 'movie.yify'

def getURLS():
    # Default domain list
    urls = [
        "http://yts.to",
        "http://eqwww.image.yt"
    ]

    # Evaluate user domain
    userURL = urlparse(plugin.get_setting("base_yify"))
    if not userURL.scheme or not userURL.netloc:
        return urls

    fUserURL = "{url.scheme}://{url.netloc}".format(url=userURL)
    # Prioritize user domain
    if fUserURL in urls:
        urls.remove(fUserURL)
    urls.insert(0, fUserURL)

    return urls
