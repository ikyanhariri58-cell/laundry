[app]
title = Laundry
package.name = laundry
package.domain = org.laundry
source.dir = .

# PENTING: Kita masukin file 'ffmpeg' ke dalam APK
source.include_patterns = assets/*,images/*,*.png,*.jpg,*.kv,*.atlas,*.srt,ffmpeg,*.py

# Versi aplikasi
version = 1.0

# REQUIREMENTS DIET KETAT:
# Hapus ffmpeg/ffmpeg-python. Cuma butuh Python & Kivy.
requirements = python3,kivy

# Izin Akses
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Versi Android
android.api = 33
android.minapi = 24
android.ndk_api = 26

# Output
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 0
android.archs = arm64-v8a

[android]
fullscreen = 0
