[app]

# (str) Title of your application
title = Laundry

# (str) Package name
package.name = laundry

# (str) Package domain (needed for android/ios packaging)
package.domain = org.laundry

# (str) Source code where the main.py live
source.dir = .

# (str) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,srt

# (list) Application requirements
# PENTING: Ada ffmpeg, openssl, dan libffi
requirements = python3,kivy,ffmpeg,ffmpeg-python,openssl,libffi

# (str) Presplash of the application
# android.presplash_color = #000000

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android NDK API to use.
android.ndk_api = 26

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0

# --- ARSITEKTUR KHUSUS TECNO SPARK ---
# arm64-v8a only biar build cepet & stabil
android.archs = arm64-v8a

[android]
# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0