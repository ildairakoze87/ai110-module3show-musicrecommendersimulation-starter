"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile used for all comparisons in this simulation run.
    # This listener prefers chill, acoustic-leaning lofi with moderate energy.
    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.42,
        "target_valence": 0.62,
        "likes_acoustic": True,
        "target_liveness": 0.25,
        "target_speechiness": 0.10,
        "target_instrumentalness": 0.65,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 64)
    print("Top Recommendations")
    print("=" * 64)
    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reason_items = [item.strip() for item in explanation.split(",") if item.strip()]

        print(f"\n{idx}. {song['title']} — {song['artist']}")
        print(f"   Final Score : {score:.2f}")
        print("   Reasons     :")
        for reason in reason_items:
            print(f"   - {reason}")
    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
