"""Konten layar Beranda: unggulan, promo Finder, kategori, baru dilihat, populer."""
import flet as ft

from app.database import GAME_OBJECTS, CATEGORIES, get_game_by_id
from app.theme import get_palette, AppSpacing, AppTypography, AppRadius
from app.components.game_card import featured_game_card, game_list_tile
from app.components.finder_promo_card import finder_promo_card
from app.components.random_promo_card import random_promo_card
from app.components.section_header import section_header
from app.async_utils import async_handler

# Game unggulan tetap (bukan acak), supaya tampilan tidak berubah tiap render
# (mis. tiap kali tema di-toggle). Bisa disempurnakan nanti jadi rotasi harian.
_FEATURED_ID = "regicide"


def fill_recent_section(holder: ft.Column, recent_games, mode: str, on_open_game):
    """Isi (atau kosongkan) bagian "Baru Dilihat" di dalam wadah yang persisten.

    Dipisah supaya saat kembali dari layar detail, hanya bagian ini yang
    diperbarui -- bukan seluruh Beranda dibangun ulang.
    """
    if not recent_games:
        holder.controls = []
        return
    holder.controls = [
        ft.Container(height=AppSpacing.SM),
        section_header("Baru Dilihat", mode),
        ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                game_list_tile(g, mode, on_tap=async_handler(on_open_game, g.id))
                for g in recent_games
            ],
        ),
    ]


async def build_home_view(storage, mode: str, on_open_game, on_open_finder,
                           on_open_category, on_see_all_popular, on_open_random,
                           recent_holder: ft.Column = None) -> ft.Control:
    c = get_palette(mode)

    recent_ids = await storage.get_recently_viewed()
    recent_games = [g for g in (get_game_by_id(i) for i in recent_ids) if g]

    featured = get_game_by_id(_FEATURED_ID) or GAME_OBJECTS[0]
    popular = GAME_OBJECTS[:8]

    sections = [
        ft.Container(height=AppSpacing.XS),
        ft.Text("REKOMENDASI HARI INI", size=AppTypography.META,
                 weight=ft.FontWeight.BOLD, color=c.GOLD),
        featured_game_card(featured, mode, on_tap=async_handler(on_open_game, featured.id)),

        ft.Container(height=AppSpacing.SM),
        finder_promo_card(mode, on_tap=async_handler(on_open_finder)),

        ft.Container(height=AppSpacing.XS),
        random_promo_card(mode, on_tap=async_handler(on_open_random)),

        ft.Container(height=AppSpacing.SM),
        section_header("Kategori", mode),
        ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=AppSpacing.XS,
            controls=[
                ft.Container(
                    on_click=async_handler(on_open_category, cat),
                    ink=True,
                    bgcolor=c.ELEVATED,
                    border=ft.Border.all(1, c.BORDER),
                    border_radius=AppRadius.PILL,
                    padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.XS),
                    content=ft.Text(cat, size=AppTypography.CAPTION, color=c.TEXT,
                                      weight=ft.FontWeight.BOLD),
                )
                for cat in CATEGORIES
            ],
        ),
    ]

    if recent_holder is None:
        recent_holder = ft.Column(spacing=0)
    fill_recent_section(recent_holder, recent_games, mode, on_open_game)
    sections.append(recent_holder)

    sections += [
        ft.Container(height=AppSpacing.SM),
        section_header("Populer", mode, action_text="Lihat Semua",
                        on_action=async_handler(on_see_all_popular)),
        ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                game_list_tile(g, mode, on_tap=async_handler(on_open_game, g.id))
                for g in popular
            ],
        ),
        ft.Container(height=AppSpacing.XXL),
    ]

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=AppSpacing.XS,
        controls=sections,
    )
