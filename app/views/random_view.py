"""Layar Random Game: pilih beberapa game acak (default 3), dengan filter
kategori opsional.

Di versi Kivy, filter kategori sebenarnya tidak pernah aktif (variabel
random_filters tidak pernah diisi) -- di sini dijadikan fitur sungguhan lewat
chip kategori, sesuai yang sudah disepakati di perencanaan Batch F5.

Auto-mengacak sekali saat layar pertama kali dibuka (meneruskan perilaku
on_pre_enter di Kivy: kalau belum ada game terpilih, langsung acak).
"""
import random

import flet as ft

from app.async_utils import async_handler
from app.database import GAME_OBJECTS, CATEGORIES
from app.components.game_card import game_list_tile
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography

RANDOM_RESULT_COUNT = 3


class RandomScreen:
    def __init__(self, page: ft.Page, mode: str, on_open_game, on_close):
        self.page = page
        self.mode = mode
        self.on_open_game = on_open_game   # async, menerima game_id
        self.on_close = on_close           # async, tombol back
        self.selected_categories = set()
        self.current_games = []
        self.chip_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=AppSpacing.XS)
        self.result_container = ft.Container()

    # ---------- Kategori ----------

    def _chip(self, category: str) -> ft.Control:
        c = get_palette(self.mode)
        selected = category in self.selected_categories
        return ft.Container(
            on_click=lambda e, cat=category: self._toggle_category(cat),
            ink=True,
            bgcolor=c.PRIMARY if selected else c.ELEVATED,
            border=ft.Border.all(1, c.PRIMARY if selected else c.BORDER),
            border_radius=AppRadius.PILL,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.XS),
            content=ft.Text(category, size=AppTypography.CAPTION,
                             color=c.ON_PRIMARY if selected else c.TEXT,
                             weight=ft.FontWeight.BOLD),
        )

    def _refresh_chips(self):
        self.chip_row.controls = [self._chip(cat) for cat in CATEGORIES]

    def _toggle_category(self, category: str):
        if category in self.selected_categories:
            self.selected_categories.discard(category)
        else:
            self.selected_categories.add(category)
        self._refresh_chips()
        self.page.update()

    # ---------- Acak ----------

    def _pool(self):
        if not self.selected_categories:
            return GAME_OBJECTS
        pool = [g for g in GAME_OBJECTS if g.category in self.selected_categories]
        return pool or GAME_OBJECTS   # kalau kombinasi kategori kosong, jatuh ke semua game

    def _roll(self, e=None):
        pool = self._pool()
        k = min(RANDOM_RESULT_COUNT, len(pool))
        self.current_games = random.sample(pool, k)
        self.result_container.content = ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                game_list_tile(
                    g, self.mode,
                    on_tap=async_handler(self.on_open_game, g.id),
                )
                for g in self.current_games
            ],
        )
        self.page.update()

    # ---------- Bangun View ----------

    def build_view(self) -> ft.View:
        c = get_palette(self.mode)
        self._refresh_chips()

        self._roll()   # auto-acak saat layar dibuka, meneruskan perilaku Kivy

        body = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=AppSpacing.LG,
            controls=[
                ft.Text("Filter kategori (opsional)", size=AppTypography.BODY,
                         weight=ft.FontWeight.BOLD, color=c.TEXT),
                self.chip_row,
                ft.Text(f"{RANDOM_RESULT_COUNT} pilihan buat kamu, ketuk salah satu untuk buka detail",
                         size=AppTypography.CAPTION, color=c.TEXT_MUTED),
                self.result_container,
            ],
        )

        bottom_bar = ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.LG, vertical=AppSpacing.SM),
            alignment=ft.Alignment.CENTER_RIGHT,
            content=ft.Button(content="Acak Ulang", icon=ft.Icons.CASINO_ROUNDED,
                                on_click=self._roll, bgcolor=c.PRIMARY, color=c.ON_PRIMARY),
        )

        return ft.View(
            route="/random",
            bgcolor=c.BG,
            padding=0,
            appbar=ft.AppBar(
                title=ft.Text("Random Game", color=c.TEXT, weight=ft.FontWeight.BOLD),
                bgcolor=c.SURFACE,
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=c.TEXT,
                                       on_click=self.on_close),
            ),
            controls=[
                ft.Container(expand=True, padding=AppSpacing.LG, content=body),
                bottom_bar,
            ],
        )
