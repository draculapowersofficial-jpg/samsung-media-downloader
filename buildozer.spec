[app]
title = Universal Media Downloader
package.name = unimediadownloader
package.domain = org.mymediaapp
source.dir = .
source.include_exts = py,png,jpg
version = 1.0.0

# Pin down standard cross-platform libraries
requirements = python3,kivy==2.3.0,yt-dlp,certifi,openssl

orientation = portrait
fullscreen = 1

# Permission required to pull video links online
android.permissions = INTERNET

# STABILITY FIX: Force stable Android SDK & NDK versions to prevent compiler link mismatch
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Optimize architecture for modern 64-bit devices like your Samsung A06
android.archs = arm64-v8a

android.accept_sdk_license = True
