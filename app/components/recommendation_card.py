"""Kartu rekomendasi Game Finder: info game + alasan kenapa cocok."""
import flet as ft

from app.theme import get_palette, AppSpacing, AppRadius, AppTypography


def recommendation_card(game, reason: str, mode: str, on_tap=None, highlight: bool = False) -> ft.Control:
    """highlight=True untuk rekomendasi teratas: bingkai emas lebih tebal."""
    c = get_palette(mode)
    return ft.Container(
        on_click=on_tap,
        ink=True,
        bgcolor=c.SURFACE,
        border=ft.Border.all(2 if highlight else 1, c.GOLD if highlight else c.BORDER),
        border_radius=AppRadius.LG,
        padding=AppSpacing.MD,
        content=ft.Column(
            spacing=AppSpacing.SM,
            controls=[
                ft.Row(
                    spacing=AppSpacing.SM,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=44, height=44,
                            bgcolor=c.PRIMARY if highlight else c.ELEVATED,
                            border_radius=AppRadius.SM,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.STYLE_ROUNDED,
                                             color=c.WHITE if highlight else c.PRIMARY_LIGHT, size=22),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=2,
                            controls=[
                                ft.Text(game.name, size=AppTypography.SECTION,
                                         weight=ft.FontWeight.BOLD, color=c.TEXT,
                                         max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"{game.category} \u2022 {game.player_label()} \u2022 {game.duration}",
                                         size=AppTypography.META, color=c.TEXT_MUTED,
                                         max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color=c.TEXT_MUTED, size=20),
                    ],
                ),
                ft.Text(reason, size=AppTypography.CAPTION, color=c.GOLD_LIGHT,
                         weight=ft.FontWeight.BOLD),
            ],
        ),
    )
