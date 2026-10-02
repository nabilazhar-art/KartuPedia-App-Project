"""Penyimpanan lokal untuk favorit, riwayat dilihat, dan preferensi tema.

Versi Kivy menyimpan semuanya manual ke file kartupedia_data.json, termasuk
kode khusus path Android yang sebenarnya tidak pernah benar-benar dipakai.
Versi Flet ini memakai ft.SharedPreferences() (service penyimpanan key-value
bawaan Flet): di desktop otomatis disimpan sebagai file JSON oleh Flet
sendiri, di web jadi localStorage, di Android/iOS jadi SharedPreferences/
NSUserDefaults asli -- semua lewat satu API yang sama, tanpa perlu kode
per-platform.

Catatan versi: sempat dicoba lewat page.shared_preferences (shortcut yang
disebut di sebagian dokumentasi Flet), tapi ternyata tidak ada di versi Flet
yang terpasang -> dipakai ft.SharedPreferences() langsung, yang merupakan
cara resmi lain untuk mengakses service yang sama persis.

Semua method di sini async karena SharedPreferences memang async.
"""
import flet as ft

# Prefix pada semua key, praktik yang disarankan Flet supaya tidak bentrok
# dengan aplikasi Flet lain yang kebetulan dijalankan client yang sama.
_PREFIX = "kartupedia."
FAVORITES_KEY = _PREFIX + "favorites"
RECENT_KEY = _PREFIX + "recently_viewed"
THEME_KEY = _PREFIX + "theme_mode"

MAX_RECENTLY_VIEWED = 5


class Storage:
    """Wrapper tipis di atas ft.SharedPreferences(), khusus data KartuPedia."""

    def __init__(self, page: ft.Page):
        # page disimpan untuk kebutuhan lain di masa depan (mis. snackbar),
        # tidak dipakai langsung oleh SharedPreferences.
        self.page = page
        self._prefs = ft.SharedPreferences()
        # Cache di memori: data dibaca dari SharedPreferences sekali saja, lalu
        # semua pembacaan berikutnya langsung dari memori (tanpa bolak-balik ke
        # klien Flutter). Penulisan tetap diteruskan ke SharedPreferences, jadi
        # format data yang tersimpan tidak berubah.
        self._favs_cache = None
        self._recent_cache = None
        # Naik setiap kali favorit berubah; dipakai shell untuk tahu apakah tab
        # Favorit perlu dibangun ulang setelah kembali dari layar lain.
        self.favs_version = 0

    # ---------- Favorit ----------

    async def get_favorites(self) -> list:
        if self._favs_cache is None:
            favs = await self._prefs.get(FAVORITES_KEY)
            self._favs_cache = list(favs) if favs else []
        return list(self._favs_cache)

    async def _save_favorites(self, favs: list):
        self._favs_cache = list(favs)
        self.favs_version += 1
        await self._prefs.set(FAVORITES_KEY, list(favs))

    async def is_favorite(self, game_id: str) -> bool:
        return game_id in await self.get_favorites()

    async def toggle_favorite(self, game_id: str) -> bool:
        """Tambah/hapus dari favorit. Return True kalau sekarang jadi favorit."""
        favs = await self.get_favorites()
        if game_id in favs:
            favs.remove(game_id)
            is_fav = False
        else:
            favs.append(game_id)
            is_fav = True
        await self._save_favorites(favs)
        return is_fav

    async def clear_favorites(self):
        await self._save_favorites([])

    async def restore_favorites(self, ids: list):
        """Dipakai tombol Undo di Pengaturan setelah 'Hapus Semua Favorit'."""
        await self._save_favorites(list(ids))

    # ---------- Baru dilihat ----------

    async def get_recently_viewed(self) -> list:
        if self._recent_cache is None:
            recent = await self._prefs.get(RECENT_KEY)
            self._recent_cache = list(recent) if recent else []
        return list(self._recent_cache)

    async def _save_recent(self, recent: list):
        self._recent_cache = list(recent)
        await self._prefs.set(RECENT_KEY, list(recent))

    async def add_recently_viewed(self, game_id: str):
        recent = await self.get_recently_viewed()
        if game_id in recent:
            recent.remove(game_id)
        recent.insert(0, game_id)
        del recent[MAX_RECENTLY_VIEWED:]
        await self._save_recent(recent)

    async def clear_recently_viewed(self):
        await self._save_recent([])

    async def restore_recently_viewed(self, ids: list):
        """Dipakai tombol Undo di Pengaturan setelah 'Hapus Riwayat Dilihat'."""
        await self._save_recent(list(ids))

    # ---------- Preferensi tema (dark/light) ----------

    async def get_theme_mode(self) -> str:
        mode = await self._prefs.get(THEME_KEY)
        return mode if mode in ("dark", "light") else "dark"

    async def set_theme_mode(self, mode: str):
        await self._prefs.set(THEME_KEY, mode)
