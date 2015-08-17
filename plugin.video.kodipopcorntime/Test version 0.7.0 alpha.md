KODI Popcorn Time
===========

Test the new 0.7.0 alpha version
----------
1. To test the Alpha release you need to download the source code from [master branch](https://github.com/Diblo/KODI-Popcorn-Time/tree/master/plugin.video.kodipopcorntime) and 'torrent2http-x.x.x.zip' file from [torrent2http](https://github.com/anteo/torrent2http/releases)
2. Copy torrent2http's folders to the bin folder
3. Make a zip file and install


Warning!
----------
This is the first Alpha release, and not all work is done!


Great deal of new things
----------
- [x] New and more icons
- [x] New and improved setting possibilities (You will love it!)
- [x] Has become ready to integrate TV series provider
- [ ] Writing provider to TV series (metadata and subtitles included)
- [ ] Search
- [ ] Search in more languages than English
- [x] Setting: Preferred video quality
- [x] Setting: Download and upload rate limit
- [x] Setting: Prioritize hearing impaired subtitles
- [x] Setting: Ability to add more proxy domains at once
- [x] Integrated proxy domains
- [ ] Better cache cleanup
- [x] New and better torrent2http provider (https://github.com/anteo/torrent2http)
- [x] Several modules have been removed
- [x] Tuning and optimization
- [x] New structure
- [ ] Do not show the loading window, when there is a cache


What it is
----------
With KODI Popcorn Time you can search for movies that you can see immediately in KODI.


Download
--------
Check out http://github.com/Diblo/KODI-Popcorn-Time/releases to download the ZIP file.


Supported Platforms
-------------------
* Helix 14.x (KODI)
* Gotham 13.x (XBMC)
* Windows x32 and x64
* OSX x32 and x64
* Linux x32, x64 and ARM
* Android ARM
* Darwin x64
* Raspberry Pi

How it works
------------
KODI Popcorn Time is actually two parts:
* KODI Popcorn Time: the add-on written in Python.
* torrent2http: a custom torrent client that turns magnet links into HTTP endpoints, using sequential download.


Discussions
------------
There is one active threads on http://forums.tvaddons.ag/threads/32586-KODI-Popcorn-Time?p=271031.


Credits
-----------
* https://github.com/anteo/torrent2http
* https://github.com/anteo/script.module.torrent2http
* https://github.com/jbeluch/xbmcswift2


Issues
-----------
Please, file an issue :) - http://github.com/Diblo/KODI-Popcorn-Time/issues


Changelog
---------
Check out http://github.com/Diblo/KODI-Popcorn-Time/releases.


## FAQ ##
---------------------------------------
### I can't code. How can I help? ###
Spread the word. Talk about it with your friends, show them, make videos, tutorials. Talk about it on social networks, blogs etc...

### The plug-in doesn't work at all, what can I do? ###
Post your issue at http://github.com/Diblo/KODI-Popcorn-Time/issues with your kodi.log.

### Can it stream HD? ###
Of course! 720p, 1080p and 3D work fine, provided you have enough bandwidth, and there are enough people on the torrent.

### Does it supports subtitles? ###
Of course! It will always download the proper subtitle of the film, if there is one. It is also possible to use KODI to search for the subtitle in the absence of a subtitle.

### Does it downloads the whole file? Do I need the space? Is it ever deleted?
Yes and yes. KODI Popcorn Time will pre-allocate the whole file before download. So if you want to watch a 4GB video, you'll need the 4GB. The file is deleted once you stop watching it.

### Where is the file located? Can I change it? ###
The torrent files are located in "/cache" in the user data directory or "resources/bin/<OS>/" in the add-on directory. Yes of course, just changes the path in the add-on settings.

### Can I keep the file after playback? ###
Yes, just enable this option in the add-on settings.

### Can I set it to download directly to my NAS and keep it after playback? ###
Yes of course. Just set the download directly to your NAS location, and make sure you have enabled "Keep files after playback" option.

### What about seeding? ###
KODI Popcorn Time will seed the file you're watching until it's finished playing. For instance, if the download of a 2 hours long movie is finished in 10 minutes, you'll continue seeding it until you finish watching the movie. This is by design, to make up for the fact that we are using sequential download.

[![Analytics](https://ga-beacon.appspot.com/UA-63872919-1/KODI-Popcorn-Time/Test_the_new_0.7.0_alpha_version)](https://github.com/igrigorik/ga-beacon)
