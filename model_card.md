# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeMap CLI Recommender 1.0

---

## 2. Intended Use

This recommender is designed for classroom exploration of content-based recommendation logic. It generates top-k song recommendations by matching a user taste profile to song features. It assumes the user can provide clear preferences like favorite genre, favorite mood, and target energy. It is not intended for production users.

---

## 3. How the Model Works

Each song is represented with features including genre, mood, energy, tempo, valence, danceability, acousticness, liveness, speechiness, and instrumentalness. The user profile provides preferred genre and mood, a target energy, and optional numeric targets plus an acoustic preference.

The model starts each song at score 0, then adds fixed points for genre and mood matches and similarity points for numeric features based on closeness to target values. It returns both a final score and human-readable reasons with point contributions, then ranks songs by score and returns the top-k.

---

## 4. Data

The catalog has 18 songs. It includes genres such as pop, lofi, rock, ambient, jazz, synthwave, indie pop, disco, folk, hip-hop, classical, salsa, and metal. Moods include happy, chill, intense, relaxed, moody, focused, romantic, nostalgic, rebellious, serene, upbeat, aggressive, dreamy, and bittersweet.

The dataset was expanded from the starter version to increase genre and mood coverage. The main missing pieces are lyrics, language, artist popularity trends, and long-term user interaction history.

---

## 5. Strengths

The model performs well for clearly defined profiles. For High-Energy Pop, Sunrise City and Gym Hero rank near the top. For Chill Lofi, Midnight Coding and Library Rain rank first and second. For Deep Intense Rock, Storm Runner ranks first.

These outcomes match intuition because genre and mood anchors combine with energy closeness and optional tie-breakers. The explanations are transparent and make it easy to see why a song was ranked highly.

---

## 6. Limitations and Bias

One weakness I found is that the system can over-prioritize energy closeness, especially in adversarial profiles where preferences conflict. In those tests, tracks with very close energy values often ranked above songs with better overall emotional fit, which made some outputs feel mechanically correct but musically less intuitive. This creates a filter-bubble effect where recommendations cluster around one numeric target instead of balancing style and mood. The issue is amplified by the small catalog size, because the same high-energy or low-energy songs reappear across different profiles.

---

## 7. Evaluation

I tested seven profiles:

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Adversarial: Conflicting Mood vs Energy
- Adversarial: Genre Lock-In Test
- Adversarial: Acoustic Contradiction
- Adversarial: Nonexistent Category

What surprised me was that the baseline model adapted well across the three core profiles, with different songs ranking first in each case, which was more robust than I expected for a small catalog. In conflicting/adversarial cases, energy closeness often dominated and pushed up songs that felt less emotionally aligned, revealing how sensitive rankings are to weight choices. When genre and mood did not exist in the dataset, the recommender still produced stable rankings by falling back to numeric similarity, but those outputs felt more generic and less personalized.

Profile-to-profile comparison notes (plain language):

Pairwise profile comments:

