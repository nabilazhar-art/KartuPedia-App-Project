"""Logika Game Finder: pertanyaan, penghitungan skor, dan alasan rekomendasi.

Dipindah dari GameFinderScreen (versi Kivy) TANPA mengubah aturan skornya, dan
sengaja dipisah dari kode tampilan (tidak meng-import Flet sama sekali) supaya
bisa diuji sendiri: hasil untuk semua kombinasi jawaban dibandingkan langsung
dengan versi Kivy.

Aturan skor: pemain +4, durasi +3, gaya +3, kesulitan +2, mode +1..+4.
Game kategori Casino atau bertag "betting" tidak pernah direkomendasikan.
"""
from app.utils import duration_bucket, player_bucket_matches

PLAYER_OPTIONS = ["1 pemain", "2 pemain", "3-4 pemain", "5+ pemain"]
TIME_OPTIONS = ["< 15 menit", "15-30 menit", "30-60 menit", "> 60 menit"]
STYLE_OPTIONS = ["Santai", "Strategis", "Cepat"]
DIFFICULTY_OPTIONS = ["Mudah", "Sedang", "Sulit"]
MODE_OPTIONS = ["Sendiri", "Kompetitif", "Kerja sama", "Bebas"]

# (judul pertanyaan, pilihan jawaban, kunci di dict jawaban)
QUESTIONS = [
    ("1. Berapa orang yang akan bermain?", PLAYER_OPTIONS, "players"),
    ("2. Berapa banyak waktu yang tersedia?", TIME_OPTIONS, "duration"),
    ("3. Gaya bermain yang diinginkan?", STYLE_OPTIONS, "style"),
    ("4. Seberapa sulit game yang diinginkan?", DIFFICULTY_OPTIONS, "difficulty"),
    ("5. Mode permainan yang dicari?", MODE_OPTIONS, "mode"),
]

MAX_RESULTS = 5
DEFAULT_REASON = "Pilihan yang cukup sesuai dengan jawabanmu."

_PLAYER_ANSWER_TO_BUCKET = {
    "1 pemain": "1",
    "2 pemain": "2",
    "3-4 pemain": "3-4",
    "5+ pemain": "5+",
}


def score_game(game, answers: dict):
    """Return (skor, daftar alasan). Skor -999 = tidak boleh direkomendasikan."""
    if game.category == "Casino" or "betting" in game.tags:
        return -999, []

    score = 0
    reasons = []

    players = _PLAYER_ANSWER_TO_BUCKET.get(answers.get("players"))
    if players and player_bucket_matches(game, players):
        score += 4
        reasons.append(f"cocok untuk {game.player_label()}")

    duration = answers.get("duration")
    if duration and duration_bucket(game.duration_minutes) == duration:
        score += 3
        reasons.append(f"durasi {game.duration}")

    style = answers.get("style")
    if style and game.style == style:
        score += 3
        reasons.append(f"gaya {game.style.lower()}")

    difficulty = answers.get("difficulty")
    if difficulty and game.difficulty == difficulty:
        score += 2
        reasons.append(f"level {game.difficulty.lower()}")

    mode = answers.get("mode")
    if mode == "Sendiri" and game.players_min == 1:
        score += 4
        reasons.append("bisa dimainkan sendiri")
    elif mode == "Kerja sama" and any(t in game.tags for t in ("kooperatif", "tim")):
        score += 4
        reasons.append("memiliki unsur kerja sama/tim")
    elif mode == "Kompetitif" and game.players_max >= 2 and not any(
            t in game.tags for t in ("kooperatif", "tim")):
        score += 2
        reasons.append("cocok untuk bermain kompetitif")
    elif mode == "Bebas":
        score += 1

    return score, reasons


def recommend(games, answers: dict, limit: int = MAX_RESULTS):
    """Return list (skor, game, alasan) urut skor tertinggi, maksimal `limit`.
    Tanpa jawaban sama sekali -> list kosong."""
    if not answers:
        return []
    scored = []
    for game in games:
        score, reasons = score_game(game, answers)
        if score >= 0:
            scored.append((score, game, reasons))
    scored.sort(key=lambda item: (-item[0], item[1].name))
    return scored[:limit]


def reason_text(score: int, best_score: int, reasons: list) -> str:
    """Kalimat alasan di kartu; game dengan skor tertinggi diberi awalan 'Paling cocok'."""
    text = " \u2022 ".join(reasons[:3]) if reasons else DEFAULT_REASON
    if score == best_score:
        text = "Paling cocok: " + text
    return text
