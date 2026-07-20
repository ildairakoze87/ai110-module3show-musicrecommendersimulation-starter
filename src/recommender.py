import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Experimental toggle: disable mood contribution to test sensitivity.
DISABLE_MOOD_MATCH = True


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


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = []
        for song in self.songs:
            score, _ = score_song(self._profile_to_prefs(user), self._song_to_dict(song))
            scored_songs.append((song, score))

        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = score_song(self._profile_to_prefs(user), self._song_to_dict(song))
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
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return score plus reasons."""
    score = 0.0
    reasons: List[str] = []

    # Finalized starter weighting recipe for the assignment.
    weights = {
        "genre_match": 1.0,
        "mood_match": 1.0,
        "energy_similarity": 2.0,
        "acoustic_bonus": 0.5,
        "valence_similarity": 0.8,
        "liveness_similarity": 0.5,
        "speechiness_similarity": 0.5,
        "instrumentalness_similarity": 0.5,
    }

    preferred_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    preferred_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("energy") or user_prefs.get("target_energy")
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    target_valence = user_prefs.get("valence") or user_prefs.get("target_valence")
    target_liveness = user_prefs.get("liveness") or user_prefs.get("target_liveness")
    target_speechiness = user_prefs.get("speechiness") or user_prefs.get("target_speechiness")
    target_instrumentalness = user_prefs.get("instrumentalness") or user_prefs.get("target_instrumentalness")

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

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top-k recommendations with explanations."""
    scored_songs = [
        (song, score, ", ".join(reasons) if reasons else "general fit")
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    ranked = sorted(scored_songs, key=lambda item: item[1], reverse=True)
    return ranked[:k]
