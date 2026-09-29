"""Entry point KartuPedia (Flet).

Alur start: tampilkan Splash sebentar (logo + nama app), lalu masuk ke shell
utama (AppShell: AppBar + NavigationBar + 4 tab).

Splash dan shell memakai SATU view root yang sama (isinya saja yang diganti),
bukan mengganti seluruh page.views. Kalau start gagal, pesan error ditampilkan
di layar (bukan macet diam-diam di splash) supaya mudah didiagnosis di HP.
"""
import asyncio
import traceback

import flet as ft

from app.config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from app.theme import build_theme, get_palette
from app.storage import Storage
from app.shell import AppShell
from app.views.splash_view import build_splash_content

SPLASH_DURATION_SECONDS = 1.2


def _root_view(page: ft.Page) -> ft.View:
    """Ambil view root bawaan page; buat baru hanya kalau belum ada."""
    if not page.views:
        page.views.append(ft.View(route="/"))
    root = page.views[0]
    root.padding = 0
    root.spacing = 0
    return root


def _show_error(page: ft.Page, root: ft.View, err: BaseException):
    root.controls = [
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=[
                    ft.Text("KartuPedia gagal dimulai", size=20,
                            weight=ft.FontWeight.BOLD, color="#E47D8A"),
                    ft.Text(f"{type(err).__name__}: {err}", size=14,
                            color="#F8FAFC", selectable=True),
                    ft.Text(traceback.format_exc(), size=11,
                            color="#B6C0D0", selectable=True),
                ],
            ),
        )
    ]
    page.update()


async def main(page: ft.Page):
    page.title = APP_NAME
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.padding = 0
    page.theme = build_theme("light")
    page.dark_theme = build_theme("dark")
    page.bgcolor = get_palette("dark").BG

    root = _root_view(page)

    try:
        storage = Storage(page)
        try:
            saved_mode = await asyncio.wait_for(storage.get_theme_mode(), timeout=3)
        except Exception:
            saved_mode = "dark"  # penyimpanan lambat/gagal -> pakai default, jangan macet
        page.theme_mode = ft.ThemeMode.DARK if saved_mode == "dark" else ft.ThemeMode.LIGHT

        mode = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
        page.bgcolor = get_palette(mode).BG
        root.bgcolor = page.bgcolor
        root.controls = [build_splash_content(mode)]
        page.update()

        await asyncio.sleep(SPLASH_DURATION_SECONDS)

        shell = AppShell(page, storage)
        await shell.mount(root)
    except Exception as err:  # noqa: BLE001
        _show_error(page, root, err)


ft.run(main)
