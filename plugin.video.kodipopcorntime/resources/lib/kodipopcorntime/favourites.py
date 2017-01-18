import json
import os, sys, xbmcaddon, xbmc
from kodipopcorntime.logging import log, LOGLEVEL

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))

_json_file = os.path.join(__addondir__, 'favourites.json')

_skeleton = {
    "movies": [

    ],
    "tvshows": [

    ],
    "anime": [

    ]
}

def create_skeleton_file():
    with open(_json_file, mode='w+') as json_file:
        json_file.write(json.dumps(_skeleton, indent = 3))
        log("(Favourites) File created")

def _add_to_favs(mediatype, data):
    if not os.path.isfile(_json_file):
        create_skeleton_file

    with open(_json_file) as json_read:
        favourites = json.load(json_read)
    log("(Favourites) _add_to_favs %s" %favourites)

    if mediatype == 'movies':
        movie_fav = favourites.get('movies')
        for item in movie_fav:
            if item['id'] == data:
                data = None
        if data:
            data2 = {'id': '%s' %data}
            movie_fav.append(data2)
        favourites2 = {
            'movies': movie_fav,
            'tvshows': favourites.get('tvshows'),
            'anime': favourites.get('anime')
        }
    if mediatype == 'tvshows':
        tvshow_fav = favourites.get('tvshows')
        for item in tvshow_fav:
            if item['id'] == data:
                data = None
        if data:
            data2 = {'id': '%s' %data}
            tvshow_fav.append(data2)
        favourites2 = {
            'movies': favourites.get('movies'),
            'tvshows': tvshow_fav,
            'anime': favourites.get('anime')
        }
    if mediatype == 'anime':
        anime_fav = favourites.get('anime')
        for item in anime_fav:
            if item['id'] == data:
                data = None
        if data:
            data2 = {'id': '%s' %data}
            anime_fav.append(data2)
        favourites2 = {
            'movies': favourites.get('movies'),
            'tvshows': favourites.get('tvshows'),
            'anime': anime_fav
        }

    log("(Favourites2) _add_to_favs %s" %favourites2)
    with open(_json_file, mode='w') as json_write:
        json_write.write(json.dumps(favourites2, indent=3))

    xbmc.executebuiltin('Notification(%s, %s favourite has been added, 5000)' % (__addonname__, mediatype))

def _remove_from_favs(mediatype, data):
    with open(_json_file) as json_read:
        favourites = json.load(json_read)
    log("(Favourites) _remove_from_favs %s" %favourites)

    if mediatype == 'movies':
        movie_fav = favourites.get('movies')
        movie_fav2 = []
        for item in movie_fav:
            if item['id'] == data:
                pass
            else:
                movie_fav2.append(item)
        favourites2 = {
            'movies': movie_fav2,
            'tvshows': favourites.get('tvshows'),
            'anime': favourites.get('anime')
        }
    if mediatype == 'tvshows':
        tvshow_fav = favourites.get('tvshows')
        tvshow_fav2 = []
        for item in tvshow_fav:
            if item['id'] == data:
                pass
            else:
                tvshow_fav2.append(item)
        favourites2 = {
            'movies': favourites.get('movies'),
            'tvshows': tvshow_fav2,
            'anime': favourites.get('anime')
        }
    if mediatype == 'anime':
        anime_fav = favourites.get('anime')
        anime_fav2 = []
        for item in anime_fav:
            if item['id'] == data:
                pass
            else:
                anime_fav2.append(item)
        favourites2 = {
            'movies': favourites.get('movies'),
            'tvshows': favourites.get('tvshows'),
            'anime': anime_fav2
        }

    log("(Favourites2) _add_to_favs %s" %favourites)
    with open(_json_file, mode='w') as json_write:
        json_write.write(json.dumps(favourites2, indent=3))

    xbmc.executebuiltin('Notification(%s, %s favourite has been removed, 5000)' % (__addonname__, mediatype))
    xbmc.executebuiltin('Container.Refresh')

def _get_favs(mediatype):
    if not os.path.isfile(_json_file):
        log("(Favourites) File does not exist")
        create_skeleton_file()

    with open(_json_file) as json_read:
        favourites = json.load(json_read)
        log("(Favourites) _get_favs %s" %favourites)
    return favourites.get('%s' %mediatype)

def _clear_favourites(mediatype):
    if mediatype == 'all':
        create_skeleton_file
    else:
        if mediatype == 'movies': #TODO
            return {}

        if mediatype == 'tvshows': #TODO
            return {}

        if mediatype == 'anime': #TODO
            return {}
