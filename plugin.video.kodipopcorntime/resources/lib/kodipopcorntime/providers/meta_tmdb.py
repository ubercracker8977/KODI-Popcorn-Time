#!/usr/bin/python
import xbmc
from kodipopcorntime.utils import url_get, cleanDictList
from kodipopcorntime.caching import shelf

provides = 'movies.meta'

_api_key = "308a68c313ff66d165c1eb029b0716bc"
_base_url = "http://api.themoviedb.org"

def get(id, label, year):
    # English
    params={
        "api_key": _api_key,
        "append_to_response": "credits",
        "language": "en",
        "include_image_language": "en,null"
    }
    meta = url_get(_base_url, "/3/movie/{id}".format(id=id), params=params)
    if not meta or meta.get('status_code'):
        return {}

    # System language
    sys_lang = xbmc.getLanguage(xbmc.ISO_639_1)
    if not sys_lang == 'en':
        params.update({"language": sys_lang, "include_image_language": sys_lang})
        sys_meta = url_get(_base_url, "/3/movie/{id}".format(id=id), params=params)
        if sys_meta and not sys_meta.get('status_code'):
            meta.update(cleanDictList(sys_meta))

    return _create_item(meta)

def search(query, page, **kwargs):
    params = {
        "api_key": _api_key,
        "query": query,
        "language": "en",
        "page": page
    }
    results = url_get(_base_url, "/3/search/movie".format(id=id), params=params)
    if results.get('status_code'):
        return {}
    items = []
    for movie in results:
        items.append(_create_item(movie))
    return {
        'pages': data.get("total_pages", 1),
        'items': items
    }

def _tmdb_config():
    with shelf("meta.imdb.conf", 24 * 3600) as conf:
        if not conf:
            try:
                conf.update(url_get(_base_url, "/3/configuration", params={"api_key": _api_key}))
            except:
                return {}
        return dict(conf)

def _create_item(meta):
    item = {
        "label": meta.get("title", ''),
        "info": {
            "title": meta.get("title", ''),
            "year": int(meta.get("release_date", '0-').split("-")[0]),
            "originaltitle": meta.get("original_title", ''),
            "genre": " / ".join([g["name"] for g in meta.get("genres", [])]),
            "plot": meta.get("overview", ''),
            "plotoutline": meta.get("overview", ''),
            "tagline": meta.get("tagline", ''),
            "rating": float(meta.get("vote_average", 0.0)),
            "duration": str(meta.get("runtime", '')),
            "code": meta.get("imdb_id", ''),
            "studio": " / ".join([s['name'] for s in meta.get("production_companies", [])]),
            "votes": meta.get("vote_average") and str(meta.get("vote_count", '')) or ''
        },
    }

    def get_images():
        base_url = _tmdb_config().get("images", {}).get("base_url", '')
        if not base_url:
            return {}

        poster = meta.get("poster_path", '')
        if poster:
            poster = "{base_url}/w500{rel_url}".format(base_url=base_url, rel_url=poster)

        fanart = meta.get("backdrop_path", '')
        if fanart:
            fanart = "{base_url}/original{rel_url}".format(base_url=base_url, rel_url=fanart)

        return {
            "icon": poster,
            "thumbnail": poster,
            "properties": {
                "fanart_image": fanart
            }
        }
    item.update(get_images())

    def get_credits():
        credits = meta.get("credits", {})
        if not credits:
            return {}

        castandrole = []
        director = []
        writer = []
 
        for c in credits.get("cast", []):
            castandrole.append(u"{name}|{character}".format(name=c["name"], character=c.get("character", '')))

        for c in credits.get("crew", []):
            if c["job"] == 'Director':
                director.append(c["name"])
                continue
            if c["job"] == 'Novel' or c["job"] == 'Writer' or c["job"] == 'Screenplay':
                writer.append(c["name"])

        return {
            'castandrole': castandrole,
            'director': " / ".join(director),
            'writer': " / ".join(writer)
        }
    item['info'].update(get_credits())

    return item
