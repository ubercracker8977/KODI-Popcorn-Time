import json
import urllib2


class BaseContent(object):
    # TODO: WIP for common functionality
    pass


class BaseContentWithSeasons(BaseContent):
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
