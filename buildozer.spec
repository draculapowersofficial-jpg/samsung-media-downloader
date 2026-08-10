[app]
title = Media Downloader Pro
package.name = mediadownloaderpro
package.domain = com.samsung.downloader
source.dir = .
source.include_exts = py,html,css
version = 1.0

# Using a standard web view framework instead of Kivy
requirements = python3, hostpython3, flask, requests, yt-dlp

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
