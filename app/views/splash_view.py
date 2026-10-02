"""Layar pembuka (splash): logo, nama app, tagline, tampil singkat lalu
otomatis masuk ke aplikasi utama (dipanggil dari main.py).
"""
import flet as ft

from app.config import APP_NAME, APP_TAGLINE
from app.theme import get_palette, AppSpacing, AppTypography


def build_splash_view(mode: str) -> ft.View:
    c = get_palette(mode)

    logo = ft.Container(
        width=88, height=88,
        bgcolor=c.PRIMARY,
        border_radius=22,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.STYLE_ROUNDED, color=c.WHITE, size=44),
    )

    # Posisi tengah diatur langsung oleh ft.View (bukan lewat Container(expand=True)),
    # karena expand di dalam View tidak selalu mengisi layar sehingga isi splash
    # menempel di atas dan tertimpa status bar.
    return ft.View(
        route="/splash",
        bgcolor=c.BG,
        padding=0,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=AppSpacing.SM,
                controls=[
                    logo,
                    ft.Text(APP_NAME, size=AppTypography.HERO,
                             weight=ft.FontWeight.BOLD, color=c.TEXT),
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=AppSpacing.LG),
                        content=ft.Text(APP_TAGLINE, size=AppTypography.CAPTION,
                                         color=c.TEXT_SECONDARY,
                                         text_align=ft.TextAlign.CENTER),
                    ),
                ],
            ),
        ],
    )
