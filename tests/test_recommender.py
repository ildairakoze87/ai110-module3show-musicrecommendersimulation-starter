from src.recommender import Song, UserProfile, Recommender, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_ranking_strategy_changes_ordering():
    songs = [
        {
            "id": 1,
            "title": "Genre Match Low Energy",
            "artist": "A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.0,
            "acousticness": 0.2,
            "valence": 0.5,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
        {
            "id": 2,
            "title": "Energy Match Wrong Genre",
            "artist": "B",
            "genre": "rock",
            "mood": "happy",
            "energy": 1.0,
            "acousticness": 0.2,
            "valence": 0.5,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
    ]
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 1.0,
        "likes_acoustic": False,
    }

    balanced = recommend_songs(user_prefs, songs, k=2, ranking_strategy="balanced")
    genre_first = recommend_songs(user_prefs, songs, k=2, ranking_strategy="genre_first")

    assert balanced[0][0]["title"] == "Energy Match Wrong Genre"
    assert genre_first[0][0]["title"] == "Genre Match Low Energy"


def test_diversity_penalty_limits_repeated_artists_in_top_results():
    songs = [
        {
            "id": 1,
            "title": "A1",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.9,
            "acousticness": 0.2,
            "valence": 0.8,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
        {
            "id": 2,
            "title": "A2",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.88,
            "acousticness": 0.2,
            "valence": 0.8,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
        {
            "id": 3,
            "title": "A3",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.86,
            "acousticness": 0.2,
            "valence": 0.8,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
        {
            "id": 4,
            "title": "B1",
            "artist": "Artist B",
            "genre": "rock",
            "mood": "happy",
            "energy": 0.82,
            "acousticness": 0.2,
            "valence": 0.8,
            "liveness": 0.2,
            "speechiness": 0.1,
            "instrumentalness": 0.1,
        },
    ]
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
    }

    results = recommend_songs(
        user_prefs,
        songs,
        k=2,
        ranking_strategy="balanced",
        max_songs_per_artist=1,
        max_songs_per_genre=3,
    )

    top_artists = [song["artist"] for song, _, _ in results]
    assert top_artists.count("Artist A") == 1
    assert top_artists.count("Artist B") == 1
