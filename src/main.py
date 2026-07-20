"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
import importlib


def get_tabulate_func():
    """Lazily resolve tabulate if installed; return None otherwise."""
    try:
        return importlib.import_module("tabulate").tabulate
    except Exception:
        return None

from src.recommender import load_songs, recommend_songs


RANKING_MODES = {
    "balanced": "Default blend of all features",
    "genre_first": "Prioritizes genre and decade alignment",
    "mood_first": "Prioritizes mood and mood-tag alignment",
    "energy_focused": "Prioritizes energy and intensity features",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run music recommendations with selectable ranking modes.")
    parser.add_argument(
        "--mode",
        default="balanced",
        choices=[*RANKING_MODES.keys(), "all"],
        help="Ranking strategy mode. Use 'all' to compare every mode.",
    )
    return parser.parse_args()


def truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def build_recommendations_table(recommendations) -> str:
    tabulate_func = get_tabulate_func()
    rows = []
    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reason_items = [item.strip() for item in explanation.split(",") if item.strip()]
        summary_reasons = "; ".join(reason_items[:3]) if reason_items else "general fit"
        rows.append(
            [
                idx,
                truncate(song["title"], 26),
                truncate(song["artist"], 20),
                truncate(song.get("genre", "unknown"), 12),
                f"{score:.2f}",
                truncate(summary_reasons, 70),
            ]
        )

    headers = ["#", "Title", "Artist", "Genre", "Score", "Reasons"]
    if tabulate_func is not None:
        return tabulate_func(rows, headers=headers, tablefmt="github")

    # Plain ASCII fallback when tabulate is unavailable.
    col_widths = [
        max(len(str(row[col_idx])) for row in ([headers] + rows))
        for col_idx in range(len(headers))
    ]

    def format_row(values) -> str:
        parts = []
        for idx, value in enumerate(values):
            align_right = headers[idx] in {"#", "Score"}
            text = str(value)
            parts.append(text.rjust(col_widths[idx]) if align_right else text.ljust(col_widths[idx]))
        return " | ".join(parts)

    separator = "-+-".join("-" * width for width in col_widths)
    return "\n".join([format_row(headers), separator] + [format_row(row) for row in rows])


def print_recommendations_block(profile_name: str, recommendations, ranking_mode: str) -> None:
    print("\n" + "=" * 64)
    print(f"Top Recommendations - {profile_name}")
    print(f"Ranking Mode        - {ranking_mode} ({RANKING_MODES.get(ranking_mode, 'custom')})")
    print("=" * 64)
    print(build_recommendations_table(recommendations))

    top_score = None
    for _, score, _ in recommendations:
        if top_score is None:
            top_score = score

    avg_score = sum(score for _, score, _ in recommendations) / len(recommendations)
    print(
        "Summary: "
        f"top={top_score:.2f} | avg_top_{len(recommendations)}={avg_score:.2f} | "
        f"unique_artists={len({song['artist'] for song, _, _ in recommendations})} | "
        f"unique_genres={len({song.get('genre', 'unknown') for song, _, _ in recommendations})}"
    )


def main() -> None:
    args = parse_args()
    songs = load_songs("data/songs.csv")

    profiles = {
        "High-Energy Pop": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.88,
            "target_valence": 0.82,
            "likes_acoustic": False,
            "target_liveness": 0.35,
            "target_speechiness": 0.12,
            "target_instrumentalness": 0.08,
        },
        "Chill Lofi": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.42,
            "target_valence": 0.62,
            "likes_acoustic": True,
            "target_liveness": 0.25,
            "target_speechiness": 0.10,
            "target_instrumentalness": 0.65,
        },
        "Deep Intense Rock": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.92,
            "target_valence": 0.40,
            "likes_acoustic": False,
            "target_liveness": 0.55,
            "target_speechiness": 0.10,
            "target_instrumentalness": 0.15,
        },
    }

    adversarial_profiles = {
        "Adversarial: Conflicting Mood vs Energy": {
            "favorite_genre": "rock",
            "favorite_mood": "chill",
            "target_energy": 0.95,
            "target_valence": 0.20,
            "likes_acoustic": True,
            "target_liveness": 0.30,
            "target_speechiness": 0.10,
            "target_instrumentalness": 0.10,
        },
        "Adversarial: Genre Lock-In Test": {
            "favorite_genre": "lofi",
            "favorite_mood": "intense",
            "target_energy": 0.92,
            "target_valence": 0.40,
            "likes_acoustic": False,
            "target_liveness": 0.40,
            "target_speechiness": 0.12,
            "target_instrumentalness": 0.08,
        },
        "Adversarial: Acoustic Contradiction": {
            "favorite_genre": "classical",
            "favorite_mood": "serene",
            "target_energy": 0.30,
            "target_valence": 0.65,
            "likes_acoustic": False,
            "target_liveness": 0.20,
            "target_speechiness": 0.05,
            "target_instrumentalness": 0.80,
        },
        "Adversarial: Nonexistent Category": {
            "favorite_genre": "blues",
            "favorite_mood": "euphoric",
            "target_energy": 0.70,
            "target_valence": 0.70,
            "likes_acoustic": True,
            "target_liveness": 0.35,
            "target_speechiness": 0.20,
            "target_instrumentalness": 0.25,
        },
    }

    selected_modes = list(RANKING_MODES.keys()) if args.mode == "all" else [args.mode]

    for ranking_mode in selected_modes:
        for profile_name, user_prefs in profiles.items():
            recommendations = recommend_songs(user_prefs, songs, k=5, ranking_strategy=ranking_mode)
            print_recommendations_block(profile_name, recommendations, ranking_mode)

        for profile_name, user_prefs in adversarial_profiles.items():
            recommendations = recommend_songs(user_prefs, songs, k=5, ranking_strategy=ranking_mode)
            print_recommendations_block(profile_name, recommendations, ranking_mode)
    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
