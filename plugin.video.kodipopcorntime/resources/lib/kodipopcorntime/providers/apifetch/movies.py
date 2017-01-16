import os
import re
import sys
import urllib2
import xbmc
from kodipopcorntime import settings
__addon__ = sys.modules['__main__'].__addon__

_genres = {
    '30400': 'Action',
    '30401': 'Adventure',
    '30402': 'Animation',
    '30403': 'Comedy',
    '30404': 'Crime',
    '30405': 'Disaster',
    '30406': 'Documentary',
    '30407': 'Drama',
    '30408': 'Eastern',
    '30409': 'Family',
    '30410': 'Fan-Film',
    '30411': 'Fantasy',
    '30412': 'Film-Noir',
    '30413': 'History',
    '30414': 'Horror',
    '30415': 'Indie',
    '30416': 'Music',
    '30417': 'Mystery',
    '30418': 'Road',
    '30419': 'Romance',
    '30420': 'Science-Fiction',
    '30421': 'Short',
    '30422': 'Sports',
    '30423': 'Sporting-event',
    '30424': 'Suspence',
    '30425': 'Thriller',
    '30426': 'TV-Movie',
    '30427': 'War',
    '30428': 'Western'
}

def _create_item(data):
    if not data.get("title"): # Title is require
        return {}

    torrents = {}
    for quality, torrent_info in data.get('torrents').get('en', {}).items():
        if quality in settings.QUALITIES:
            torrents[quality] = torrent_info.get('url')
            torrents['%ssize' % quality] = torrent_info.get('size')

    # Do not show Movies without torrents
    if not torrents:
        return {}

    # Set video width and height
    width = 640
    height = 480
    if torrents.get('1080p'):
        width = 1920
        height = 1080
    elif torrents.get('720p'):
        width = 1280
        height = 720

    title = data["title"]

    trailer = ''
    if data.get("trailer"):
        trailer_regex = re.match('^[^v]+v=(.{11}).*', data.get("trailer"))
        try:
            trailer_id = trailer_regex.group(1)
            trailer = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" %trailer_id
        except:
            pass

    return {
        "label": title,
        "icon": data.get('images').get('poster'),
        "thumbnail": data.get('images').get('poster'),
        "info": {
            "title": title,
            "year": int(data.get("year") or 0),
            "genre": u" / ".join(genre for genre in data.get("genres", [])) or None,
            #"duration": int(0),
            "code": data.get("imdb_id"),
            "plot": data.get('synopsis') or None,
            "plotoutline": data.get('synopsis') or None,
            "trailer": trailer
        },
        "properties": {
            "fanart_image": data.get('images').get('fanart')
        },
        "stream_info": {
            "video": {
                "codec": u"h264",
                "duration": int(0),
                "width": width,
                "height": height
            },
            "audio": {
                "codec": u"aac",
                "language": u"en",
                "channels": 2
            }
        },
        "params": torrents
    }

def _folders(action, **kwargs):
    if action == 'cat_Movies':
        return [
            {
                # Search option
                "label": __addon__.getLocalizedString(30002),                   # "label" is required
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "search"                                        # "endpoint" is required
                }
            },
            {
                # Most Popular option
                "label": __addon__.getLocalizedString(30004),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'popular.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'popular.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "browse",                                       # "endpoint" is require
                    'action': "trending",                                       # Require when calling browse or folders (Action is used to separate the content)
                    'order': '-1'
                }
            },
            {
                # Recently Added Option
                "label": __addon__.getLocalizedString(30006),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'recently.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'recently.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "browse",                                       # "endpoint" is required
                    'action': "last_added",                                     # Require when calling browse or folders (Action is used to separate the content)
                    'order': '-1'
                }
            },
            {
                # Best Rated Option
                "label": __addon__.getLocalizedString(30005),                       # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "browse",                                       # "endpoint" is require
                    'action': "rating",                                         # Require when calling browse or folders (Action is used to separate the content)
                    'order': '-1'
                }
            },
            {
                # Sort by Title Option
                "label": __addon__.getLocalizedString(30025),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "browse",                                       # "endpoint" is require
                    'action': "title",                                          # Require when calling browse or folders (Action is used to separate the content)
                    'order': '1'
                }
            },
            {
                # Sort By Year
                "label": __addon__.getLocalizedString(30026),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "categ": "movies",                                          # "categ" is required when using browse as an endpoint
                    "endpoint": "browse",                                       # "endpoint" is require
                    'action': "year",                                           # Require when calling browse or folders (Action is used to separate the content)
                    'order': '-1'
                }
            },
            {
                # Browse by Genre Option
                "label": __addon__.getLocalizedString(30003),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "params": {
                    "endpoint": "folders",                                      # "endpoint" is require
                    'action': "genres_movies"                                   # Require when calling browse or folders (Action is used to separate the content)
                }
            }
            ]
    if action == 'genres_movies':
        '''Action genres_movies creates a list of genres'''
        items= []
        for n in __addon__.getLocalizedString(30499).split(','):
            if _genres.get(n):
                path = os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres', '%s.png' %_genres[n])
                items.append({
                    "label": __addon__.getLocalizedString(int(n)),              # "label" is require
                    "icon": path,
                    "thumbnail": path,
                    "params": {
                        "categ": "movies",                                      # "categ" is required when using browse as an endpoint
                        "endpoint": "browse",                                   # "endpoint" is require
                        'action': "genre",                                      # Require when calling browse or folders (Action is used to separate the content)
                        'genre': _genres[n],
                        'order': '-1'
                    }
                })
        return items

def _search(proxy, dom, query, page, **kwargs):
    '''search are used to returning parameters used for 'Request' when a search result is displayed.
       :param query: (string) Contains an query string
       :param page: (int) Contains the current page number
       :param kwargs: (dict) Contain user parameters
       :return: (dict) Return parameters used for 'Request'
    '''
    return {
        'proxies': dom,
        'path': "/tv/movies/%s" %page,
        'params': {
            'page': page,
            'quality': 'all',
            'keywords': query.encode('UTF-8')
        },
    'proxyid': proxy
    }

def _search_build(data, query, page, **kwargs):
    '''search_build are used to create a dict with the items when a search result is displayed.
       :param data: Contains a list with data from 'Request'
       :param query: (string) Contains an query string
       :param page: (int) Contains the current page number
       :param kwargs: (dict) Contain user parameters that were given to search function
       :return: Return a dict
    '''
    items = []
    for movie in data:
        item = _create_item(movie)
        if item:
            items.append(item)
    if not items:
        return {}

    return {
        'pages': 50,
        'items': items
    }