- High-Energy Pop vs Chill Lofi: High-Energy Pop lifts upbeat tracks, while Chill Lofi shifts toward calmer low-energy songs, which fits their opposite energy and mood targets.
- High-Energy Pop vs Deep Intense Rock: Both like strong energy, but Rock moves Storm Runner above pop tracks because genre and mood intensity fit better.
- High-Energy Pop vs Adversarial: Conflicting Mood vs Energy: The adversarial profile still pushes intense songs high because energy closeness beats the conflicting chill mood request.
- High-Energy Pop vs Adversarial: Genre Lock-In Test: The lock-in test keeps some lofi tracks high even at high energy, showing genre can still bend results away from pure pop.
- High-Energy Pop vs Adversarial: Acoustic Contradiction: The contradiction profile moves toward classical/serene signals and away from pop, so the list looks less party-like.
- High-Energy Pop vs Adversarial: Nonexistent Category: When labels do not exist, results become generic energy/valence matches instead of clear pop-focused picks.
- Chill Lofi vs Deep Intense Rock: Chill Lofi favors soft, acoustic-leaning songs, while Deep Intense Rock favors loud aggressive tracks, which is exactly what these profiles ask for.
- Chill Lofi vs Adversarial: Conflicting Mood vs Energy: The conflicting profile pulls in hotter tracks than Chill Lofi because high target energy overrides some chill intent.
- Chill Lofi vs Adversarial: Genre Lock-In Test: Both include lofi high in the list, but lock-in adds intense energy pressure, so the results feel less relaxed.
- Chill Lofi vs Adversarial: Acoustic Contradiction: Chill Lofi rewards acoustic texture, while Acoustic Contradiction penalizes it, producing very different mid-list songs.
- Chill Lofi vs Adversarial: Nonexistent Category: With missing labels, the system falls back to numbers and loses the clearly "lofi" feel.
- Deep Intense Rock vs Adversarial: Conflicting Mood vs Energy: Both can put Storm Runner first, but the conflicting profile introduces chill-tagged songs because mood and energy fight each other.
- Deep Intense Rock vs Adversarial: Genre Lock-In Test: Lock-in keeps lofi tracks competitive even with intense energy, showing genre boost can counter expected rock dominance.
- Deep Intense Rock vs Adversarial: Acoustic Contradiction: Acoustic Contradiction elevates Winter Orchard from classical/serene cues, unlike rock profile outputs.
- Deep Intense Rock vs Adversarial: Nonexistent Category: Nonexistent labels remove rock anchors, so ranking becomes mostly numeric similarity and feels less stylistically sharp.
- Adversarial: Conflicting Mood vs Energy vs Adversarial: Genre Lock-In Test: Conflicting profile rewards raw energy fit, while lock-in keeps genre-matched lofi tracks near the top.
- Adversarial: Conflicting Mood vs Energy vs Adversarial: Acoustic Contradiction: Conflicting profile favors very high-energy tracks; Acoustic Contradiction favors classical/serene plus low-acoustic preference.
- Adversarial: Conflicting Mood vs Energy vs Adversarial: Nonexistent Category: Conflicting profile still has useful labels, but Nonexistent Category has none, so outputs become more generic.
- Adversarial: Genre Lock-In Test vs Adversarial: Acoustic Contradiction: Lock-in repeatedly surfaces lofi tracks, while Acoustic Contradiction centers classical features and pushes a different sound palette.
- Adversarial: Genre Lock-In Test vs Adversarial: Nonexistent Category: Genre Lock-In is label-heavy, but Nonexistent Category cannot use labels, so it defaults to numeric closeness.
- Adversarial: Acoustic Contradiction vs Adversarial: Nonexistent Category: Both can look odd, but Acoustic Contradiction still has valid labels to anchor results, while Nonexistent Category has almost no categorical guidance.

Why Gym Hero keeps showing up for people who want Happy Pop:

Gym Hero has very high energy and is in the pop genre, so it earns strong points even if the mood is not an exact happy match. In simple terms, the model reads it as "very close to the target vibe" because energy and genre are weighted heavily.

---

## 8. Future Work

Next steps include adding input validation for out-of-range preference values, adding a diversity penalty to reduce repeated artist/genre dominance, and introducing lightweight normalization across features. I would also add profile blending (for mixed moods), plus a history-aware layer that adjusts recommendations using listens/skips.

---

## 9. Personal Reflection

This project showed me how quickly simple weighted rules can produce believable recommendations, especially when profile and feature design are clear. I also learned that explainability improves debugging: seeing per-feature point reasons made it much easier to understand ranking behavior.

The adversarial tests were the most useful part. They revealed that even a transparent model can behave unexpectedly when preferences conflict, which changed how I think about recommendation apps: good results depend as much on robust profile handling and data coverage as on the scoring formula itself.
