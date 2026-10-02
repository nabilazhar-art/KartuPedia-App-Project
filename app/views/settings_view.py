"""Layar Pengaturan (menggantikan Tentang): ringkasan statistik, toggle tema,
hapus data (dengan Undo lewat SnackBar), dan info aplikasi singkat.
"""
import flet as ft

from app.config import APP_NAME, APP_VERSION
from app.database import GAME_OBJECTS
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography
from app.async_utils import async_handler


def show_snackbar(page: ft.Page, snackbar: ft.SnackBar):
    """Tampilkan SnackBar dengan cara yang tersedia di versi Flet yang terpasang.

    Cara menampilkan overlay (SnackBar/dialog) sudah berubah antar versi Flet,
    dan belum pernah diuji di Flet asli proyek ini, jadi dicoba berurutan dari
    yang terbaru ke yang lama -- bukan satu cara yang ditebak:
      1) page.show_dialog(...)  -- API terbaru
      2) page.open(...)         -- API versi pertengahan
      3) page.snack_bar = ...   -- API lama
    """
    if hasattr(page, "show_dialog"):
        page.show_dialog(snackbar)
    elif hasattr(page, "open"):
        page.open(snackbar)
    else:
        page.snack_bar = snackbar
        snackbar.open = True
        page.update()


