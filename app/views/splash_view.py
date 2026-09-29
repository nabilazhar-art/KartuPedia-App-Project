"""Layar pembuka (splash): logo, nama app, tagline.

Dibuat sebagai KONTEN (bukan ft.View baru) supaya bisa ditampilkan di view
root yang sama dengan aplikasi utama. Mengganti seluruh page.views (clear +
append) saat transisi splash -> shell terbukti rawan membuat layar macet di
splash pada perangkat Android.
"""
import flet as ft

from app.config import APP_NAME, APP_TAGLINE
from app.theme import get_palette, AppSpacing, AppTypography


def build_splash_content(mode: str) -> ft.Control:
    c = get_palette(mode)

    logo = ft.Container(
        width=88, height=88,
        bgcolor=c.PRIMARY,
        border_radius=22,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.STYLE_ROUNDED, color=c.WHITE, size=44),
    )

    return ft.SafeArea(
        expand=True,
        content=ft.Container(
            expand=True,
            bgcolor=c.BG,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=AppSpacing.SM,
                controls=[
                    logo,
                    ft.Text(APP_NAME, size=AppTypography.HERO,
                             weight=ft.FontWeight.BOLD, color=c.TEXT),
                    ft.Text(APP_TAGLINE, size=AppTypography.CAPTION, color=c.TEXT_SECONDARY,
                             text_align=ft.TextAlign.CENTER),
                ],
            ),
        ),
    )
