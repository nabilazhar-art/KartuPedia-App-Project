"""Layar Detail Game: header locked (kategori, judul, deskripsi, metadata) +
konten yang bisa di-scroll (aturan main, tips, dst).

Ditulis sbg controller class (mirip FilterScreen) krn perlu state favorit
yang bisa berubah reaktif (ikon hati) tanpa membangun ulang seluruh layar.
"""
import flet as ft

from app.theme import get_palette, AppSpacing, AppRadius, AppTypography
from app.components.tutorial_video_card import tutorial_video_card


class DetailScreen:
    def __init__(self, page: ft.Page, storage, mode: str, game, on_close, on_open_tutorial=None):
        self.page = page
        self.storage = storage
        self.mode = mode
        self.game = game
        self.on_close = on_close
        self.on_open_tutorial = on_open_tutorial
        self.fav_icon_button = None
        self.is_favorite = False

    # ---------- Favorit ----------

    async def _toggle_favorite(self, e=None):
        self.is_favorite = await self.storage.toggle_favorite(self.game.id)
        c = get_palette(self.mode)
        self.fav_icon_button.icon = (
            ft.Icons.FAVORITE_ROUNDED if self.is_favorite else ft.Icons.FAVORITE_BORDER_ROUNDED
        )
        self.fav_icon_button.icon_color = c.ERROR if self.is_favorite else c.TEXT
        self.page.update()

    # ---------- Bagian-bagian konten ----------

    def _label(self, text: str, color) -> ft.Control:
        return ft.Text(text, size=AppTypography.BODY, color=color)

    def _section(self, title: str, body: ft.Control) -> ft.Control:
        c = get_palette(self.mode)
        return ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                ft.Text(title, size=AppTypography.SECTION, weight=ft.FontWeight.BOLD, color=c.TEXT),
                body,
            ],
        )

    def _numbered_list(self, items: list) -> ft.Control:
        c = get_palette(self.mode)
        rows = []
        for i, item in enumerate(items, start=1):
            rows.append(
                ft.Row(
                    spacing=AppSpacing.SM,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            width=24, height=24,
                            bgcolor=c.PRIMARY,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(str(i), size=AppTypography.CAPTION,
                                              weight=ft.FontWeight.BOLD, color=c.ON_PRIMARY),
                        ),
                        ft.Text(item, size=AppTypography.BODY, color=c.TEXT_SECONDARY, expand=True),
                    ],
                )
            )
        return ft.Column(spacing=AppSpacing.SM, controls=rows)

    def _bullet_text(self, items: list) -> ft.Control:
        c = get_palette(self.mode)
        text = "\n".join(f"\u2022 {t}" for t in items)
        return ft.Text(text, size=AppTypography.BODY, color=c.TEXT_SECONDARY)

    def _special_cards(self, items: list) -> ft.Control:
        c = get_palette(self.mode)
        return ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                ft.Container(
                    bgcolor=c.SURFACE,
                    border=ft.Border.all(1, c.BORDER),
                    border_radius=AppRadius.MD,
                    padding=AppSpacing.SM,
                    content=ft.Text(sc, size=AppTypography.BODY, color=c.TEXT_SECONDARY),
                )
                for sc in items
            ],
        )

    def _ranking(self, items: list) -> ft.Control:
        c = get_palette(self.mode)
        rows = []
        for i, r in enumerate(items, start=1):
            rows.append(
                ft.Row(
                    spacing=AppSpacing.SM,
                    controls=[
                        ft.Text(str(i), size=AppTypography.BODY, weight=ft.FontWeight.BOLD, color=c.GOLD),
                        ft.Text(r, size=AppTypography.BODY, color=c.TEXT_SECONDARY, expand=True),
                    ],
                )
            )
        return ft.Column(spacing=AppSpacing.XS, controls=rows)

    # ---------- Bangun View ----------

    async def build_view(self) -> ft.View:
        self.is_favorite = await self.storage.is_favorite(self.game.id)
        await self.storage.add_recently_viewed(self.game.id)

        c = get_palette(self.mode)
        g = self.game

        self.fav_icon_button = ft.IconButton(
            icon=ft.Icons.FAVORITE_ROUNDED if self.is_favorite else ft.Icons.FAVORITE_BORDER_ROUNDED,
            icon_color=c.ERROR if self.is_favorite else c.TEXT,
            on_click=self._toggle_favorite,
        )

        # Blok locked sengaja DIJAGA RINGKAS (identitas + metadata saja). Kartu
        # video tadinya di sini (F4b), tapi di layar HP area scroll jadi terlalu
        # sempit untuk membaca aturan main -> dipindah ke awal area scroll.
        locked_controls = [
            ft.Text(g.category.upper(), size=AppTypography.META,
                     weight=ft.FontWeight.BOLD, color=c.GOLD),
            ft.Text(g.name, size=AppTypography.HERO, weight=ft.FontWeight.BOLD, color=c.TEXT),
            ft.Text(g.description, size=AppTypography.BODY, color=c.TEXT_SECONDARY),
            ft.Row(
                spacing=AppSpacing.LG,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text(g.player_label(), size=AppTypography.BODY,
                                 weight=ft.FontWeight.BOLD, color=c.TEXT),
                        ft.Text("Pemain", size=AppTypography.META, color=c.TEXT_MUTED),
                    ]),
                    ft.Column(spacing=2, controls=[
                        ft.Text(g.duration, size=AppTypography.BODY,
                                 weight=ft.FontWeight.BOLD, color=c.TEXT),
                        ft.Text("Durasi", size=AppTypography.META, color=c.TEXT_MUTED),
                    ]),
                    ft.Column(spacing=2, controls=[
                        ft.Container(
                            bgcolor=c.DIFFICULTY.get(g.difficulty, c.TEXT_MUTED),
                            border_radius=AppRadius.PILL,
                            padding=ft.Padding.symmetric(horizontal=AppSpacing.SM, vertical=2),
                            content=ft.Text(g.difficulty, size=AppTypography.META,
                                              weight=ft.FontWeight.BOLD, color=c.WHITE),
                        ),
                        ft.Text("Difficulty", size=AppTypography.META, color=c.TEXT_MUTED),
                    ]),
                ],
            ),
            ft.Divider(color=c.BORDER),
        ]

        locked = ft.Column(spacing=AppSpacing.XS, controls=locked_controls)

        sections = []
        if g.tutorial_url and self.on_open_tutorial:
            sections.append(tutorial_video_card(g, self.mode, self.on_open_tutorial))
        if g.about:
            sections.append(self._section("Tentang", self._label(g.about, c.TEXT_SECONDARY)))
        if g.objective:
            sections.append(self._section("Tujuan", self._label(g.objective, c.TEXT_SECONDARY)))
        if g.setup:
            sections.append(self._section("Persiapan", self._label(g.setup, c.TEXT_SECONDARY)))
        if g.how_to_play:
            sections.append(self._section("Cara Bermain", self._numbered_list(g.how_to_play)))
        if g.special_cards:
            sections.append(self._section("Kartu Khusus", self._special_cards(g.special_cards)))
        if g.ranking:
            sections.append(self._section("Ranking", self._ranking(g.ranking)))
        if g.scoring:
            sections.append(self._section("Scoring", self._label(g.scoring, c.TEXT_SECONDARY)))
        if g.tips:
            sections.append(self._section("Tips", self._bullet_text(g.tips)))
        if g.variations:
            sections.append(self._section("Variasi", self._bullet_text(g.variations)))
        if g.quick_guide:
            sections.append(self._section("Panduan Cepat", self._numbered_list(g.quick_guide)))
        sections.append(ft.Container(height=AppSpacing.XXL))

        scrollable = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=AppSpacing.LG,
            controls=sections,
        )

        return ft.View(
            route=f"/detail/{g.id}",
            bgcolor=c.BG,
            appbar=ft.AppBar(
                bgcolor=c.SURFACE,
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=c.TEXT,
                                       on_click=self.on_close),
                actions=[self.fav_icon_button],
            ),
            controls=[
                ft.Container(
                    expand=True,
                    padding=AppSpacing.LG,
                    content=ft.Column(expand=True, spacing=AppSpacing.SM, controls=[locked, scrollable]),
                ),
            ],
        )
