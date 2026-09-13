[app]
title = Turbo Racer
package.name = turboracer
package.domain = org.turboracer
source.dir = .
source.include_exts = py,wav,txt,ttf,png,jpg,jpeg,json
version = 1.0
requirements = python3,pygame
orientation = portrait
fullscreen = 1

# Keep the original entry point.
entrypoint = bagui.py
icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
