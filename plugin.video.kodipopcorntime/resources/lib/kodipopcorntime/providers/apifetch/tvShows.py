import json
import os
import sys
import urllib2
import xbmc

from kodipopcorntime import settings
from kodipopcorntime import favourites as _favs

from .base import BaseContentWithSeasons


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


class TvShow(BaseContentWithSeasons):
    category = 'show'
    # Request path is created as: '{domain}/{request_path}/kwargs[id_field]'.
    # We need to provide the correct values for request_path and id_field.
    request_path = 'tv/show'
    id_field = 'imdb_id'


def _folders(action, **kwargs):
    if action == 'cat_TVShows':
        '''Action cat_TVShows creates a list of options for TV Shows '''
        return [
            {
                # Sarch Option
                "label": __addon__.getLocalizedString(30002),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "params": {
                    "act": "search",
                    'search': 'true',
                    'action': 'show-list',                                      # Require when calling browse or folders (Action is used to separate the content)
                    "endpoint": "folders",                                       # "endpoint" is require
                    'page': 1,
                    'genre': 'all'
                }
            },
            {
                # Most Popular Option
                "label": __addon__.getLocalizedString(30004),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'popular.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'popular.png'),
                "params": {
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "trending",
                    'search': 'false',
                    'genre': 'all',
                    'page': 1,
                    'action': "show-list"                                       # Require when calling browse or folders (Action is used to separate the content)
                }
            },
            {
                # Last Updated Option
                "label": __addon__.getLocalizedString(30027),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'recently.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'recently.png'),
                "params": {
                    "action": "show-list",                                      # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    'page': 1,
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "updated"
                }
            },
            {
                # Best Rated Option
                "label": __addon__.getLocalizedString(30005),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "show-list",                                      # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    'page': 1,
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "rating"
                }
            },
            {
                # Sort by Title Option
                "label": __addon__.getLocalizedString(30025),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "show-list",                                      # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    'page': 1,
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "name"
                }
            },
            {
                # Sort by Year Option
                "label": __addon__.getLocalizedString(30026),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "show-list",                                      # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    'page': 1,
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "year"
                }
            },
            {
                # Browse by Genre Option
                "label": __addon__.getLocalizedString(30003),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "params": {
                    "endpoint": "folders",                                      # "endpoint" is require
                    'action': "genres_TV-shows"                                 # Require when calling browse or folders (Action is used to separate the content)
                }
            },
            {
                # Favourites Option
                "label": __addon__.getLocalizedString(30029),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "favorites_TV-Shows",                                      # Require when calling browse or folders (Action is used to separate the content)
                    "endpoint": "folders",                                      # "endpoint" is require
                }
            }
        ]

    if action == 'genres_TV-shows':
        '''Action genres_movies creates a list of genres'''
        items = []
        for n in __addon__.getLocalizedString(30499).split(','):
            if _genres.get(n):
                path = os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres', '%s.png' %_genres[n])
                items.append({
                    "label": __addon__.getLocalizedString(int(n)),              # "label" is require
                    "icon": path,
                    "thumbnail": path,
                    "params": {
                        "action": "show-list",                                   # Require when calling browse or folders (Action is used to separate the content)
                        'search': 'false',
                        "endpoint": "folders",                                  # "endpoint" is require
                        'act': "genre",
                        'page': 1,
                        'genre': _genres[n]
                    }
                })
        return items

