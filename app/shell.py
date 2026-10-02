"""Shell aplikasi: AppBar + NavigationBar (Beranda/Jelajah/Favorit/Pengaturan)
di level page (persisten), dengan area konten yang berganti sesuai tab aktif.

page.navigation_bar & page.appbar dipasang SEKALI di level page (bukan per
ft.View) -- ini pola resmi Flet untuk navigasi tab yang persisten. Rute "/"
di page.views hanya berisi wadah konten (content_area) yang isinya ditukar
saat pindah tab. Layar "tarik turun" (Detail Game, Game Finder, Random,
Filter, Tutorial) memakai page.views.append(...) terpisah, dgn tombol back.
"""
import flet as ft

from app.config import APP_NAME
from app.database import GAME_OBJECTS, get_game_by_id
from app.theme import get_palette, AppSpacing, AppTypography
from app.utils import filter_games
from app.views.home_view import build_home_view, fill_recent_section
from app.views.explore_view import build_explore_shell, build_chip_row, build_results_list
from app.views.filter_screen import FilterScreen
from app.views.favorite_view import build_favorite_view
from app.views.settings_view import SettingsScreen
from app.views.detail_view import DetailScreen
from app.views.tutorial_player_view import build_tutorial_player_view
from app.views.finder_view import FinderScreen
from app.views.random_view import RandomScreen

TABS = ["home", "explore", "favorite", "settings"]
TAB_TITLES = {"home": APP_NAME, "explore": "Jelajah", "favorite": "Favorit", "settings": "Pengaturan"}


