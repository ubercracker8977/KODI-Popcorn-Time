import json
import os
import sys
import urllib2

import xbmc

from kodipopcorntime import settings
from kodipopcorntime.exceptions import Abort


__addon__ = sys.modules['__main__'].__addon__


class BaseContent(object):
    # TODO: WIP for common functionality
    pass


class BaseContentWithSeasons(BaseContent):
    @classmethod
    def get_shows(cls, dom, **kwargs):
        if kwargs['search'] == 'true':
            search_string = xbmc.getInfoLabel("ListItem.Property(searchString)")
            if not search_string:
                keyboard = xbmc.Keyboard('', __addon__.getLocalizedString(30001), False)
                keyboard.doModal()
                if not keyboard.isConfirmed() or not keyboard.getText():
                    raise Abort()
                search_string = keyboard.getText()
                search_string = search_string.replace(' ', '+')
            search = '{domain}/{search_path}/1?keywords={keywords}'.format(
                domain=dom[0],
                search_path=cls.search_path,
                keywords=search_string,
            )
        else:
            search = '{domain}/{search_path}/{page}?genre={genre}&sort={sort}'.format(
                domain=dom[0],
                search_path=cls.search_path,
                page=kwargs['page'],
                genre=kwargs['genre'],
                sort=kwargs['act'],
            )

        req = urllib2.Request(
            search,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36",
                "Accept-Encoding": "none",
            },
        )
        response = urllib2.urlopen(req)
        results = json.loads(response.read())

        items = [
            {
                "label": result['title'],  # "label" is required
                "icon": result.get('images').get('poster'),
                "thumbnail": result.get('images').get('poster'),
                "info": {
                    "title": result['title'],
                    "plot": 'Year: %s; Rating: %s' % (result['year'], result.get('rating').get('percentage')),
                },
                "properties": {
                    "fanart_image": result.get('images').get('fanart'),
                },
                "params": {
                    "endpoint": "folders",  # "endpoint" is required
                    'action': "{category}-seasons".format(category=cls.category),  # Required when calling browse or folders (Action is used to separate the content)
                    cls.id_field: result[cls.id_field],
                    'poster': result.get('images').get('poster'),
                    'fanart': result.get('images').get('fanart'),
                    'tvshow': result['title']
                },
                "context_menu": [
                    (
                        '%s' % __addon__.getLocalizedString(30039),
                        'RunPlugin(plugin://plugin.video.kodipopcorntime?cmd=add_fav&action={action}&id={id})'.format(
                            action=cls.action,
                            id=result[cls.id_field],
                        ),
                    )
                ],
                "replace_context_menu": True
            }
            for result in results
        ]

        # Next Page
        items.append({
            "label": 'Show more',  # "label" is required
            "icon": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more.png'),
            "thumbnail": os.path.join(settings.addon.resources_path, 'media', 'movies', 'more_thumbnail.png'),
            "params": {
                "endpoint": "folders",  # "endpoint" is required
                'action': "{category}-list".format(category=cls.category),  # Required when calling browse or folders (Action is used to separate the content)
                'act': kwargs['act'],
                'genre': kwargs['genre'],
                'search': kwargs['search'],
                'page': int(kwargs['page']) + 1,
            },
        })

        return items

    @classmethod
    def get_seasons(cls, dom, **kwargs):
        req = urllib2.Request(
            '{domain}/{request_path}/{content_id}'.format(
                domain=dom[0],
                request_path=cls.request_path,
                content_id=kwargs[cls.id_field]
            ),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36",
                "Accept-Encoding": "none",
            },
        )

        response = urllib2.urlopen(req)
        result = json.loads(response.read())
        seasons = result['episodes']

        season_list = sorted(list(set(
            season['season']
            for season in seasons
        )))

        return [
            {
                "label": 'Season %s' % season,  # "label" is required
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
                    'categ': cls.category,  # "categ" is required when using browse as an endpoint
                    'seasons': season,
                    'image': kwargs['poster'],
                    'image2': kwargs['fanart'],
                    'tvshow': kwargs['tvshow'],
                    "endpoint": "browse",  # "endpoint" is required
                    'action': kwargs[cls.id_field]  # Required when calling browse or folders (Action is used to separate the content)
                }
            }
            for season in season_list
        ]
