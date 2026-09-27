"""Layar Filter (dipush sbg View tersendiri, bukan bottom sheet -- konsisten
dgn pola navigasi drill-down yang sama dipakai Detail Game/Game Finder,
supaya tidak menambah API Flet baru yang belum teruji: page.views push/pop
sudah terbukti berfungsi di Batch F2).
"""
import flet as ft

from app.database import CATEGORIES
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography

PLAYER_OPTIONS = ["1", "2", "3-4", "5+"]
DURATION_OPTIONS = ["< 15 menit", "15-30 menit", "30-60 menit", "> 60 menit"]
DIFFICULTY_OPTIONS = ["Mudah", "Sedang", "Sulit"]


class FilterScreen:
    """Controller layar filter. Instance baru dibuat tiap kali dibuka, dibuang
    setelah ditutup -- pola sama seperti AppShell tapi berumur pendek."""

    def __init__(self, page: ft.Page, mode: str, current_filters: dict, on_apply, on_close):
        self.page = page
        self.mode = mode
        self.on_apply = on_apply
        self.on_close = on_close
        self.selected = {
            "players": set(current_filters.get("players", set())),
            "duration": set(current_filters.get("duration", set())),
            "difficulty": set(current_filters.get("difficulty", set())),
            "category": set(current_filters.get("category", set())),
        }
        self.body_container = ft.Container()

    def _chip(self, group: str, value: str) -> ft.Control:
        c = get_palette(self.mode)
        selected = value in self.selected[group]
        bg = c.PRIMARY if selected else c.ELEVATED
        fg = c.ON_PRIMARY if selected else c.TEXT
        return ft.Container(
            on_click=lambda e, g=group, v=value: self._toggle(g, v),
            ink=True,
            bgcolor=bg,
            border=ft.Border.all(1, c.BORDER if not selected else c.PRIMARY),
            border_radius=AppRadius.PILL,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.XS),
            content=ft.Text(value, size=AppTypography.CAPTION, color=fg, weight=ft.FontWeight.BOLD),
        )

    def _section(self, title: str, group: str, options: list) -> ft.Control:
        c = get_palette(self.mode)
        return ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                ft.Text(title, size=AppTypography.SECTION, weight=ft.FontWeight.BOLD, color=c.TEXT),
                ft.Row(wrap=True, spacing=AppSpacing.XS, run_spacing=AppSpacing.XS,
                        controls=[self._chip(group, opt) for opt in options]),
            ],
        )

    def _toggle(self, group: str, value: str):
        if value in self.selected[group]:
            self.selected[group].discard(value)
        else:
            self.selected[group].add(value)
        self._render_body()
        self.page.update()

    def _reset(self, e=None):
        self.selected = {"players": set(), "duration": set(), "difficulty": set(), "category": set()}
        self._render_body()
        self.page.update()

    async def _apply(self, e=None):
        self.on_apply(self.selected)
        await self.on_close()

    def _render_body(self):
        c = get_palette(self.mode)
        self.body_container.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=AppSpacing.LG,
            controls=[
                self._section("Jumlah Pemain", "players", PLAYER_OPTIONS),
                self._section("Durasi", "duration", DURATION_OPTIONS),
                self._section("Tingkat Kesulitan", "difficulty", DIFFICULTY_OPTIONS),
                self._section("Kategori", "category", CATEGORIES),
                ft.Container(height=AppSpacing.XXL),
            ],
        )

    def build_view(self) -> ft.View:
        c = get_palette(self.mode)
        self._render_body()
        self.body_container.padding = AppSpacing.LG
        self.body_container.expand = True

        return ft.View(
            route="/filter",
            bgcolor=c.BG,
            appbar=ft.AppBar(
                title=ft.Text("Filter", color=c.TEXT, weight=ft.FontWeight.BOLD),
                bgcolor=c.SURFACE,
                leading=ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=c.TEXT,
                                       on_click=self.on_close),
            ),
            controls=[
                self.body_container,
                ft.Container(
                    padding=AppSpacing.LG,
                    content=ft.Row(
                        spacing=AppSpacing.SM,
                        controls=[
                            ft.OutlinedButton(content="Reset", on_click=self._reset, expand=True),
                            ft.Button(content="Terapkan Filter", on_click=self._apply,
                                                bgcolor=c.PRIMARY, color=c.ON_PRIMARY, expand=True),
                        ],
                    ),
                ),
            ],
        )
