"""Layar Tonton Tutorial: video YouTube diputar di dalam aplikasi lewat WebView.

Memakai package flet-webview-all (BUKAN flet-webview resmi, yang tidak
mendukung Windows). Package ini adalah EXTENSION: kodenya harus dikompilasi
ke dalam klien Flutter lewat `flet build`. Klien bawaan `flet run` (web,
desktop, maupun app "Flet" di HP) tidak memilikinya, sehingga kontrolnya
tampil sebagai kotak merah "Unknown control: flet_webview_all" -- dan itu
dirender di sisi klien, jadi TIDAK bisa ditangkap try/except di Python.

Karena itu pemilihan pemutar dilakukan SEBELUM kontrol dibuat:
  - aplikasi hasil build (atau INAPP_VIDEO_MODE = "on")  -> WebView
  - selain itu (mode dev `flet run`)                     -> tampilan cadangan:
    thumbnail + tombol "Tonton di YouTube"

Tombol "Buka di YouTube" pada mode WebView tetap ada, karena sebagian video
YouTube melarang di-embed pemiliknya (WebView hanya menampilkan pesan error
dari YouTube, bukan exception Python).
"""
import os

import flet as ft

from app import config
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography
from app.async_utils import async_handler

try:
    from flet_webview_all import FletWebviewAll
except ImportError:  # package belum terpasang
    FletWebviewAll = None

THUMB_HEIGHT = 220


def _inapp_player_available() -> bool:
    """True kalau kontrol WebView benar-benar ada di klien yang sedang jalan."""
    if FletWebviewAll is None:
        return False
    mode = str(getattr(config, "INAPP_VIDEO_MODE", "auto")).strip().lower()
    if mode == "off":
        return False
    if mode == "on":
        return True
    # "auto": FLET_APP_CONSOLE hanya di-set Flet pada aplikasi hasil `flet build`
    # (mode produksi), tidak pada `flet run`.
    return bool(os.environ.get("FLET_APP_CONSOLE"))


async def _open_external(game):
    if game.tutorial_url:
        await ft.UrlLauncher().launch_url(game.tutorial_url)


def _fallback_player(mode: str, game) -> ft.Control:
    """Cadangan untuk mode dev: thumbnail besar + penjelasan + tombol YouTube."""
    c = get_palette(mode)
    open_youtube = async_handler(_open_external, game)

    thumbnail = ft.Container(
        height=THUMB_HEIGHT,
        border_radius=AppRadius.LG,
        bgcolor=c.ELEVATED,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        on_click=open_youtube,
        ink=True,
        content=ft.Stack(
            fit=ft.StackFit.EXPAND,
            controls=[
                ft.Image(src=game.tutorial_thumbnail_url, fit=ft.BoxFit.COVER),
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.Container(
                        width=64, height=64,
                        bgcolor=ft.Colors.with_opacity(0.55, "#000000"),
                        border_radius=32,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=c.WHITE, size=36),
                    ),
                ),
            ],
        ),
    )

    return ft.Container(
        expand=True,
        padding=AppSpacing.LG,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=AppSpacing.MD,
            controls=[
                thumbnail,
                ft.Text(
                    "Pemutar di dalam aplikasi aktif di aplikasi hasil build "
                    "(APK / Windows). Pada mode pengembangan, video dibuka di YouTube.",
                    size=AppTypography.CAPTION, color=c.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content="Tonton di YouTube",
                    icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                    on_click=open_youtube,
                    bgcolor=c.PRIMARY,
                    color=c.ON_PRIMARY,
                ),
            ],
        ),
    )


def build_tutorial_player_view(mode: str, game, on_close) -> ft.View:
    c = get_palette(mode)
    use_webview = _inapp_player_available() and bool(game.tutorial_embed_url)

    if use_webview:
        player_area = ft.Container(
            expand=True,
            bgcolor="#000000",
            content=FletWebviewAll(url=game.tutorial_embed_url, expand=True),
        )
        bottom_bar = ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.LG, vertical=AppSpacing.SM),
            bgcolor=c.SURFACE,
            content=ft.Row(
                spacing=AppSpacing.SM,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Video tidak muncul?", size=AppTypography.CAPTION,
                             color=c.TEXT_MUTED, expand=True),
                    ft.OutlinedButton(
                        content="Buka di YouTube",
                        icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                        on_click=async_handler(_open_external, game),
                    ),
                ],
            ),
        )
        controls = [player_area, bottom_bar]
    else:
        controls = [_fallback_player(mode, game)]

    return ft.View(
        route=f"/tutorial/{game.id}",
        bgcolor=c.BG,
        padding=0,
        appbar=ft.AppBar(
            title=ft.Text(f"Tutorial {game.name}", color=c.TEXT, weight=ft.FontWeight.BOLD,
                           size=AppTypography.SECTION),
            bgcolor=c.SURFACE,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=c.TEXT,
                                   on_click=on_close),
        ),
        controls=controls,
    )