def _shows(dom, **kwargs):

        '''Action show-list creates a list of TV Shows'''
        action = 'tvshows'

        page = kwargs['page']

        # Search Dialog
        if kwargs['search'] == 'true':
            search_string = xbmc.getInfoLabel("ListItem.Property(searchString)")
            if not search_string:
                keyboard = xbmc.Keyboard('', __addon__.getLocalizedString(30001), False)
                keyboard.doModal()
                if not keyboard.isConfirmed() or not keyboard.getText():
                    raise Abort()
                search_string = keyboard.getText()
                search_string=search_string.replace(' ', '+')
            search = '%s/tv/shows/1?keywords=%s' % (dom[0], search_string)
        else:
            search = '%s/tv/shows/%s?genre=%s&sort=%s' % (dom[0], page, kwargs['genre'], kwargs['act'])

        req = urllib2.Request(search, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36", "Accept-Encoding": "none"})
        response = urllib2.urlopen(req)
        shows = json.loads(response.read())
        items = []
        for show in shows:
            context_menu = [('%s' %__addon__.getLocalizedString(30039), 'RunPlugin(plugin://plugin.video.kodipopcorntime?cmd=add_fav&action=%s&id=%s)' % (action, show['imdb_id']))]
            items.append({
                "label": show['title'],                                         # "label" is require
                "icon": show.get('images').get('poster'),
                "thumbnail": show.get('images').get('poster'),
                "info": {
                    "title": show['title'],
                    "plot": 'Year: %s; Rating: %s' % (show['year'], show.get('rating').get('percentage')) or None
                },
                "properties": {
                    "fanart_image": show.get('images').get('fanart'),
                },
                "params": {
                    "seasons": show['num_seasons'],
                    "endpoint": "folders",                                      # "endpoint" is require
                    'action': "show-seasons",                                   # Require when calling browse or folders (Action is used to separate the content)
                    'imdb_id': show['imdb_id'],
                    'poster': show.get('images').get('poster'),
                    'fanart': show.get('images').get('fanart'),
                    'tvshow': show['title']
                },
                "context_menu": context_menu,
                "replace_context_menu": True
            })

        # Next Page
        items.append({
            "label": 'Show more',                                               # "label" is require
            "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more.png'),
            "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more_thumbnail.png'),
            "params": {
                "endpoint": "folders",                                          # "endpoint" is require
                'action': "show-list",                                          # Require when calling browse or folders (Action is used to separate the content)
                'act': kwargs['act'],
                'genre': kwargs['genre'],
                'search': kwargs['search'],
                'page': int(page)+1
            }
        })

        return items

def _favourites(dom, **kwargs):

    action = 'tvshows'
    favs = _favs._get_favs(action)

    shows = []
    for fa in favs:
        search = '%s/tv/show/%s' % (dom[0], fa['id'])
        req = urllib2.Request(search, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36", "Accept-Encoding": "none"})
        response = urllib2.urlopen(req)
        show1 = json.loads(response.read())

        shows.append({
            "_id": fa['id'],
            "imdb_id": fa['id'],
            "tvdb_id": show1['tvdb_id'],
            "title": show1['title'],
            "year": show1['year'],
            "slug": show1['slug'],
            "num_seasons": show1['num_seasons'],
            "images": show1['images'],
            "rating": show1['rating']
        })

    items = []
    for show in shows:
        context_menu = [('%s' %__addon__.getLocalizedString(30040), 'RunPlugin(plugin://plugin.video.kodipopcorntime?cmd=remove_fav&action=%s&id=%s)' % (action, show['imdb_id']))]
        items.append({
            "label": show['title'],                                         # "label" is require
            "icon": show.get('images').get('poster'),
            "thumbnail": show.get('images').get('poster'),
            "info": {
                "title": show['title'],
                "plot": 'Year: %s; Rating: %s' % (show['year'], show.get('rating').get('percentage')) or None
            },
            "properties": {
                "fanart_image": show.get('images').get('fanart'),
            },
            "params": {
                "seasons": show['num_seasons'],
                "endpoint": "folders",                                      # "endpoint" is require
                'action': "show-seasons",                                   # Require when calling browse or folders (Action is used to separate the content)
                'imdb_id': show['imdb_id'],
                'poster': show.get('images').get('poster'),
                'fanart': show.get('images').get('fanart'),
                'tvshow': show['title']
            },
            "context_menu": context_menu,
            "replace_context_menu": True
        })

    return items


def _seasons(dom, **kwargs):
    return TvShow.get_seasons(dom, **kwargs)


def _create_item(data):
    label = 'Episode %s: %s' % (data[0]['episode'], data[0]['title'])

    # seasondata0 has all the data from show
    seasondata0 = int(data[0]['season'])

    # seasondata_1 carries additional user data not included in show data
    seasondata_1 = int(data[-1]['seasons'])
    if not seasondata0 == seasondata_1:
        return {}

    torrents = {}
    for quality, torrent_info in data[0].get('torrents', {}).items():
        torrent_url = torrent_info.get('url')
        if quality in settings.QUALITIES and torrent_url is not None:
            torrents[quality] = torrent_url
            torrents['%ssize' % quality] = 1000000000*60

    # Do not return Shows  without torrents
    if not torrents:
        return {}

    # Set video width and hight
    width = 640
    height = 480
    if torrents.get('1080p'):
        width = 1920
        height = 1080
    elif torrents.get('720p'):
        width = 1280
        height = 720

    return {
        "label": label,
        "icon": data[-1]['image'],
        "thumbnail": data[-1]['image'],
        "info": {
            "title": data[0]['title'],
            "season": int(data[0].get('season') or 0),
            "episode": int(data[0].get('episode') or 0),
            "tvshowtitle": data[-1]['tvshow'],
            #"duration": int(0),
            "code": data[0].get("tvdb_id"),
            "plot": data[0]['overview'],
            "plotoutline": data[0]['overview']
        },
        "properties": {
            "fanart_image": data[-1]['image2'],
            "tvshowthumb": data[-1]['image2']
        },
        "stream_info": {
            "video": {
                "codec": u"h264",
                #"duration": int(0),
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
