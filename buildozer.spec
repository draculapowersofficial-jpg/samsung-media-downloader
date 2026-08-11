[app]
title = Universal Media Downloader
package.name = unimediadownloader
package.domain = org.mymediaapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Dependencies needed inside the app
requirements = python3,kivy==2.3.0,yt-dlp,certifi,openssl

orientation = portrait
fullscreen = 1

# Permission required to pull video links online
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk_api = 21

android.accept_sdk_license = True
