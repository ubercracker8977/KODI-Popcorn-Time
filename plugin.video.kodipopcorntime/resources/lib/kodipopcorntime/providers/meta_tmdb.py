from kodipopcorntime.utils import url_get
from kodipopcorntime.caching import shelf
                conf.update(url_get("{base_url}/configuration".format(base_url=BASE_URL), params={"api_key": API_KEY}, headers=HEADERS))
            meta = url_get("{base_url}/movie/{id}".format(base_url=BASE_URL, id=id), params={"api_key": API_KEY, "append_to_response": "credits", "language": "en", "include_image_language": "en,null"}, headers=HEADERS)
                sys_meta = url_get("{base_url}/movie/{id}".format(base_url=BASE_URL, id=id), params={"api_key": API_KEY, "append_to_response": "credits", "language": sys_lang, "include_image_language": sys_lang}, headers=HEADERS)
    return url_get("{base_url}/search/movie".format(base_url=BASE_URL), params={"api_key": API_KEY, "query": query, "language": "en"}, headers=HEADERS)
