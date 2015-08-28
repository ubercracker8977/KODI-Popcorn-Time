#!/usr/bin/python
import os, sys
from urlparse import urlparse
from kodipopcorntime.path import RESOURCES_PATH
from kodipopcorntime.utils import url_get
from kodipopcorntime.msg import log

__addon__ = sys.modules['__main__'].__addon__
provides = 'movies'

_genres = {
    '30400': 'Action',
    '30401': 'Adventure',
    '30402': 'Animation',
    '30403': 'Biography',
    '30404': 'Comedy',
    '30405': 'Crime',
    '30406': 'Documentary',
    '30407': 'Drama',
    '30408': 'Family',
    '30409': 'Fantasy',
    '30410': 'Film-Noir',
    '30411': 'History',
    '30412': 'Horror',
    '30413': 'Music',
    '30414': 'Musical',
    '30415': 'Mystery',
    '30416': 'Romance',
    '30417': 'Sci-Fi',
    '30418': 'Sport',
    '30419': 'Thriller',
    '30420': 'War',
    '30421': 'Western'
}
_proxy_identifier = 'movie.yify'

def catalogs(**kwargs):
    if kwargs.get('separate') == 'genres':
        items= []
        for n in __addon__.getLocalizedString(30499).split(','):
            if _genres.get(n, None):
                path = os.path.join(RESOURCES_PATH, 'media', 'genres', '{name}.png'.format(name=_genres[n]))
                items.append({
                    "label": __addon__.getLocalizedString(int(n)),
                    "endpoint": "browse",
                    "icon": path,
                    "thumbnail": path,
                    "kwargs": {
                        'separate': "genre",
                        'genre': _genres[n],
                        'page': 1
                    }
                })
        return items

    if kwargs.get('separate') == 'index':
        return [
            {
                "label": __addon__.getLocalizedString(30002),
                "icon": os.path.join(RESOURCES_PATH, 'media', 'search.png'),
                "thumbnail": os.path.join(RESOURCES_PATH, 'media', 'search.png'),
                "endpoint": "search"
            },
            {
                "label": __addon__.getLocalizedString(30004),
                "icon": os.path.join(RESOURCES_PATH, 'media', 'popular.png'),
                "thumbnail": os.path.join(RESOURCES_PATH, 'media', 'popular.png'),
                "endpoint": "browse",
                "kwargs": {
                    'separate': "seeds",
                    'page': 1
                }
            },
            {
                "label": __addon__.getLocalizedString(30006),
                "icon": os.path.join(RESOURCES_PATH, 'media', 'recently.png'),
                "thumbnail": os.path.join(RESOURCES_PATH, 'media', 'recently.png'),
                "endpoint": "browse",
                "kwargs": {
                    'separate': "date_added",
                    'page': 1
                }
            },
            {
                "label": __addon__.getLocalizedString(30005),
                "icon": os.path.join(RESOURCES_PATH, 'media', 'rated.png'),
                "thumbnail": os.path.join(RESOURCES_PATH, 'media', 'rated.png'),
                "endpoint": "browse",
                "kwargs": {
                    'separate': "rating",
                    'page': 1
                }
            },
            {
                "label": __addon__.getLocalizedString(30003),
                "icon": os.path.join(RESOURCES_PATH, 'media', 'genres.png'),
                "thumbnail": os.path.join(RESOURCES_PATH, 'media', 'genres.png'),
                "endpoint": "catalogs",
                "kwargs": {
                    'separate': "genres"
                }
            }
        ]

    return {
        "label": '',
        "icon": '',
        "thumbnail": '',
        "properties": {
            "fanart_image": ''
        },
        "endpoint": 'catalogs',
        "kwargs": {
            'separate': "index"
        }
    }

def browse(separate, page, **kwargs):
    params = {
        'limit': kwargs['limit'],
        'page': page,
        'quality': 'all',
        'genre': separate == "genre" and kwargs['genre'] or 'all',
        'sort_by': separate == "genre" and "seeds" or separate,
        'order_by': 'desc',
    }
    data = url_get(_getDomains(), "/api/v2/list_movies.json", params=params, proxyid=_proxy_identifier)
    if not data:
        return {}
    movies = data.get("data", {}).get("movies")
    if not movies:
        return {}

    items = []
    for movie in movies:
        if not movie.get("title") or not movie.get("imdb_code"):
            continue
        item = _create_item(movie, kwargs['qualities'])
        if not item:
            continue
        items.append(item)

    _tmp = int(data["data"].get("movie_count", 20))/int(kwargs['limit'])
    pages = int(_tmp)
    if _tmp > pages:
        pages = pages+1

    return {
        'pages': pages,
        'items': items
    }

def get(query, **kwargs):
    params = {
        'limit': 1,
        'page': 1,
        'quality': 'all',
        'query_term': query
    }
    data = url_get(_getDomains(), "/api/v2/list_movies.json", params=params, proxyid=_proxy_identifier)
    movies = data.get("data", {}).get("movies")
    if not movies:
        return {}

    if not movies[0].g("title") or not movies[0].get("imdb_code"):
        return []

    return _create_item(movies[0], kwargs['qualities'])

def search(query, page, **kwargs):
    params = {
        'limit': kwargs['limit'],
        'page': page,
        'quality': 'all',
        'query_term': query
    }
    data = url_get(_getDomains(), "/api/v2/list_movies.json", params=params, proxyid=_proxy_identifier)
    movies = data.get("data", {}).get("movies")
    if not movies:
        return {}

    items = []
    for movie in movies:
        if not movie.get("title") or not movie.get("imdb_code"):
            continue
        item = _create_item(movie, kwargs['qualities'])
        if not item:
            continue
        items.append(item)

    _tmp = int(data.get("data", {}).get("movie_count", 20))/int(kwargs['limit'])
    pages = int(_tmp)
    if _tmp > pages:
        pages = pages+1

    return {
        'pages': pages,
        'items': items
    }

def _getDomains():
    domains = [
        "http://yts.to",
        "http://eqwww.image.yt"
    ]

    userDomains = __addon__.getSetting("yify_domain").split(',')
    # Evaluate user domain
    for userDomain in reversed(userDomains):
        uD = urlparse(userDomain)
        if not uD.netloc:
            continue
        fUD = "{scheme}://{netloc}".format(scheme=uD.scheme or 'http', netloc=uD.netloc)
        # Prioritize user domain
        if fUD in domains:
            domains.remove(fUD)
        domains.insert(0, fUD)

    return domains

def _create_item(movie, qualities):
    torrents = {}
    for torrent in movie.get("torrents", []):
        if not torrent.get("hash") or not torrent.get("quality") or not torrent.get("quality") in qualities:
            continue
        torrents.update({
            torrent["quality"]: torrent["hash"]
        })

    if not torrents:
        return {}

    return {
        "label": movie["title"],
        "icon": movie.get("medium_cover_image", movie.get("small_cover_image", '')),
        "thumbnail": movie.get("medium_cover_image", movie.get("small_cover_image", '')),
        "torrents": torrents,
        "info": {
            "title": movie["title"],
            "genre": movie.get("genres") and " / ".join([genre for genre in movie["genres"]]) or "",
            "duration": int(movie.get("runtime", 0))*60,
            "code": movie["imdb_code"],
            "year": movie.get("year", '')
        },
        "properties": {
            "fanart_image": movie.get("background_image", '')
        },
        "stream_info": {
            "video": {
                "codec": "h264",
                "duration": movie.get("runtime", 0)
            },
            "audio": {
                "codec": "aac",
                "language": "en",
                'channels': 2
            }
        }
    }
