from os import path
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlsplit as urlparse
from kodipopcorntime.proxy import update_proxies, set_default_proxy
from kodipopcorntime.utils import url_get
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
            search_result = url_get("{proxy}/api/v2/list_movies.json".format(proxy=proxy), params=params, headers={"Referer": proxy})