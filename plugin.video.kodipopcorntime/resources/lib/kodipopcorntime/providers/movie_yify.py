from os import path
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlsplit as urlparse
from kodipopcorntime.common import plugin, RESOURCES_PATH, AnErrorOccurred
from kodipopcorntime.proxy import update_proxies, set_default_proxy
from kodipopcorntime.utils import url_get

INDEX = {
    "label": '',
    "icon": '',
    "thumbnail": '',
    "properties": {
        "fanart_image": ''
    }
}
GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "Game-Show",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western",
]
PROXY_IDENTIFIER = 'movie.yify'

def getURLS():
    # Default domain list
    urls = [
        "http://yts.to",
        "http://eqwww.image.yt"
    ]

    # Evaluate user domain
    userURL = urlparse(plugin.get_setting("base_yify"))
    if not userURL.scheme or not userURL.netloc:
        return urls

    fUserURL = "{url.scheme}://{url.netloc}".format(url=userURL)
    # Prioritize user domain
    if fUserURL in urls:
        urls.remove(fUserURL)
    urls.insert(0, fUserURL)

    return urls

def list(**kwargs):
    if kwargs['item'] == 'genres':
        items= []
        for i, genre in enumerate(GENRES):
            items.append({
                "label": plugin.addon.getLocalizedString((30400 + i)),
                "kodipopcorn_endpoint": "browse",
                "kodipopcorn_items": {
                    'item': "genre",
                    'genre': v
                }
            }
        return items

    return [
        {
            "label": plugin.addon.getLocalizedString(30002),
            "icon": path.join(RESOURCES_PATH, 'media', 'Search.png'),
            "thumbnail": path.join(RESOURCES_PATH, 'media', 'Search.png'),
            "kodipopcorn_endpoint": "search"
        },
        {
            "label": plugin.addon.getLocalizedString(30003),
            "icon": path.join(RESOURCES_PATH, 'media', 'Genres.png'),
            "thumbnail": path.join(RESOURCES_PATH, 'media', 'Genres.png'),
            "kodipopcorn_endpoint": "list",
            "kodipopcorn_kwargs": {
                'item': "genres"
            }
        },
        {
            "label": plugin.addon.getLocalizedString(30004),
            "icon": path.join(RESOURCES_PATH, 'media', 'Top.png'),
            "thumbnail": path.join(RESOURCES_PATH, 'media', 'Top.png'),
            "kodipopcorn_endpoint": "browse",
            "kodipopcorn_kwargs": {
                'item': "seeds",
                'page': 1
            }
        },
        {
            "label": plugin.addon.getLocalizedString(30005),
            "icon": path.join(RESOURCES_PATH, 'media', 'Top.png'),
            "thumbnail": path.join(RESOURCES_PATH, 'media', 'Top.png'),
            "kodipopcorn_endpoint": "browse",
            "kodipopcorn_kwargs": {
                'item': "rating",
                'page': 1
            }
        },
        {
            "label": plugin.addon.getLocalizedString(30006),
            "icon": path.join(RESOURCES_PATH, 'media', 'Recently.png'),
            "thumbnail": path.join(RESOURCES_PATH, 'media', 'Recently.png'),
            "kodipopcorn_endpoint": "browse",
            "kodipopcorn_kwargs": {
                'item': "date",
                'page': 1
            }
        }
    ]

def search_show_data():
    plugin.set_content("movies")
    args = dict((k, v[0]) for k, v in plugin.request.args.items())

    current_page = int(args["page"])
    limit = int(args["limit"])

    with closing(SafeDialogProgress(delay_close=0)) as dialog:
        dialog.create(plugin.name)
        dialog.update(percent=0, line1=plugin.addon.getLocalizedString(30007), line2="", line3="")

        try:
            search_result = tmdb.search(args[query])
        except:
            pass

        if not movies:
            if callback == "search_query":
                yield {
                        "label": plugin.addon.getLocalizedString(30008),
                        "icon": path.join(RESOURCES_PATH, 'icons', 'Search.png'),
                        "thumbnail": path.join(RESOURCES_PATH, 'icons', 'Search.png'),
                        "path": plugin.url_for("search")
                    }
            return

        state = {"done": 0}
        def on_movie(future):
            data = future.result()
            state["done"] += 1
            dialog.update(
                percent=int(state["done"] * 100.0 / len(movies)),
                line2=data.get("title") or data.get("MovieTitleClean") or "",
            )

        with futures.ThreadPoolExecutor(max_workers=2) as pool_tmdb:
            tmdb_list = [pool_tmdb.submit(tmdb.get, movie["imdb_code"]) for movie in movies]
            [future.add_done_callback(on_movie) for future in tmdb_list]
            while not all(job.done() for job in tmdb_list):
                if dialog.iscanceled():
                    return
                xbmc.sleep(100)

        tmdb_list = map(lambda job: job.result(), tmdb_list)
        for movie, tmdb_meta in izip(movies, tmdb_list):
            if tmdb_meta:
                sub = yifysubs.get_sub_items(movie["imdb_code"])
                if sub == None:
                    sub = ["none", ""]

                item = tmdb.get_list_item(tmdb_meta)
                for torrent in movie["torrents"]:
                    if args.get("quality") == "all" and torrent["quality"] != "720p":
                        item["label"] = "%s (%s)" % (item["label"], torrent["quality"])

                    if item.get("info", {}).get("duration") == 0:
                        item["info"]["duration"] = movie["runtime"]

                    item.update({
                        "path": plugin.url_for("play", sub=sub[0], uri=from_meta_data(torrent["hash"], movie["title_long"], torrent["quality"])),
                        "is_playable": True,
                    })

                    item.setdefault("info", {}).update({
                        "code": movie["imdb_code"],
                        "size": torrent["size_bytes"],
                    })

                    width = 1920
                    height = 1080
                    if torrent["quality"] == "720p":
                        width = 1280
                        height = 720
                    item.setdefault("stream_info", {}).update({
                        "video": {
                            "codec": "h264",
                            "width": width,
                            "height": height,
                        },
                        "audio": {
                            "codec": "aac",
                            "language": "en",
                        },
                        "subtitle": {
                            "language": sub[1],
                        },
                    })

                    yield item

        if current_page < (movie_count / limit):
            next_args = args.copy()
            next_args["page"] = int(next_args["page"]) + 1
            yield {
                "label": plugin.addon.getLocalizedString(30009),
                "path": plugin.url_for("search_query", **next_args),
            }

def browse(item, page, **kwargs):
    params = {
        'limit': kwargs['limit'],
        'page': page,
        'quality': kwargs['quality'],
        'genre': item == "genre" and item or 'all',
        'sort_by': item == "genre" and "seeds" or item,
        'order_by': 'desc',
    }
    for proxy in update_proxies(PROXY_IDENTIFIER, getURLS()): # Update proxy list if there is any changes
        try:
            search_result = url_get("{proxy}/api/v2/list_movies.json".format(proxy=proxy), params=params, headers={"Referer": proxy})
            # Prioritizes the last known domain that did work
            set_default_proxy(PROXY_ID, proxy)
            break
        except:
            pass
    if not search_result:
        raise AnErrorOccurred(30304)

    movies = search_result.get("data", {}).get("movies")
    if not movies:
        raise AnErrorOccurred(30305)

    items = []
    for movie in movies:
        if not movie.get("title") or not movie.get("imdb_code"):
            continue

        for torrent in movie["torrents"]:
            if not torrent.get("hash") or not torrent.get("quality"):
                continue

            width = 1920
            height = 1080
            if torrent["quality"] == "720p":
                width = 1280
                height = 720

            items.append({
                "label": movie["title"],
                "icon": movie.get("medium_cover_image", movie.get("small_cover_image", '')),
                "thumbnail": movie.get("medium_cover_image", movie.get("small_cover_image", '')),
                "kodipopcorn_hash": torrent["hash"],
                "kodipopcorn_quality": torrent["quality"],
                "info": {
                    "title": movie["title"],
                    "genre": movie.get("genres") and " / ".join([genre for genre in movie["genres"]]) or "",
                    "duration": movie.get("runtime", 0),
                    "code": movie["imdb_code"],
                    "size": torrent.get("size_bytes", 0),
                    "year": movie.get("year", '')
                },
                "properties": {
                    "fanart_image": movie.get("background_image", '')
                },
                "stream_info": {
                    "video": {
                        "codec": "h264",
                        "width": width,
                        "height": height
                    },
                    "audio": {
                        "codec": "aac",
                        "language": "en"
                    }
                }
            })

    if items:
        return items
    raise AnErrorOccurred(30307)

def search_query(provider, item, query, page, **kwargs):
    kwargs.update({
        "provider": provider,
        "item": item,
        "query": query,
        "page": page,
    })
    return show_data(**kwargs)