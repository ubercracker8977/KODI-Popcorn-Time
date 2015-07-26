#!/usr/bin/python
import os, sys
from urllib import urlretrieve
from zipfile import ZipFile
from kodipopcorntime.caching import CACHE_DIR
from kodipopcorntime.utils import url_get

__addon__ = sys.modules['__main__'].__addon__
provides = 'movies.subtitles'

_subtitles_formats = ['.aqt', '.gsub', '.jss', '.sub', '.ttxt', '.pjs', '.psb', '.rt', '.smi', '.stl', '.ssf', '.srt', '.ssa', '.ass', '.usf', '.idx']

_subtitlelang = [
    None,
    "albanian",
    "arabic",
    "bengali",
    "brazilian-portuguese",
    "bulgarian",
    "chinese",
    "croatian",
    "czech",
    "danish",
    "dutch",
    "english",
    "farsi-persian",
    "finnish",
    "french",
    "german",
    "greek",
    "hebrew",
    "hungarian",
    "indonesian",
    "italian",
    "japanese",
    "korean",
    "lithuanian",
    "macedonian",
    "malay",
    "norwegian",
    "polish",
    "portuguese",
    "romanian",
    "russian",
    "serbian",
    "slovenian",
    "spanish",
    "swedish",
    "thai",
    "turkish",
    "urdu",
    "vietnamese"
]
_subtitle_iso = {
    "None": None,
    "albanian": "sq",
    "arabic": "ar",
    "bengali": "bn",
    "brazilian-portuguese": "pt-br",
    "bulgarian": "bg",
    "chinese": "zh",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "farsi-persian": "fa",
    "finnish": "fi",
    "french": "fr",
    "german": "de",
    "greek": "el",
    "hebrew": "he",
    "hungarian": "hu",
    "indonesian": "id",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "lithuanian": "lt",
    "macedonian": "mk",
    "malay": "ms",
    "norwegian": "no",
    "polish": "pl",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "serbian": "sr",
    "slovenian": "sl",
    "spanish": "es",
    "swedish": "sv",
    "thai": "th",
    "turkish": "tr",
    "urdu": "ur",
    "vietnamese": "vi"
}

def get(id, label, year):
    data = url_get('http://api.yifysubtitles.com', "/subs/"+id).get("subs", {}).get(id)
    if not data:
        return {}

    for l in [_subtitlelang[int(__addon__.getSetting('sub_language1'))], _subtitlelang[int(__addon__.getSetting('sub_language2'))], _subtitlelang[int(__addon__.getSetting('sub_language3'))]]:
        subtitles = data.get(l)
        if not subtitles:
            continue
        subtitle = subtitles.pop(0)
        for s in subtitles:
            hi = s["hi"]
            if __addon__.getSetting("hearing_impaired") == 'true':
                hi = -(s["hi"]-2)
            if s["rating"] <= subtitle["rating"] and hi >= subtitle["hi"] or hi > subtitle["hi"]:
                continue
            subtitle = s

        lang = _subtitle_iso[l]
        return {
            'label': label,
            'subtitle': 'http://www.yifysubtitles.com'+subtitle["url"],
            'stream_info': {
                'subtitle': {
                    'language':  lang
                }
            }
        }
    return {}

def download(url, dirname, filename):
    if int(__addon__.getSetting('sub_language1')) == 0:
        return {}

    cache_path = os.path.join(CACHE_DIR, 'temp.zip')
    try:
        urlretrieve(url, cache_path)
        z = ZipFile(cache_path)
    except:
        return None

    path = None
    for f in z.namelist():
        ext = os.path.splitext(f)[1]
        if not ext in _subtitles_formats:
            continue
        path = os.path.join(dirname, filename+ext)
        z.extract(f, CACHE_DIR)
        if os.path.isfile(path):
            os.unlink(path)
        os.rename(os.path.join(CACHE_DIR, f), path)
        break

    z.close()
    os.unlink(cache_path)
    return path

def remove(path):
    if os.path.splitext(os.path.basename(path))[1] in _subtitles_formats:
        os.unlink(path)
