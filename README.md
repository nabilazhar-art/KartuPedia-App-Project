# KartuPedia (Flet)

Ensiklopedia permainan kartu. Versi ini adalah hasil migrasi dari
versi Kivy ke [Flet](https://flet.dev), dengan tampilan dirombak total ke
gaya Material Design (Flutter) — bukan sekadar port 1:1.

## Fitur

- **Beranda** — game unggulan, promo Game Finder, promo Random Game,
  kategori, riwayat dilihat, populer
- **Jelajah** — pencarian + filter (jumlah pemain, durasi, kesulitan, kategori)
- **Game Finder** — wizard 5 pertanyaan, merekomendasikan hingga 5 game
  dengan alasan kecocokannya
- **Random Game** — 3 pilihan acak sekaligus, dengan filter kategori opsional
- **Detail Game** — aturan main lengkap, video tutorial YouTube
- **Favorit** — daftar game yang ditandai favorit
- **Pengaturan** — ringkasan statistik (favorit/dilihat), toggle tema, hapus
  riwayat/favorit (dengan Undo), info aplikasi
- Tema **Dark/Light** dengan toggle, tersimpan permanen
- Video tutorial: diputar langsung di aplikasi (WebView) pada versi hasil
  `flet build`; di mode pengembangan (`flet run`) otomatis beralih ke
  tampilan cadangan (thumbnail + tombol buka YouTube) — lihat
  `app/config.py` (`INAPP_VIDEO_MODE`) dan `app/views/tutorial_player_view.py`

## Menjalankan (mode pengembangan)

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
flet run --web main.py      # atau: flet run main.py (desktop)
flet run --android main.py      # Android (memerlukan aplikasi flet di android)
flet build apk -v      # menjadikan kodingan ke APK
```

## Struktur Proyek

```
main.py                        # entry point (splash lalu shell utama)
data/
    games.json                   # database 34 game (sama dgn versi Kivy)
app/
    config.py                     # identitas app, path data, INAPP_VIDEO_MODE
    theme.py                      # palet warna Dark & Light, design tokens
    models.py                     # class Game
    database.py                   # load games.json
    storage.py                    # favorit, riwayat, preferensi tema (shared_preferences)
    utils.py                      # filter_games dkk
    finder_logic.py                # skor & rekomendasi Game Finder (murni Python)
    async_utils.py                 # helper on_click -> method async
    shell.py                       # AppBar + NavigationBar + navigasi antar layar
    components/                    # widget yang dipakai ulang
    views/                         # satu file per layar
```

## Catatan Migrasi

Proyek ini dibangun bertahap sambil diuji langsung oleh pengguna di Flet
asli (bukan cuma disimulasikan), karena API Flet berubah cukup cepat antar
versi. Beberapa hal yang perlu diperhatikan kalau mengembangkan lebih lanjut:

- Semua warna/spacing/border pakai kelas kapital (`ft.Padding`, `ft.Border`,
  `ft.Alignment`, `ft.Colors`), bukan bentuk huruf kecil lama.
- Tombol memakai `ft.Button` (terisi), `ft.OutlinedButton`, `ft.TextButton`
  — bukan `ft.ElevatedButton`/`ft.FilledButton` (sudah dihapus).
- Parameter teks tombol adalah `content=`, bukan `text=`.
- Penyimpanan lokal lewat `ft.SharedPreferences()`, bukan
  `page.client_storage` atau `page.launch_url()` (keduanya deprecated/dihapus).
- `flet-webview-all` adalah *extension*: hanya aktif di aplikasi hasil
  `flet build`, tidak tersedia di `flet run` biasa.

## Riwayat

Proyek awalnya dibuat dengan menggunakan Kivy (proyek `KartuPedia` versi kivy ada di branch yang sudah saya buat), yang kemudian dirombak total ke Flet untuk tampilan yang lebih modern.
