"""Kartu ajakan Random Game di Beranda."""
import flet as ft

from app.theme import get_palette, AppSpacing, AppRadius, AppTypography


def random_promo_card(mode: str, on_tap=None) -> ft.Control:
    c = get_palette(mode)
    return ft.Container(
        on_click=on_tap,
        ink=True,
        bgcolor=c.SURFACE,
        border=ft.Border.all(1, c.BORDER),
        border_radius=AppRadius.LG,
        padding=AppSpacing.MD,
        content=ft.Row(
            spacing=AppSpacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=52, height=52,
                    bgcolor=c.ELEVATED,
                    border_radius=AppRadius.MD,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.CASINO_ROUNDED, color=c.GOLD_LIGHT, size=26),
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text("Acak Permainan", size=AppTypography.BODY,
                                 weight=ft.FontWeight.BOLD, color=c.TEXT),
                        ft.Text("Tidak mau mikir? Biar kami pilihkan satu untukmu.",
                                 size=AppTypography.CAPTION, color=c.TEXT_SECONDARY,
                                 max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=c.TEXT_MUTED, size=20),
            ],
        ),
    )
