"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse

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


def print_recommendations_block(profile_name: str, recommendations, ranking_mode: str) -> None:
    print("\n" + "=" * 64)
    print(f"Top Recommendations - {profile_name}")
    print(f"Ranking Mode        - {ranking_mode} ({RANKING_MODES.get(ranking_mode, 'custom')})")
    print("=" * 64)
    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reason_items = [item.strip() for item in explanation.split(",") if item.strip()]

        print(f"\n{idx}. {song['title']} - {song['artist']}")
        print(f"   Final Score : {score:.2f}")
        print("   Reasons     :")
        for reason in reason_items:
            print(f"   - {reason}")


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
