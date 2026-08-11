[app]
title = Universal Media Downloader
package.name = unimediadownloader
package.domain = org.mymediaapp
source.dir = .
source.include_exts = py,png,jpg
version = 1.0.0

# Fixed versioning dependencies for stability
requirements = python3,kivy==2.3.0,yt-dlp,certifi,openssl

orientation = portrait
fullscreen = 1

# Permission required to pull video links online
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk_api = 21

# CRITICAL FIX: Only compile for modern 64-bit devices like your Samsung A06
# This stops the server from crashing due to running out of memory
android.archs = arm64-v8a

android.accept_sdk_license = True
