"""Kartu video tutorial YouTube: thumbnail 16:9 + overlay tombol play.

Menyentuh kartu membuka video lewat browser/app YouTube di perangkat, pakai
ft.UrlLauncher().launch_url() -- BUKAN page.launch_url() yang sudah
deprecated (akan dihapus di Flet 1.0.0) atau webbrowser.open() bawaan Python
yang salah sasaran saat aplikasi dijalankan sbg web (flet run --web): itu
akan membuka browser di komputer SERVER, bukan di komputer yang melihat
halaman webnya.
"""
import flet as ft

from app.theme import get_palette, AppSpacing, AppRadius, AppTypography
from app.async_utils import async_handler

THUMB_HEIGHT = 190


async def _open_video(game):
    if game.tutorial_url:
        await ft.UrlLauncher().launch_url(game.tutorial_url)


def tutorial_video_card(game, mode: str) -> ft.Control:
    c = get_palette(mode)

    thumbnail = ft.Container(
        height=THUMB_HEIGHT,
        border_radius=ft.BorderRadius(top_left=AppRadius.LG, top_right=AppRadius.LG,
                                        bottom_left=0, bottom_right=0),
        bgcolor=c.ELEVATED,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Stack(
            fit=ft.StackFit.EXPAND,
            controls=[
                ft.Image(
                    src=game.tutorial_thumbnail_url,
                    fit=ft.BoxFit.COVER,
                ),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=56, height=56,
                        bgcolor=ft.Colors.with_opacity(0.55, "#000000"),
                        border_radius=28,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=c.WHITE, size=32),
                    ),
                ),
            ],
        ),
    )

    label_row = ft.Container(
        padding=ft.Padding.symmetric(horizontal=AppSpacing.SM, vertical=AppSpacing.XS),
        content=ft.Row(
            spacing=AppSpacing.XS,
            controls=[
                ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE_ROUNDED, color=c.GOLD_LIGHT, size=16),
                ft.Text("Tonton Tutorial di YouTube", size=AppTypography.CAPTION,
                         weight=ft.FontWeight.BOLD, color=c.GOLD_LIGHT),
            ],
        ),
    )

    return ft.Container(
        on_click=async_handler(_open_video, game),
        ink=True,
        bgcolor=c.SURFACE,
        border=ft.Border.all(1, c.BORDER),
        border_radius=AppRadius.LG,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(spacing=0, controls=[thumbnail, label_row]),
    )
