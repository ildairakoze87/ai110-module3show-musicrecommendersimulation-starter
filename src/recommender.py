from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Experimental toggle: disable mood contribution to test sensitivity.
DISABLE_MOOD_MATCH = True


BASE_WEIGHTS = {
    "genre_match": 1.0,
    "mood_match": 1.0,
    "energy_similarity": 2.0,
    "acoustic_bonus": 0.5,
    "valence_similarity": 0.8,
    "liveness_similarity": 0.5,
    "speechiness_similarity": 0.5,
    "instrumentalness_similarity": 0.5,
    "popularity_similarity": 0.5,
    "decade_match": 0.6,
    "mood_tags_overlap": 0.7,
    "loudness_similarity": 0.4,
    "duration_similarity": 0.4,
    "explicitness_match": 0.3,
}


STRATEGY_MULTIPLIERS = {
    "balanced": {},
    "genre_first": {
        "genre_match": 2.0,
        "decade_match": 1.4,
        "energy_similarity": 0.8,
        "mood_tags_overlap": 0.8,
    },
    "mood_first": {
        "mood_match": 2.0,
        "mood_tags_overlap": 1.8,
        "valence_similarity": 1.2,
        "energy_similarity": 0.8,
    },
    "energy_focused": {
        "energy_similarity": 2.2,
        "loudness_similarity": 1.6,
        "duration_similarity": 1.3,
        "genre_match": 0.7,
        "mood_match": 0.8,
    },
}


def get_strategy_weights(ranking_strategy: str = "balanced") -> Dict[str, float]:
    """Return a weight map for the selected ranking strategy."""
    strategy = (ranking_strategy or "balanced").strip().lower()
    weights = BASE_WEIGHTS.copy()
    for feature, multiplier in STRATEGY_MULTIPLIERS.get(strategy, {}).items():
        weights[feature] = weights[feature] * multiplier
    return weights


def _diversity_adjusted_score(
    base_score: float,
    artist: str,
    genre: str,
    artist_counts: Dict[str, int],
    genre_counts: Dict[str, int],
    artist_penalty: float,
    genre_penalty: float,
) -> Tuple[float, float, float]:
    """Apply repeat penalties for artist/genre based on already-selected songs."""
    artist_repeat_penalty = artist_counts.get(artist, 0) * artist_penalty
    genre_repeat_penalty = genre_counts.get(genre, 0) * genre_penalty
    adjusted_score = base_score - artist_repeat_penalty - genre_repeat_penalty
    return adjusted_score, artist_repeat_penalty, genre_repeat_penalty


def _apply_diversity_penalty_to_dict_results(
    scored_songs: List[Tuple[Dict, float, List[str]]],
    k: int,
    max_songs_per_artist: int = 2,
    max_songs_per_genre: int = 3,
    artist_penalty: float = 0.35,
    genre_penalty: float = 0.20,
) -> List[Tuple[Dict, float, str]]:
    """Greedy reranker that discourages repeated artists and genres in top-k."""
    remaining = list(scored_songs)
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    selected: List[Tuple[Dict, float, str]] = []

    while remaining and len(selected) < k:
        best_index = None
        best_adjusted = float("-inf")
        best_artist_penalty = 0.0
        best_genre_penalty = 0.0

        for idx, (song, base_score, _) in enumerate(remaining):
            artist = str(song.get("artist", "unknown"))
            genre = str(song.get("genre", "unknown"))
            if artist_counts.get(artist, 0) >= max_songs_per_artist:
                continue
            if genre_counts.get(genre, 0) >= max_songs_per_genre:
                continue

            adjusted_score, artist_repeat_penalty, genre_repeat_penalty = _diversity_adjusted_score(
                base_score,
                artist,
                genre,
                artist_counts,
                genre_counts,
                artist_penalty,
                genre_penalty,
            )
            if adjusted_score > best_adjusted:
                best_adjusted = adjusted_score
                best_index = idx
                best_artist_penalty = artist_repeat_penalty
                best_genre_penalty = genre_repeat_penalty

        # If constraints are too strict for remaining songs, back off and fill by adjusted score only.
        if best_index is None:
            for idx, (song, base_score, _) in enumerate(remaining):
                adjusted_score, artist_repeat_penalty, genre_repeat_penalty = _diversity_adjusted_score(
                    base_score,
                    str(song.get("artist", "unknown")),
                    str(song.get("genre", "unknown")),
                    artist_counts,
                    genre_counts,
                    artist_penalty,
                    genre_penalty,
                )
                if adjusted_score > best_adjusted:
                    best_adjusted = adjusted_score
                    best_index = idx
                    best_artist_penalty = artist_repeat_penalty
                    best_genre_penalty = genre_repeat_penalty

        song, _, reasons = remaining.pop(best_index)
        artist = str(song.get("artist", "unknown"))
        genre = str(song.get("genre", "unknown"))
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

        reason_items = list(reasons)
        if best_artist_penalty > 0:
            reason_items.append(f"artist diversity penalty (-{best_artist_penalty:.2f})")
        if best_genre_penalty > 0:
            reason_items.append(f"genre diversity penalty (-{best_genre_penalty:.2f})")

        selected.append((song, round(best_adjusted, 3), ", ".join(reason_items) if reason_items else "general fit"))

    return selected


