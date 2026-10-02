"""Model data: representasi satu permainan kartu.

Dipindah dari versi Kivy (kartupedia/core/models.py) tanpa perubahan berarti --
class ini murni Python, tidak pernah bergantung pada Kivy.
"""


class Game:
    """Representasi satu permainan kartu."""

    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.name = data.get("name", "Tanpa Nama")
        self.category = data.get("category", "Klasik")
        self.description = data.get("description", "")
        self.players_min = data.get("players_min", 1)
        self.players_max = data.get("players_max", 1)
        self.duration = data.get("duration", "15-30 menit")
        self.duration_minutes = data.get("duration_minutes", 20)
        self.difficulty = data.get("difficulty", "Mudah")
        self.tags = data.get("tags", [])
        self.style = data.get("style", "Santai")
        self.about = data.get("about", "")
        self.objective = data.get("objective", "")
        self.setup = data.get("setup", "")
        self.how_to_play = data.get("how_to_play", [])
        self.special_cards = data.get("special_cards", [])
        self.ranking = data.get("ranking", [])
        self.scoring = data.get("scoring", "")
        self.tips = data.get("tips", [])
        self.variations = data.get("variations", [])
        self.quick_guide = data.get("quick_guide", [])
        self.tutorial_youtube_id = data.get("tutorial_youtube_id", "")

    @property
    def tutorial_url(self):
        """Link YouTube biasa (dipakai fallback / tombol "buka di YouTube")."""
        if not self.tutorial_youtube_id:
            return ""
        return f"https://youtu.be/{self.tutorial_youtube_id}"

    @property
    def tutorial_embed_url(self):
        """Link embed YouTube untuk diputar di WebView dalam aplikasi."""
        if not self.tutorial_youtube_id:
            return ""
        return (
            f"https://www.youtube.com/embed/{self.tutorial_youtube_id}"
            "?autoplay=1&playsinline=1&rel=0&modestbranding=1"
            "&origin=https://www.youtube.com"
        )

    @property
    def tutorial_embed_html(self):
        """Halaman HTML berisi iframe YouTube (dipakai untuk mengatasi Error 153).

        Error 153 muncul kalau pemutar embed dimuat tanpa Referer. Iframe dengan
        referrerpolicy eksplisit membuat WebView mengirim referrer ke YouTube.
        """
        if not self.tutorial_youtube_id:
            return ""
        return (
            "<!doctype html><html><head>"
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="referrer" content="strict-origin-when-cross-origin">'
            "<style>html,body{margin:0;height:100%;background:#000}"
            "iframe{position:absolute;inset:0;width:100%;height:100%;border:0}</style>"
            "</head><body>"
            f'<iframe src="{self.tutorial_embed_url}" '
            'referrerpolicy="strict-origin-when-cross-origin" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
            'gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
            "</body></html>"
        )

    @property
    def tutorial_thumbnail_url(self):
        """URL thumbnail video (dari CDN img.youtube.com, kosong kalau tidak ada video)."""
        if not self.tutorial_youtube_id:
            return ""
        return f"https://img.youtube.com/vi/{self.tutorial_youtube_id}/hqdefault.jpg"

    def player_label(self):
        if self.players_min == self.players_max:
            return f"{self.players_min} Pemain"
        return f"{self.players_min}-{self.players_max} Pemain"

    def matches_query(self, query: str) -> bool:
        if not query:
            return True
        q = query.strip().lower()
        haystack = " ".join([
            self.name, self.category, self.description,
            " ".join(self.tags),
        ]).lower()
        return q in haystack
