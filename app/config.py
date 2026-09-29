"""Konfigurasi aplikasi KartuPedia: identitas dan path data."""
import os

APP_NAME = "KartuPedia"
APP_TAGLINE = "Your Guide to Card Games"
APP_VERSION = "2.0.0"  # dinaikkan: versi Flet, desain baru

# Root proyek = satu tingkat di atas folder paket "app".
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")

# Ukuran jendela default saat aplikasi dijalankan di desktop.
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 860

# Pemutar video tutorial di dalam aplikasi (WebView, package flet-webview-all).
# Extension ini baru aktif kalau sudah dikompilasi ke dalam aplikasi lewat
# `flet build` (apk / windows / web). Di `flet run` (termasuk --web dan
# --android) klien bawaan Flet TIDAK menyertakannya -> "Unknown control".
#   "auto" : WebView hanya dipakai di aplikasi hasil build (terdeteksi otomatis)
#   "on"   : paksa pakai WebView (mis. setelah build klien sendiri)
#   "off"  : selalu pakai tampilan cadangan (thumbnail + tombol YouTube)
INAPP_VIDEO_MODE = "auto"
