[app]
title = Media Downloader Pro
package.name = mediadownloaderpro
package.domain = com.samsung.downloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Critical core library requirements
requirements = python3, kivy, requests, yt-dlp, hostpython3

# This forces the builder to use raw python source packaging for the backend components
android.pip_dependencies = requests yt-dlp

orientation = portrait
fullscreen = 0

# Android specific configurations
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
