"""Entry point KartuPedia (Flet).

Alur start: tampilkan Splash sebentar (logo + nama app), lalu masuk ke shell
utama (AppShell: AppBar + NavigationBar + 4 tab).
"""
import asyncio

import flet as ft

from app.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from app.theme import build_theme, get_palette
from app.storage import Storage
from app.shell import AppShell
from app.views.splash_view import build_splash_view

SPLASH_DURATION_SECONDS = 1.2


async def main(page: ft.Page):
    page.title = APP_NAME
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.padding = 0
    page.theme = build_theme("light")
    page.dark_theme = build_theme("dark")

    storage = Storage(page)
    saved_mode = await storage.get_theme_mode()
    page.theme_mode = ft.ThemeMode.DARK if saved_mode == "dark" else ft.ThemeMode.LIGHT

    mode = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
    c = get_palette(mode)
    page.bgcolor = c.BG
    page.views.clear()
    page.views.append(build_splash_view(mode))
    page.update()

    await asyncio.sleep(SPLASH_DURATION_SECONDS)

    shell = AppShell(page, storage)
    await shell.mount()


ft.run(main)
