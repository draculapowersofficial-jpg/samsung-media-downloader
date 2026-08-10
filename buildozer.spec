[app]
title = Media Downloader Pro
package.name = mediadownloaderpro
package.domain = com.samsung.downloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Explicitly maps python3 and core mobile graphics frameworks
requirements = python3, kivy==2.3.0, hostpython3, requests, yt-dlp

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
