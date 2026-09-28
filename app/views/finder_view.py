"""Layar Game Finder: 5 pertanyaan (chip) -> rekomendasi game.

Dipush sebagai View tersendiri (dengan tombol back), seperti Detail/Filter.
Aturan skornya ada di app/finder_logic.py (tanpa Flet, diuji identik dgn Kivy).

Pilihan UX:
- Tombol "Temukan Rekomendasi" & "Ulangi" ditaruh di bar bawah yang TETAP
  (tidak ikut scroll), jadi selalu terjangkau di layar HP.
- Chip diperbarui di tempat (mengganti isi Row-nya saja, bukan membangun ulang
  seluruh halaman), supaya posisi scroll tidak melompat ke atas tiap memilih.
- Tap chip yang sudah terpilih = membatalkan pilihan itu.
- Setelah "Temukan", halaman digulir otomatis ke hasil.
"""
import inspect

import flet as ft

from app.async_utils import async_handler
from app.components.recommendation_card import recommendation_card
from app.database import GAME_OBJECTS
from app.finder_logic import QUESTIONS, recommend, reason_text
from app.theme import get_palette, AppSpacing, AppRadius, AppTypography

_RESULTS_KEY = "finder_results"


class FinderScreen:
    def __init__(self, page: ft.Page, mode: str, on_open_game, on_close):
        self.page = page
        self.mode = mode
        self.on_open_game = on_open_game   # async, menerima game_id
        self.on_close = on_close           # async, dipakai tombol back
        self.answers = {}
        self.chip_rows = {}                # kunci pertanyaan -> ft.Row berisi chip
        self.options = {key: opts for _, opts, key in QUESTIONS}
        self.results_col = ft.Column(spacing=AppSpacing.SM)
        self.scroll_col = None

    # ---------- Chip pilihan ----------

    def _chip(self, key: str, option: str) -> ft.Control:
        c = get_palette(self.mode)
        selected = self.answers.get(key) == option
        return ft.Container(
            on_click=lambda e, k=key, o=option: self._select(k, o),
            ink=True,
            bgcolor=ft.Colors.with_opacity(0.22, c.PRIMARY) if selected else c.SURFACE,
            border=ft.Border.all(1, c.PRIMARY_LIGHT if selected else c.BORDER),
            border_radius=AppRadius.MD,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.SM),
            content=ft.Text(
                option, size=AppTypography.CAPTION,
                weight=ft.FontWeight.BOLD if selected else ft.FontWeight.W_500,
                color=c.PRIMARY_LIGHT if selected else c.TEXT_SECONDARY,
            ),
        )

    def _refresh_chips(self, key: str):
        self.chip_rows[key].controls = [self._chip(key, o) for o in self.options[key]]

    def _select(self, key: str, option: str):
        if self.answers.get(key) == option:
            self.answers.pop(key)          # tap ulang = batalkan pilihan
        else:
            self.answers[key] = option
        self._refresh_chips(key)
        self.page.update()

    def _question(self, title: str, key: str) -> ft.Control:
        c = get_palette(self.mode)
        row = ft.Row(wrap=True, spacing=AppSpacing.XS, run_spacing=AppSpacing.XS)
        self.chip_rows[key] = row
        self._refresh_chips(key)
        return ft.Column(
            spacing=AppSpacing.XS,
            controls=[
                ft.Text(title, size=AppTypography.BODY, weight=ft.FontWeight.BOLD, color=c.TEXT),
                row,
            ],
        )

    # ---------- Aksi ----------

    def _reset(self, e=None):
        self.answers = {}
        for key in self.chip_rows:
            self._refresh_chips(key)
        self.results_col.controls = []
        self.page.update()

    def _message(self, icon, title: str, subtitle: str = "") -> ft.Control:
        c = get_palette(self.mode)
        controls = [
            ft.Icon(icon, color=c.TEXT_MUTED, size=36),
            ft.Text(title, size=AppTypography.SECTION, weight=ft.FontWeight.BOLD,
                     color=c.TEXT, text_align=ft.TextAlign.CENTER),
        ]
        if subtitle:
            controls.append(ft.Text(subtitle, size=AppTypography.CAPTION, color=c.TEXT_SECONDARY,
                                     text_align=ft.TextAlign.CENTER))
        return ft.Container(
            padding=AppSpacing.LG,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                               spacing=AppSpacing.XS, controls=controls),
        )

    def _render_results(self):
        c = get_palette(self.mode)
        header = ft.Container(
            key=_RESULTS_KEY,
            content=ft.Text("", size=1),   # jangkar scroll; diganti judul di bawah
        )
        if not self.answers:
            header.content = ft.Text("Pilih jawaban terlebih dahulu", size=AppTypography.SECTION,
                                      weight=ft.FontWeight.BOLD, color=c.TEXT)
            self.results_col.controls = [
                header,
                self._message(ft.Icons.TOUCH_APP_OUTLINED, "Belum ada jawaban",
                              "Pilih minimal satu jawaban di atas, lalu tekan Temukan Rekomendasi."),
            ]
            return

        header.content = ft.Text("Rekomendasi Untukmu", size=AppTypography.SECTION,
                                  weight=ft.FontWeight.BOLD, color=c.TEXT)
        top = recommend(GAME_OBJECTS, self.answers)
        controls = [header]
        if not top:
            controls.append(self._message(
                ft.Icons.SEARCH_OFF_ROUNDED, "Belum menemukan game",
                "Coba ubah beberapa jawaban agar hasilnya lebih luas."))
        else:
            best = top[0][0]
            for score, game, reasons in top:
                controls.append(recommendation_card(
                    game, reason_text(score, best, reasons), self.mode,
                    on_tap=async_handler(self.on_open_game, game.id),
                    highlight=(score == best),
                ))
            controls.append(ft.Text(
                "Rekomendasi dihitung langsung dari data game di aplikasi dan dapat dicoba ulang kapan saja.",
                size=AppTypography.META, color=c.TEXT_MUTED, text_align=ft.TextAlign.CENTER))
        self.results_col.controls = controls

    async def _find(self, e=None):
        self._render_results()
        self.page.update()
        await self._scroll_to_results()

    async def _scroll_to_results(self):
        # Menggulir otomatis ke hasil hanyalah kenyamanan tambahan. API scroll_to
        # bisa sinkron atau async tergantung versi Flet, jadi dijaga penuh:
        # kalau gagal, hasil tetap tampil normal (hanya tidak digulir otomatis).
        try:
            res = self.scroll_col.scroll_to(key=_RESULTS_KEY, duration=300)
            if inspect.isawaitable(res):
                await res
        except Exception:
            pass

    # ---------- Bangun View ----------

    def build_view(self) -> ft.View:
        c = get_palette(self.mode)

        intro = ft.Container(
            bgcolor=c.STRONG,
            border=ft.Border.all(1, c.BORDER),
            border_radius=AppRadius.LG,
            padding=AppSpacing.MD,
            content=ft.Row(
                spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=48, height=48, bgcolor=c.PRIMARY_DARK, border_radius=AppRadius.MD,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=c.GOLD_LIGHT, size=26),
                    ),
                    ft.Column(
                        expand=True, spacing=2,
                        controls=[
                            ft.Text("Temukan game yang cocok", size=AppTypography.SECTION,
                                     weight=ft.FontWeight.BOLD, color=c.TEXT),
                            ft.Text("Jawab beberapa pertanyaan singkat. Boleh dilewati kalau tidak yakin.",
                                     size=AppTypography.CAPTION, color=c.TEXT_SECONDARY),
                        ],
                    ),
                ],
            ),
        )

        # Area hasil awalnya kosong sampai user menekan "Temukan Rekomendasi".
        body = [intro] + [self._question(title, key) for title, _, key in QUESTIONS]
        body += [self.results_col, ft.Container(height=AppSpacing.LG)]
        self.scroll_col = ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, spacing=AppSpacing.LG, controls=body)

        bottom_bar = ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.LG, vertical=AppSpacing.SM),
            bgcolor=c.SURFACE,
            content=ft.Row(
                spacing=AppSpacing.SM,
                controls=[
                    ft.OutlinedButton(content="Ulangi", on_click=self._reset, expand=2),
                    ft.Button(content="Temukan Rekomendasi", on_click=self._find,
                               bgcolor=c.PRIMARY, color=c.ON_PRIMARY, expand=3),
                ],
            ),
        )

        return ft.View(
            route="/finder",
            bgcolor=c.BG,
            padding=0,
            appbar=ft.AppBar(
                title=ft.Text("Game Finder", color=c.TEXT, weight=ft.FontWeight.BOLD),
                bgcolor=c.SURFACE,
                leading=ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=c.TEXT,
                                       on_click=self.on_close),
            ),
            controls=[
                ft.Container(expand=True, padding=AppSpacing.LG, content=self.scroll_col),
                bottom_bar,
            ],
        )