class SettingsScreen:
    def __init__(self, page: ft.Page, storage, mode: str, on_toggle_theme, on_data_changed=None):
        self.page = page
        self.storage = storage
        self.mode = mode
        self.on_toggle_theme = on_toggle_theme      # async, sama persis dgn yg di AppBar
        self.on_data_changed = on_data_changed        # opsional, dipanggil setelah hapus/undo
        self.stat_texts = {}
        self.theme_switch = None

    # ---------- Statistik ----------

    async def _refresh_stats(self):
        c = get_palette(self.mode)
        fav_count = len(await self.storage.get_favorites())
        recent_count = len(await self.storage.get_recently_viewed())
        self.stat_texts["favorit"].value = str(fav_count)
        self.stat_texts["dilihat"].value = str(recent_count)
        self.page.update()

    def _stat_box(self, key: str, value: str, label: str) -> ft.Control:
        c = get_palette(self.mode)
        value_text = ft.Text(value, size=AppTypography.HEADING, weight=ft.FontWeight.BOLD, color=c.TEXT)
        self.stat_texts[key] = value_text
        return ft.Container(
            expand=True,
            bgcolor=c.SURFACE,
            border=ft.Border.all(1, c.BORDER),
            border_radius=AppRadius.MD,
            padding=AppSpacing.SM,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    value_text,
                    ft.Text(label, size=AppTypography.META, color=c.TEXT_MUTED,
                             text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

    # ---------- Tema ----------

    async def _handle_switch_change(self, e):
        await self.on_toggle_theme()

    # ---------- Hapus data + Undo ----------

    def _snackbar(self, message: str, on_undo) -> ft.SnackBar:
        return ft.SnackBar(
            content=ft.Text(message),
            action="Urungkan",
            on_action=on_undo,
            duration=4000,
        )

    async def _refresh_after_change(self):
        """Segarkan tampilan setelah hapus/undo. Kalau AppShell menyediakan
        on_data_changed (merender ulang seluruh tab), pakai itu -- lebih
        lengkap. Kalau tidak, cukup perbarui angka statistik di tempat."""
        if self.on_data_changed:
            await self.on_data_changed()
        else:
            await self._refresh_stats()

    async def _clear_recent(self, e=None):
        backup = await self.storage.get_recently_viewed()
        if not backup:
            return
        await self.storage.clear_recently_viewed()
        await self._refresh_after_change()

        async def undo(ev=None):
            await self.storage.restore_recently_viewed(backup)
            await self._refresh_after_change()

        show_snackbar(self.page, self._snackbar(f"Riwayat dilihat ({len(backup)} game) dihapus.", undo))

    async def _clear_favorites(self, e=None):
        backup = await self.storage.get_favorites()
        if not backup:
            return
        await self.storage.clear_favorites()
        await self._refresh_after_change()

        async def undo(ev=None):
            await self.storage.restore_favorites(backup)
            await self._refresh_after_change()

        show_snackbar(self.page, self._snackbar(f"Favorit ({len(backup)} game) dihapus.", undo))

    def _data_row(self, icon, label: str, on_click) -> ft.Control:
        c = get_palette(self.mode)
        return ft.Container(
            on_click=on_click,
            ink=True,
            border_radius=AppRadius.MD,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.SM, vertical=AppSpacing.SM),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, color=c.ERROR, size=20),
                    ft.Container(width=AppSpacing.SM),
                    ft.Text(label, size=AppTypography.BODY, color=c.TEXT, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=c.TEXT_MUTED, size=18),
                ],
            ),
        )

    # ---------- Bangun konten ----------

    async def build_content(self) -> ft.Control:
        c = get_palette(self.mode)

        stats_row = ft.Row(
            spacing=AppSpacing.SM,
            controls=[
                self._stat_box("total", str(len(GAME_OBJECTS)), "Game"),
                self._stat_box("favorit", "0", "Favorit"),
                self._stat_box("dilihat", "0", "Dilihat"),
            ],
        )

        self.theme_switch = ft.Switch(
            value=(self.mode == "dark"),
            on_change=self._handle_switch_change,
            active_color=c.PRIMARY,
        )

        theme_row = ft.Container(
            bgcolor=c.SURFACE,
            border=ft.Border.all(1, c.BORDER),
            border_radius=AppRadius.MD,
            padding=AppSpacing.SM,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.DARK_MODE_ROUNDED if self.mode == "dark" else ft.Icons.LIGHT_MODE_ROUNDED,
                             color=c.TEXT, size=20),
                    ft.Container(width=AppSpacing.SM),
                    ft.Text("Mode Gelap", size=AppTypography.BODY, color=c.TEXT, expand=True),
                    self.theme_switch,
                ],
            ),
        )

        data_card = ft.Container(
            bgcolor=c.SURFACE,
            border=ft.Border.all(1, c.BORDER),
            border_radius=AppRadius.MD,
            padding=AppSpacing.XS,
            content=ft.Column(
                spacing=0,
                controls=[
                    self._data_row(ft.Icons.HISTORY_ROUNDED, "Hapus Riwayat Dilihat",
                                    async_handler(self._clear_recent)),
                    ft.Divider(color=c.BORDER, height=1),
                    self._data_row(ft.Icons.FAVORITE_BORDER_ROUNDED, "Hapus Semua Favorit",
                                    async_handler(self._clear_favorites)),
                ],
            ),
        )

        info_card = ft.Container(
            bgcolor=c.SURFACE,
            border=ft.Border.all(1, c.BORDER),
            border_radius=AppRadius.MD,
            padding=AppSpacing.SM,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(f"{APP_NAME} versi {APP_VERSION}", size=AppTypography.CAPTION, color=c.TEXT),
                    ft.Text("Ensiklopedia dan panduan permainan kartu.",
                             size=AppTypography.CAPTION, color=c.TEXT_SECONDARY),
                ],
            ),
        )

        def section_label(text: str) -> ft.Control:
            return ft.Text(text, size=AppTypography.SECTION, weight=ft.FontWeight.BOLD, color=c.TEXT)

        content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=AppSpacing.SM,
            controls=[
                ft.Container(height=AppSpacing.XS),
                section_label("Ringkasan"),
                stats_row,
                ft.Container(height=AppSpacing.XS),
                section_label("Tampilan"),
                theme_row,
                ft.Container(height=AppSpacing.XS),
                section_label("Data"),
                data_card,
                ft.Container(height=AppSpacing.XS),
                section_label("Tentang Aplikasi"),
                info_card,
                ft.Container(height=AppSpacing.XXL),
            ],
        )

        await self._refresh_stats()
        return content
