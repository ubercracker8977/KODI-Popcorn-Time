from functools import wraps
import json
import os
import xbmc
import xbmcaddon

from kodipopcorntime.logging import log


__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))

_json_file = os.path.join(__addondir__, 'favourites.json')

_skeleton = {
    "movies": [],
    "tvshows": [],
    "anime": [],
}


def create_skeleton_file():
    with open(_json_file, mode='w+') as json_file:
        json_file.write(json.dumps(_skeleton, indent=3))
        log("(Favourites) File created")


def create_skeleton_file_if_missing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.path.isfile(_json_file):
            create_skeleton_file()

        return func(*args, **kwargs)
    return wrapper


@create_skeleton_file_if_missing
def _add_to_favs(mediatype, data):
    with open(_json_file) as json_read:
        favourites = json.load(json_read)
    log("(Favourites) _add_to_favs %s" % favourites)

    add_favourite_by_type(new_fav_id=data, fav_type=mediatype, favourites=favourites)

    log("(Favourites2) _add_to_favs %s" % favourites)
    with open(_json_file, mode='w') as json_write:
        json_write.write(json.dumps(favourites, indent=3))

    xbmc.executebuiltin('Notification(%s, %s favourite has been added, 5000)' % (__addonname__, mediatype))


@create_skeleton_file_if_missing
def _remove_from_favs(mediatype, data):
    with open(_json_file) as json_read:
        favourites = json.load(json_read)
    log("(Favourites) _remove_from_favs %s" % favourites)

    remove_favourite_by_type(fav_id=data, fav_type=mediatype, favourites=favourites)

    log("(Favourites2) _remove_from_favs %s" % favourites)
    with open(_json_file, mode='w') as json_write:
        json_write.write(json.dumps(favourites, indent=3))

    xbmc.executebuiltin('Notification(%s, %s favourite has been removed, 5000)' % (__addonname__, mediatype))
    xbmc.executebuiltin('Container.Refresh')


@create_skeleton_file_if_missing
def _get_favs(mediatype):
    with open(_json_file) as json_read:
        favourites = json.load(json_read)
        log("(Favourites) _get_favs %s" % favourites)
    return favourites.get('%s' % mediatype)


def _clear_favourites(mediatype):
    if mediatype == 'all':
        create_skeleton_file()
    else:
        if mediatype == 'movies':  # TODO
            return {}

        elif mediatype == 'tvshows':  # TODO
            return {}

        elif mediatype == 'anime':  # TODO
            return {}


def add_favourite_by_type(new_fav_id, fav_type, favourites):
    """
    Modifies the `favourites` dictionary by adding the `new_fav_id` to its
    `fav_type` inner list, if it is not already a favourite.

    Examples of `fav_type` are: 'movies', 'tvshows', 'anime'
    """
    type_favourites = favourites.get(fav_type)

    if all(fav['id'] != new_fav_id for fav in type_favourites):
        type_favourites.append({'id': str(new_fav_id)})


def remove_favourite_by_type(fav_id, fav_type, favourites):
    """
    Modifies the `favourites` dictionary by removing the `fav_id` from its
    `fav_type` inner list.

    Examples of `fav_type` are: 'movies', 'tvshows', 'anime'
    """
    favourites[fav_type] = filter(
        lambda fav: fav['id'] != fav_id,
        favourites.get(fav_type),
    )