class AppShell:
    """Menyimpan state tab aktif & merender ulang chrome/isi saat tab atau tema berubah."""

    def __init__(self, page: ft.Page, storage):
        self.page = page
        self.storage = storage
        self.tab = "home"
        self.content_area = ft.Container(expand=True)
        # Wadah "Baru Dilihat" persisten + penanda versi favorit yang terakhir
        # dirender, supaya tombol kembali tidak perlu membangun ulang seluruh tab.
        self.home_recent_holder = ft.Column(spacing=0)
        self._fav_version_rendered = -1

        # State Jelajah (bertahan selama app hidup, sama seperti Screen instance
        # di versi Kivy yang menyimpan state-nya sendiri).
        self.explore_query = ""
        self.explore_category = None
        self.explore_filters = {"players": set(), "duration": set(), "difficulty": set(), "category": set()}
        # Dua wadah ini di-reuse (bukan dibangun ulang) supaya search field
        # tidak kehilangan fokus tiap kali user mengetik satu huruf.
        self.explore_results_container = ft.Container(expand=True)
        self.explore_chip_container = ft.Container()

    def mode(self) -> str:
        return "dark" if self.page.theme_mode == ft.ThemeMode.DARK else "light"

    # ---------- Siklus render ----------

    async def mount(self):
        """Dipanggil sekali di awal (dari main.py) untuk memasang shell pertama kali."""
        self.page.views.clear()
        self.page.views.append(ft.View(route="/", padding=0, controls=[self.content_area]))
        self.page.on_view_pop = self._handle_view_pop
        await self._render_chrome()
        await self._render_tab()

    async def _render_chrome(self):
        c = get_palette(self.mode())
        self.page.bgcolor = c.BG
        self.page.appbar = ft.AppBar(
            title=ft.Text(TAB_TITLES[self.tab], color=c.TEXT, weight=ft.FontWeight.BOLD),
            bgcolor=c.SURFACE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE_ROUNDED if self.mode() == "light" else ft.Icons.LIGHT_MODE_ROUNDED,
                    icon_color=c.TEXT,
                    tooltip="Ganti tema",
                    on_click=self.toggle_theme,
                ),
            ],
        )
        self.page.navigation_bar = ft.NavigationBar(
            selected_index=TABS.index(self.tab),
            bgcolor=c.SURFACE,
            on_change=self.switch_tab,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME_ROUNDED, label="Beranda"),
                ft.NavigationBarDestination(icon=ft.Icons.SEARCH_OUTLINED, selected_icon=ft.Icons.SEARCH_ROUNDED, label="Jelajah"),
                ft.NavigationBarDestination(icon=ft.Icons.FAVORITE_BORDER_ROUNDED, selected_icon=ft.Icons.FAVORITE_ROUNDED, label="Favorit"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS_ROUNDED, label="Pengaturan"),
            ],
        )
        self.page.update()

    async def _render_tab(self):
        c = get_palette(self.mode())
        self.content_area.bgcolor = c.BG
        self.content_area.padding = ft.Padding.symmetric(horizontal=AppSpacing.LG, vertical=AppSpacing.XS)
        self.content_area.content = await self._build_tab_content()
        self.page.update()

    async def _build_tab_content(self) -> ft.Control:
        if self.tab == "home":
            return await build_home_view(
                self.storage, self.mode(),
                on_open_game=self.open_game,
                on_open_finder=self.open_finder,
                on_open_random=self.open_random,
                on_open_category=self.open_category,
                on_see_all_popular=self.see_all_popular,
                recent_holder=self.home_recent_holder,
            )
        if self.tab == "explore":
            return self._build_explore_content()
        if self.tab == "favorite":
            self._fav_version_rendered = self.storage.favs_version
            return await build_favorite_view(
                self.storage, self.mode(),
                on_open_game=self.open_game,
                on_go_explore=self.see_all_popular,
            )
        if self.tab == "settings":
            screen = SettingsScreen(
                self.page, self.storage, self.mode(),
                on_toggle_theme=self.toggle_theme,
                on_data_changed=self._render_tab,
            )
            return await screen.build_content()
        return ft.Container()  # tidak akan tercapai; TABS sudah mencakup semua

    # ---------- Aksi umum ----------

    async def toggle_theme(self, e=None):
        new_mode = "light" if self.mode() == "dark" else "dark"
        self.page.theme_mode = ft.ThemeMode.DARK if new_mode == "dark" else ft.ThemeMode.LIGHT
        await self.storage.set_theme_mode(new_mode)
        await self._render_chrome()
        await self._render_tab()

    async def switch_tab(self, e):
        self.tab = TABS[e.control.selected_index]
        await self._render_chrome()
        await self._render_tab()

    async def see_all_popular(self, e=None):
        self.tab = "explore"
        await self._render_chrome()
        await self._render_tab()

    # ---------- Jelajah: search & filter ----------

    def _build_explore_content(self) -> ft.Control:
        self._refresh_explore_chips()
        self._refresh_explore_results()
        return build_explore_shell(
            self.mode(), self.explore_query,
            results_container=self.explore_results_container,
            chip_container=self.explore_chip_container,
            on_search_change=self._on_search_change,
            on_open_filter=self.open_filter,
        )

    def _refresh_explore_chips(self):
        self.explore_chip_container.content = build_chip_row(
            self.mode(), self.explore_category, self._toggle_category
        )

    def _refresh_explore_results(self):
        categories = set(self.explore_filters.get("category", set()))
        if self.explore_category:
            categories.add(self.explore_category)
        results = filter_games(
            GAME_OBJECTS, query=self.explore_query,
            categories=categories or None,
            player_buckets=self.explore_filters.get("players") or None,
            duration_buckets=self.explore_filters.get("duration") or None,
            difficulties=self.explore_filters.get("difficulty") or None,
        )
        self.explore_results_container.content = build_results_list(
            results, self.mode(), on_open_game=self.open_game
        )

    async def _on_search_change(self, e):
        # Hanya perbarui wadah hasil, TIDAK memanggil _render_tab() -- kalau
        # seluruh tab dibangun ulang (termasuk search field-nya), search field
        # akan kehilangan fokus keyboard tiap kali user mengetik satu huruf.
        self.explore_query = e.control.value
        self._refresh_explore_results()
        self.page.update()

    def _toggle_category(self, category: str):
        self.explore_category = None if self.explore_category == category else category
        self._refresh_explore_chips()
        self._refresh_explore_results()
        self.page.update()

    async def open_category(self, category: str):
        """Dipanggil dari chip kategori di Beranda -> pindah ke tab Jelajah
        dgn kategori itu langsung aktif."""
        self.tab = "explore"
        self.explore_category = category
        await self._render_chrome()
        await self._render_tab()

    async def open_filter(self):
        def handle_apply(selected: dict):
            self.explore_filters = selected
            self._refresh_explore_results()
            self.page.update()

        async def handle_close(e=None):
            await self._pop_view(e)

        screen = FilterScreen(self.page, self.mode(), self.explore_filters, handle_apply, handle_close)
        self.page.views.append(screen.build_view())
        self.page.update()

    # ---------- Layar info/error singkat (game tidak ditemukan, dsb) ----------

    async def _push_message_screen(self, title: str, message: str):
        c = get_palette(self.mode())
        self.page.views.append(
            ft.View(
                route=f"/message/{len(self.page.views)}",
                bgcolor=c.BG,
                appbar=ft.AppBar(
                    title=ft.Text(title, color=c.TEXT),
                    bgcolor=c.SURFACE,
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=c.TEXT,
                        on_click=self._pop_view,
                    ),
                ),
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        padding=AppSpacing.LG,
                        content=ft.Text(
                            message,
                            color=c.TEXT_SECONDARY, size=AppTypography.BODY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    )
                ],
            )
        )
        self.page.update()

    async def open_game(self, game_id: str):
        # Penahan ketukan ganda: selama satu layar detail sedang dibuka,
        # ketukan berikutnya diabaikan (mencegah detail terbuka dua kali).
        if getattr(self, "_opening_game", False):
            return
        self._opening_game = True
        try:
            await self._open_game(game_id)
        finally:
            self._opening_game = False

    async def _open_game(self, game_id: str):
        game = get_game_by_id(game_id)
        if not game:
            await self._push_message_screen(
                "Game tidak ditemukan",
                f"Game dengan id \"{game_id}\" tidak ada di database.",
            )
            return
        screen = DetailScreen(self.page, self.storage, self.mode(), game,
                              on_close=self._pop_view, on_open_tutorial=self.open_tutorial)
        view = await screen.build_view()
        self.page.views.append(view)
        self.page.update()
        # Isi detail dimuat bertahap setelah layar tampil (kurangi lag).
        self.page.run_task(screen.populate)

    async def open_tutorial(self, game_id: str):
        game = get_game_by_id(game_id)
        if not game or not game.tutorial_url:
            await self._push_message_screen(
                "Tutorial",
                "Game ini belum memiliki video tutorial.",
            )
            return
        self.page.views.append(build_tutorial_player_view(self.mode(), game, on_close=self._pop_view))
        self.page.update()

    async def open_finder(self):
        screen = FinderScreen(self.page, self.mode(), on_open_game=self.open_game,
                              on_close=self._pop_view)
        self.page.views.append(screen.build_view())
        self.page.update()

    async def open_random(self):
        screen = RandomScreen(self.page, self.mode(), on_open_game=self.open_game,
                               on_close=self._pop_view)
        self.page.views.append(screen.build_view())
        self.page.update()

    async def _handle_view_pop(self, e):
        await self._pop_view(e)

    async def _pop_view(self, e):
        if len(self.page.views) > 1:
            self.page.views.pop()
            # Perbarui HANYA yang memang berubah, lalu satu kali page.update():
            #  - Beranda: cukup bagian "Baru Dilihat"
            #  - Favorit: dibangun ulang hanya kalau daftar favorit berubah
            #  - Jelajah/Pengaturan: tidak perlu (state-nya tidak berubah di layar lain)
            if self.tab == "home":
                recent_ids = await self.storage.get_recently_viewed()
                games = [g for g in (get_game_by_id(i) for i in recent_ids) if g]
                fill_recent_section(self.home_recent_holder, games, self.mode(),
                                    self.open_game)
            elif self.tab == "favorite" and self._fav_version_rendered != self.storage.favs_version:
                self.content_area.content = await self._build_tab_content()
            self.page.update()