def _apply_diversity_penalty_to_song_results(
    scored_songs: List[Tuple[Song, float]],
    k: int,
    max_songs_per_artist: int = 2,
    max_songs_per_genre: int = 3,
    artist_penalty: float = 0.35,
    genre_penalty: float = 0.20,
) -> List[Song]:
    """Greedy reranker for OOP path with the same artist/genre diversity policy."""
    remaining = list(scored_songs)
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    selected: List[Song] = []

    while remaining and len(selected) < k:
        best_index = None
        best_adjusted = float("-inf")

        for idx, (song, base_score) in enumerate(remaining):
            if artist_counts.get(song.artist, 0) >= max_songs_per_artist:
                continue
            if genre_counts.get(song.genre, 0) >= max_songs_per_genre:
                continue
            adjusted_score, _, _ = _diversity_adjusted_score(
                base_score,
                song.artist,
                song.genre,
                artist_counts,
                genre_counts,
                artist_penalty,
                genre_penalty,
            )
            if adjusted_score > best_adjusted:
                best_adjusted = adjusted_score
                best_index = idx

        if best_index is None:
            for idx, (song, base_score) in enumerate(remaining):
                adjusted_score, _, _ = _diversity_adjusted_score(
                    base_score,
                    song.artist,
                    song.genre,
                    artist_counts,
                    genre_counts,
                    artist_penalty,
                    genre_penalty,
                )
                if adjusted_score > best_adjusted:
                    best_adjusted = adjusted_score
                    best_index = idx

        song, _ = remaining.pop(best_index)
        artist_counts[song.artist] = artist_counts.get(song.artist, 0) + 1
        genre_counts[song.genre] = genre_counts.get(song.genre, 0) + 1
        selected.append(song)

    return selected


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    liveness: float = 0.0
    speechiness: float = 0.0
    instrumentalness: float = 0.0
    popularity_100: int = 0
    release_decade: str = "unknown"
    mood_tags: str = ""
    loudness_db: float = 0.0
    duration_sec: int = 0
    explicitness_0_1: int = 0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None
    target_liveness: Optional[float] = None
    target_speechiness: Optional[float] = None
    target_instrumentalness: Optional[float] = None
    target_popularity_100: Optional[int] = None
    preferred_release_decade: Optional[str] = None
    preferred_mood_tags: Optional[List[str]] = None
    target_loudness_db: Optional[float] = None
    target_duration_sec: Optional[int] = None
    prefers_explicit: Optional[bool] = None


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        ranking_strategy: str = "balanced",
        max_songs_per_artist: int = 2,
        max_songs_per_genre: int = 3,
        artist_penalty: float = 0.35,
        genre_penalty: float = 0.20,
    ) -> List[Song]:
        scored_songs = []
        for song in self.songs:
            score, _ = score_song(
                self._profile_to_prefs(user),
                self._song_to_dict(song),
                ranking_strategy=ranking_strategy,
            )
            scored_songs.append((song, score))

        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return _apply_diversity_penalty_to_song_results(
            scored_songs,
            k,
            max_songs_per_artist=max_songs_per_artist,
            max_songs_per_genre=max_songs_per_genre,
            artist_penalty=artist_penalty,
            genre_penalty=genre_penalty,
        )

    def explain_recommendation(self, user: UserProfile, song: Song, ranking_strategy: str = "balanced") -> str:
        score, reasons = score_song(
            self._profile_to_prefs(user),
            self._song_to_dict(song),
            ranking_strategy=ranking_strategy,
        )
        if not reasons:
            return f"This song fits the profile with a score of {score:.2f}."
        explanation = ", ".join(reasons)
        return f"Score {score:.2f}: {explanation}."

    @staticmethod
    def _profile_to_prefs(user: UserProfile) -> Dict[str, object]:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "valence": user.target_valence,
            "liveness": user.target_liveness,
            "speechiness": user.target_speechiness,
            "instrumentalness": user.target_instrumentalness,
            "popularity_100": user.target_popularity_100,
            "release_decade": user.preferred_release_decade,
            "mood_tags": user.preferred_mood_tags,
            "loudness_db": user.target_loudness_db,
            "duration_sec": user.target_duration_sec,
            "prefers_explicit": user.prefers_explicit,
        }

    @staticmethod
    def _song_to_dict(song: Song) -> Dict[str, object]:
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "liveness": song.liveness,
            "speechiness": song.speechiness,
            "instrumentalness": song.instrumentalness,
            "popularity_100": song.popularity_100,
            "release_decade": song.release_decade,
            "mood_tags": song.mood_tags,
            "loudness_db": song.loudness_db,
            "duration_sec": song.duration_sec,
            "explicitness_0_1": song.explicitness_0_1,
        }


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of typed dictionaries."""
    print(f"Loading songs from {csv_path}...")
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        songs = []
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    "liveness": float(row.get("liveness", 0.0)),
                    "speechiness": float(row.get("speechiness", 0.0)),
                    "instrumentalness": float(row.get("instrumentalness", 0.0)),
                    "popularity_100": int(row.get("popularity_100", 0)),
                    "release_decade": row.get("release_decade", "unknown"),
                    "mood_tags": row.get("mood_tags", ""),
                    "loudness_db": float(row.get("loudness_db", 0.0)),
                    "duration_sec": int(row.get("duration_sec", 0)),
                    "explicitness_0_1": int(row.get("explicitness_0_1", 0)),
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict, ranking_strategy: str = "balanced") -> Tuple[float, List[str]]:
    """Score one song against user preferences and return score plus reasons."""
    score = 0.0
    reasons: List[str] = []

    weights = get_strategy_weights(ranking_strategy)

    preferred_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    preferred_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("energy") or user_prefs.get("target_energy")
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    target_valence = user_prefs.get("valence") or user_prefs.get("target_valence")
    target_liveness = user_prefs.get("liveness") or user_prefs.get("target_liveness")
    target_speechiness = user_prefs.get("speechiness") or user_prefs.get("target_speechiness")
    target_instrumentalness = user_prefs.get("instrumentalness") or user_prefs.get("target_instrumentalness")
    target_popularity_100 = user_prefs.get("popularity_100") or user_prefs.get("target_popularity_100")
    preferred_release_decade = user_prefs.get("release_decade") or user_prefs.get("preferred_release_decade")
    preferred_mood_tags = user_prefs.get("mood_tags") or user_prefs.get("preferred_mood_tags")
    target_loudness_db = user_prefs.get("loudness_db") or user_prefs.get("target_loudness_db")
    target_duration_sec = user_prefs.get("duration_sec") or user_prefs.get("target_duration_sec")
    prefers_explicit = user_prefs.get("prefers_explicit")

    if preferred_genre and song.get("genre") == preferred_genre:
        points = weights["genre_match"]
        score += points
        reasons.append(f"genre match (+{points:.1f})")

    if (not DISABLE_MOOD_MATCH) and preferred_mood and song.get("mood") == preferred_mood:
        points = weights["mood_match"]
        score += points
        reasons.append(f"mood match (+{points:.1f})")

    if target_energy is not None:
        energy_similarity = max(0.0, 1.0 - abs(float(song.get("energy", 0.0)) - float(target_energy)))
        points = energy_similarity * weights["energy_similarity"]
        score += points
        reasons.append(f"energy similarity (+{points:.2f})")

    if likes_acoustic is not None:
        acousticness = float(song.get("acousticness", 0.0))
        if likes_acoustic:
            if acousticness >= 0.6:
                points = weights["acoustic_bonus"]
                score += points
                reasons.append(f"acoustic preference match (+{points:.1f})")
        else:
            if acousticness < 0.5:
                points = weights["acoustic_bonus"]
                score += points
                reasons.append(f"acoustic preference match (+{points:.1f})")

    if target_valence is not None:
        valence_similarity = max(0.0, 1.0 - abs(float(song.get("valence", 0.0)) - float(target_valence)))
        points = valence_similarity * weights["valence_similarity"]
        score += points
        reasons.append(f"valence similarity (+{points:.2f})")

    if target_liveness is not None:
        liveness_similarity = max(0.0, 1.0 - abs(float(song.get("liveness", 0.0)) - float(target_liveness)))
        points = liveness_similarity * weights["liveness_similarity"]
        score += points
        reasons.append(f"liveness similarity (+{points:.2f})")

    if target_speechiness is not None:
        speechiness_similarity = max(0.0, 1.0 - abs(float(song.get("speechiness", 0.0)) - float(target_speechiness)))
        points = speechiness_similarity * weights["speechiness_similarity"]
        score += points
        reasons.append(f"speechiness similarity (+{points:.2f})")

    if target_instrumentalness is not None:
        instrumentalness_similarity = max(0.0, 1.0 - abs(float(song.get("instrumentalness", 0.0)) - float(target_instrumentalness)))
        points = instrumentalness_similarity * weights["instrumentalness_similarity"]
        score += points
        reasons.append(f"instrumentalness similarity (+{points:.2f})")

    if target_popularity_100 is not None:
        popularity_similarity = max(0.0, 1.0 - abs(float(song.get("popularity_100", 0.0)) - float(target_popularity_100)) / 100.0)
        points = popularity_similarity * weights["popularity_similarity"]
        score += points
        reasons.append(f"popularity similarity (+{points:.2f})")

    if preferred_release_decade and str(song.get("release_decade", "")).lower() == str(preferred_release_decade).lower():
        points = weights["decade_match"]
        score += points
        reasons.append(f"release decade match (+{points:.1f})")

    if preferred_mood_tags:
        if isinstance(preferred_mood_tags, str):
            pref_tags = {tag.strip().lower() for tag in preferred_mood_tags.split("|") if tag.strip()}
        else:
            pref_tags = {str(tag).strip().lower() for tag in preferred_mood_tags if str(tag).strip()}
        song_tags = {tag.strip().lower() for tag in str(song.get("mood_tags", "")).split("|") if tag.strip()}
        if pref_tags and song_tags:
            overlap = len(pref_tags & song_tags) / len(pref_tags)
            points = overlap * weights["mood_tags_overlap"]
            score += points
            reasons.append(f"mood tags overlap (+{points:.2f})")

    if target_loudness_db is not None:
        loudness_similarity = max(0.0, 1.0 - abs(float(song.get("loudness_db", 0.0)) - float(target_loudness_db)) / 20.0)
        points = loudness_similarity * weights["loudness_similarity"]
        score += points
        reasons.append(f"loudness similarity (+{points:.2f})")

    if target_duration_sec is not None:
        duration_similarity = max(0.0, 1.0 - abs(float(song.get("duration_sec", 0.0)) - float(target_duration_sec)) / 300.0)
        points = duration_similarity * weights["duration_similarity"]
        score += points
        reasons.append(f"duration similarity (+{points:.2f})")

    if prefers_explicit is not None:
        explicit_song = bool(int(song.get("explicitness_0_1", 0)))
        if bool(prefers_explicit) == explicit_song:
            points = weights["explicitness_match"]
            score += points
            reasons.append(f"explicitness match (+{points:.1f})")

    return round(score, 3), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    ranking_strategy: str = "balanced",
    max_songs_per_artist: int = 2,
    max_songs_per_genre: int = 3,
    artist_penalty: float = 0.35,
    genre_penalty: float = 0.20,
) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top-k recommendations with explanations."""
    scored_songs = [
        (song, score, reasons)
        for song in songs
        for score, reasons in [score_song(user_prefs, song, ranking_strategy=ranking_strategy)]
    ]
    ranked = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return _apply_diversity_penalty_to_dict_results(
        ranked,
        k,
        max_songs_per_artist=max_songs_per_artist,
        max_songs_per_genre=max_songs_per_genre,
        artist_penalty=artist_penalty,
        genre_penalty=genre_penalty,
    )
