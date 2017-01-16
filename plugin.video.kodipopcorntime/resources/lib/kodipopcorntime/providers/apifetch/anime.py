import json
import os
import sys
import urllib2
import xbmc
from kodipopcorntime import settings
__addon__ = sys.modules['__main__'].__addon__

_genres = {
  '30450': 'Action',
  '30451': 'Ecchi',
  '30452': 'Harem',
  '30453': 'Romance',
  '30454': 'School',
  '30455': 'Supernatural',
  '30456': 'Drama',
  '30457': 'Comedy',
  '30458': 'Mystery',
  '30459': 'Police',
  '30461': 'Sports',
  '30462': 'Mecha',
  '30463': 'Sci-Fi',
  '30464': 'Slice+of+Life',
  '30465': 'Fantasy',
  '30466': 'Adventure',
  '30467': 'Gore',
  '30468': 'Music',
  '30469': 'Psychological',
  '30470': 'Shoujo+Ai',
  '30471': 'Yuri',
  '30472': 'Magic',
  '30473': 'Horror',
  '30474': 'Thriller',
  '30475': 'Gender+Bender',
  '30476': 'Parody',
  '30477': 'Historical',
  '30478': 'Racing',
  '30479': 'Samurai',
  '30480': 'Super+Power',
  '30481': 'Military',
  '30482': 'Dementia',
  '30483': 'Mahou+Shounen',
  '30484': 'Game',
  '30485': 'Martial+Arts',
  '30486': 'Vampire',
  '30487': 'Kids',
  '30488': 'Mahou+Shoujo',
  '30489': 'Space',
  '30490': 'Shounen+Ai'
}

def _folders(action, **kwargs):
    if action == 'cat_Anime':
        '''Action cat_TVShows creates a list of options for TV Shows '''
        return [
            {
                # Search Option
                "label": __addon__.getLocalizedString(30002),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'search.png'),
                "params": {
                    "act": "search",
                    'search': 'true',
                    'action': 'anime-list',                                     # Require when calling browse or folders (Action is used to separate the content)
                    "endpoint": "folders",                                       # "endpoint" is require
                    'page': 1,
                    'genre': 'all'
                }
            },
            {
                # Best Rated Option
                "label": __addon__.getLocalizedString(30005),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "anime-list",                                     # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "rating",
                    'page': 1
                }
            },
            {
                # Sort by Title Option
                "label": __addon__.getLocalizedString(30025),            #Title           # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "anime-list",                                     # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "name",
                    'page': 1
                }
            },
            {
                # Sort by Year Option
                "label": __addon__.getLocalizedString(30026),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'rated.png'),
                "params": {
                    "action": "anime-list",                                     # Require when calling browse or folders (Action is used to separate the content)
                    'search': 'false',
                    'genre': 'all',
                    "endpoint": "folders",                                      # "endpoint" is require
                    'act': "year",
                    'page': 1
                }
            },
            {
                # Browse by Genre Option
                "label": __addon__.getLocalizedString(30003),                   # "label" is require
                "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres.png'),
                "params": {
                    "endpoint": "folders",                                      # "endpoint" is require
                    'action': "genres_anime"                                    # Require when calling browse or folders (Action is used to separate the content)
                }
            }
        ]

    if action == 'genres_anime':
        '''Action genres_anime creates a list of genres'''
        items= []
        for n in __addon__.getLocalizedString(30498).split(','):
            if _genres.get(n):
                path = os.path.join(settings.addon.resources_path, 'media', 'movies', 'genres', '%s.png' %_genres[n])
                items.append({
                    "label": __addon__.getLocalizedString(int(n)),              # "label" is require
                    "icon": path,
                    "thumbnail": path,
                    "params": {
                        "action": "anime-list",                                 # Require when calling browse or folders (Action is used to separate the content)
                        'search': 'false',
                        "endpoint": "folders",                                  # "endpoint" is require
                        'act': "genre",
                        'genre': _genres[n],
                        'page': 1
                    }
                })
        return items

def _shows(dom, **kwargs):
    if kwargs['search'] == 'true':
        search_string = xbmc.getInfoLabel("ListItem.Property(searchString)")
        if not search_string:
            keyboard = xbmc.Keyboard('', __addon__.getLocalizedString(30001), False)
            keyboard.doModal()
            if not keyboard.isConfirmed() or not keyboard.getText():
                raise Abort()
            search_string = keyboard.getText()
            search_string = search_string.replace(' ', '+')
        search = '%s/tv/animes/1?keywords=%s' % (dom[0], search_string)
    else:
        search = '%s/tv/animes/%s?genre=%s&sort=%s' % (dom[0], kwargs['page'], kwargs['genre'], kwargs['act'])

    req = urllib2.Request(search, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36", "Accept-Encoding": "none"})
    response = urllib2.urlopen(req)
    animes = json.loads(response.read())

    items = []
    for anime in animes:
        items.append({
            "label": anime['title'],                                        # "label" is require
            "icon": anime.get('images').get('poster'),
            "thumbnail": anime.get('images').get('poster'),
            "info": {
                "title": anime['title'],
                "plot": 'Year: %s; Rating: %s' % (anime['year'], anime.get('rating').get('percentage')) or None
            },
            "properties": {
                "fanart_image": anime.get('images').get('fanart')
            },
            "params": {
                "endpoint": "folders",                                      # "endpoint" is require
                'action': "anime-seasons",                                  # Require when calling browse or folders (Action is used to separate the content)
                '_id': anime['_id'],
                'poster': anime.get('images').get('poster'),
                'fanart': anime.get('images').get('fanart'),
                'tvshow': anime['title']
            }
        })

    # Next Page
    items.append({
        "label": 'Show more',                                               # "label" is require
        "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more.png'),
        "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more_thumbnail.png'),
        "params": {
            "endpoint": "folders",                                          # "endpoint" is require
            'action': "anime-list",                                          # Require when calling browse or folders (Action is used to separate the content)
            'act': kwargs['act'],
            'genre': kwargs['genre'],
            'search': kwargs['search'],
            'page': int(kwargs['page'])+1
        }
    })

    return items

def _seasons(dom, **kwargs):
    items = []
    search = '%s/tv/anime/%s' % (dom[0], kwargs['_id'])

    req = urllib2.Request(search, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36", "Accept-Encoding": "none"})
    response = urllib2.urlopen(req)
    result = json.loads(response.read())

    seasons = result['episodes']

    season_list = []
    for season in seasons:
        season_list.append(season['season'])

    season_list2 = sorted(list(set(season_list)))

    for season2 in season_list2:
        items.append({
            "label": 'Season %s' %season2,                                  # "label" is require
            "icon": kwargs['poster'],
            "thumbnail": kwargs['poster'],
            "info": {
                "title": result['title'],
                "plotoutline": result['synopsis'] or None,
                "plot": result['synopsis'] or None
            },
            "properties": {
                "fanart_image": kwargs['fanart']
            },
            "params": {
                'categ': 'anime',                                           # "categ" is required when using browse as an endpoint
                'seasons': season2,
                'image': kwargs['poster'],
                'image2': kwargs['fanart'],
                'tvshow': kwargs['tvshow'],
                "endpoint": "browse",                                       # "endpoint" is require
                'action': kwargs['_id']                                     # Require when calling browse or folders (Action is used to separate the content)
            }
        })
    return items

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
            "genre": u" / ".join(genre for genre in data[0].get("genres", [])) or None,
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
