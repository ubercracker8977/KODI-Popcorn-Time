import xbmc
from kodipopcorntime.common import plugin, cleanDictList
from kodipopcorntime.utils import url_get
from kodipopcorntime.caching import shelf

API_KEY = "57983e31fb435df4df77afb854740ea9"
BASE_URL = "http://api.themoviedb.org/3"
HEADERS = {
    "Referer": BASE_URL,
}

DEFAULT_TTL = 24 * 3600 # 24 hours

def tmdb_config():
    with shelf("com.imdb.conf", DEFAULT_TTL) as conf:
        if not conf:
            try:
                conf.update(url_get("{base_url}/configuration".format(base_url=BASE_URL), params={"api_key": API_KEY}, headers=HEADERS))
            except:
                return dict()
        return dict(conf)
tmdb_config()

def get(id):
    with shelf("com.imdb.{id}".format(id=id), DEFAULT_TTL) as movie:
        if not movie:
            meta = url_get("{base_url}/movie/{id}".format(base_url=BASE_URL, id=id), params={"api_key": API_KEY, "append_to_response": "credits", "language": "en", "include_image_language": "en,null"}, headers=HEADERS)
            if meta.get('status_code'):
                return dict()
            sys_lang = xbmc.getLanguage(xbmc.ISO_639_1)
            if not sys_lang == 'en':
                sys_meta = url_get("{base_url}/movie/{id}".format(base_url=BASE_URL, id=id), params={"api_key": API_KEY, "append_to_response": "credits", "language": sys_lang, "include_image_language": sys_lang}, headers=HEADERS)
                meta.update(cleanDictList(sys_meta))
            movie = _get_list_item(meta)
        return movie

def search(query):
    return url_get("{base_url}/search/movie".format(base_url=BASE_URL), params={"api_key": API_KEY, "query": query, "language": "en"}, headers=HEADERS)


def _get_list_item(meta):
    conf = tmdb_config()

    def get_studio():
        return (first(sorted(meta.get("production_companies", []), key=lambda x: x["id"])) or dict()).get("name") or ""

    return cleanDictList({
        "label": meta.get("title"),
        "icon": meta.get("poster_path") and conf.get("images", dict()).get("base_url") and "{base_url}/w500{rel_url}".format(base_url=conf["images"]["base_url"], rel_url=meta["poster_path"]),
        "thumbnail": meta.get("poster_path") and conf.get("images", dict()).get("base_url") and "{base_url}/w500{rel_url}".format(base_url=conf["images"]["base_url"], rel_url=meta["poster_path"]),
        "info": {
            "title": meta.get("title"),
            "originaltitle": meta.get("original_title"),
            "genre": meta.get("genres") and " / ".join([genre["name"] for genre in meta["genres"]]) or "",
            "plot": meta.get("overview"),
            "plot_outline": meta.get("overview"),
            "tagline": meta.get("tagline"),
            "rating": meta.get("vote_average"),
            "duration": meta.get("runtime", 0),
            "code": meta.get("imdb_id"),
            "cast": [cast["name"] for cast in (meta.get("credits", dict()).get("cast", []))],
            "director": [crew["name"] for crew in (meta.get("credits", dict()).get("crew", [])) if crew["job"] == 'Director'],
            "writer": [crew["name"] for crew in (meta.get("credits", dict()).get("crew", [])) if crew["job"] == 'Writer'] or [crew["name"] for crew in (meta.get("credits", dict()).get("crew", [])) if crew["job"] == 'Novel'] or [crew["name"] for crew in (meta.get("credits", dict()).get("crew", [])) if crew["job"] == 'Screenplay'],
            "studio": get_studio(),
            "year": meta.get("release_date") and meta["release_date"].split("-")[0] or ""
        },
        "properties": {
            "fanart_image": meta.get("backdrop_path") and conf.get("images", dict()).get("base_url") and "{base_url}/original{rel_url}".format(base_url=conf["images"]["base_url"], rel_url=meta["backdrop_path"])
        }
    })
