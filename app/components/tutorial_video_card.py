"""Kartu video tutorial YouTube: thumbnail 16:9 + overlay tombol play.

Menyentuh kartu memanggil callback on_tap(game_id) -- oleh AppShell diarahkan
ke layar pemutar (WebView, lihat views/tutorial_player_view.py). Kartu ini
sendiri tidak tahu cara memutar video, jadi mudah dipakai ulang.
"""
import flet as ft

from app.theme import get_palette, AppSpacing, AppRadius, AppTypography
from app.async_utils import async_handler

THUMB_HEIGHT = 190


def tutorial_video_card(game, mode: str, on_tap) -> ft.Control:
    c = get_palette(mode)

    thumbnail = ft.Container(
        height=THUMB_HEIGHT,
        border_radius=ft.BorderRadius(top_left=AppRadius.LG, top_right=AppRadius.LG,
                                        bottom_left=0, bottom_right=0),
        bgcolor=c.ELEVATED,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        # Perbaikan dari user (hasil tes di Flet asli): di dalam Stack, anak
        # tidak memakai expand=True, melainkan Stack.fit=EXPAND supaya gambar
        # & overlay play memenuhi area thumbnail.
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
                ft.Text("Tonton Tutorial", size=AppTypography.CAPTION,
                         weight=ft.FontWeight.BOLD, color=c.GOLD_LIGHT),
            ],
        ),
    )

    return ft.Container(
        on_click=async_handler(on_tap, game.id),
        ink=True,
        bgcolor=c.SURFACE,
        border=ft.Border.all(1, c.BORDER),
        border_radius=AppRadius.LG,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(spacing=0, controls=[thumbnail, label_row]),
    )
