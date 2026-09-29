"""Konten layar Jelajah: pencarian, chip kategori cepat, dan tombol filter.

Struktur sengaja dipisah: fungsi ini hanya membangun bagian yang JARANG
berubah (search field, chip kategori, tombol filter) + satu wadah kosong
untuk daftar hasil. AppShell yang mengisi/memperbarui wadah hasil itu setiap
kali user mengetik atau ganti filter -- TANPA membangun ulang search field,
supaya fokus keyboard tidak hilang setiap kali huruf diketik (search field
yang dibangun ulang akan kehilangan fokus di Flet).
"""
import flet as ft

from app.database import CATEGORIES
from app.async_utils import async_handler
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography


def build_category_chip(category: str, mode: str, selected: bool, on_toggle) -> ft.Control:
    c = get_palette(mode)
    bg = c.PRIMARY if selected else c.ELEVATED
    fg = c.ON_PRIMARY if selected else c.TEXT
    return ft.Container(
        on_click=lambda e: on_toggle(category),
        ink=True,
        bgcolor=bg,
        border=ft.Border.all(1, c.BORDER if not selected else c.PRIMARY),
        border_radius=AppRadius.PILL,
        padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.XS),
        content=ft.Text(category, size=AppTypography.CAPTION, color=fg, weight=ft.FontWeight.BOLD),
    )


def build_chip_row(mode: str, active_category, on_toggle) -> ft.Control:
    return ft.Row(
        scroll=ft.ScrollMode.AUTO,
        spacing=AppSpacing.XS,
        controls=[
            build_category_chip(cat, mode, cat == active_category, on_toggle)
            for cat in CATEGORIES
        ],
    )


def build_explore_shell(mode: str, query: str, results_container: ft.Control,
                         chip_container: ft.Control, on_search_change, on_open_filter) -> ft.Control:
    c = get_palette(mode)

    search_field = ft.TextField(
        value=query,
        hint_text="Cari permainan kartu...",
        color=c.TEXT,
        hint_style=ft.TextStyle(color=c.TEXT_MUTED),
        bgcolor=c.ELEVATED,
        # border_radius/border_color/focused_border_color sudah deprecated di
        # TextField (akan dihapus versi 1.3.0) -> dipindah ke OutlineInputBorder,
        # dgn border beda warna per ControlState (default vs fokus).
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=AppRadius.MD,
                side=ft.BorderSide(color=c.BORDER),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=AppRadius.MD,
                side=ft.BorderSide(width=2, color=c.PRIMARY),
            ),
        },
        content_padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.SM),
        expand=True,
        on_change=on_search_change,
    )

    filter_button = ft.Container(
        on_click=async_handler(on_open_filter),
        ink=True,
        width=46, height=46,
        bgcolor=c.ELEVATED,
        border=ft.Border.all(1, c.BORDER),
        border_radius=AppRadius.MD,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.TUNE_ROUNDED, color=c.TEXT, size=22),
    )

    return ft.Column(
        expand=True,
        spacing=AppSpacing.SM,
        controls=[
            ft.Container(height=AppSpacing.XS),
            ft.Row(spacing=AppSpacing.XS, controls=[search_field, filter_button]),
            chip_container,
            results_container,
        ],
    )


def build_results_list(results, mode: str, on_open_game) -> ft.Control:
    from app.components.game_card import game_list_tile
    from app.components.empty_state import empty_state

    c = get_palette(mode)
    header = ft.Text(f"{len(results)} permainan ditemukan", size=AppTypography.CAPTION, color=c.TEXT_MUTED)

    if not results:
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                empty_state(
                    mode, ft.Icons.SEARCH_OFF_ROUNDED,
                    "Tidak ada hasil",
                    "Coba ubah kata kunci atau filter pencarian.",
                ),
            ],
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=AppSpacing.XS,
        controls=[header] + [
            game_list_tile(g, mode, on_tap=async_handler(on_open_game, g.id))
            for g in results
        ] + [ft.Container(height=AppSpacing.XXL)],
    )
