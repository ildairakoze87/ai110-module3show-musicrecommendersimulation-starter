# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeMap CLI Recommender 1.0

---

## 2. Goal / Task

This model suggests songs that match a user's taste profile. It predicts a ranked top-k list by comparing user preferences to song features.

---

## 3. Data Used

The dataset has 18 songs. Song features include genre, mood, energy, tempo_bpm, valence, danceability, and acousticness. The scoring logic also supports liveness, speechiness, and instrumentalness as optional numeric features.

Main limits: small catalog size, no lyrics understanding, no user history, and no popularity or recency signals.

---

## 4. Algorithm Summary

Each song starts with score 0. The model adds fixed points for genre match and mood match. It then adds similarity points for numeric features based on closeness to target values, especially energy.

After scoring every song, it sorts from highest to lowest and returns the top-k. It also returns reason strings with point values so the ranking is explainable.

---

## 5. Observed Behavior / Biases

A clear weakness is energy dominance in some runs. When profile preferences conflict, songs with very close energy values can rank above songs that feel like better mood matches. This can create a filter-bubble effect around one target energy band.

Another bias is category fallback: if a user asks for genre or mood labels that do not exist in the dataset, the model becomes mostly numeric and results feel less personalized.

---

## 6. Evaluation Process

I tested seven profiles:

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Adversarial: Conflicting Mood vs Energy
- Adversarial: Genre Lock-In Test
- Adversarial: Acoustic Contradiction
- Adversarial: Nonexistent Category

I compared top-5 outputs and reason strings for each profile. I also ran a logic experiment by shifting weights (energy up, genre down) and by disabling mood contribution.

Top-5 snapshots:

- High-Energy Pop: Sunrise City, Gym Hero, Rooftop Lights, Caribbean Moonlight, Velvet Boulevard
- Chill Lofi: Midnight Coding, Library Rain, Focus Flow, Spacewalk Thoughts, Afterglow Park
- Deep Intense Rock: Storm Runner, Gym Hero, Iron Harbor, Neon Skyline, Night Drive Loop
- Adversarial: Conflicting Mood vs Energy: Storm Runner, Midnight Coding, Library Rain, Spacewalk Thoughts, Iron Harbor
- Adversarial: Genre Lock-In Test: Storm Runner, Midnight Coding, Focus Flow, Library Rain, Gym Hero
- Adversarial: Acoustic Contradiction: Winter Orchard, Spacewalk Thoughts, Night Drive Loop, Rooftop Lights, Library Rain
- Adversarial: Nonexistent Category: Golden Hour Echo, Midnight Orchard, Coffee Shop Stories, Afterglow Park, Focus Flow


What changed: rankings became more energy-driven. This made some lists less emotionally intuitive even when they were numerically consistent.

Pairwise comments (plain language):

- High-Energy Pop vs Chill Lofi: Pop lifts upbeat tracks; Chill Lofi shifts to softer low-energy tracks.
- High-Energy Pop vs Deep Intense Rock: Both like high energy, but Rock pushes Storm Runner higher because genre and intensity match.
- High-Energy Pop vs Conflicting Mood/Energy: Conflicting profile still favors intense tracks because high target energy dominates.
- High-Energy Pop vs Genre Lock-In: Lock-In keeps some lofi tracks high even with high energy, showing genre boost can bend results.
- High-Energy Pop vs Acoustic Contradiction: Contradiction profile moves away from pop feel and toward classical/serene alignment.
- High-Energy Pop vs Nonexistent Category: With missing labels, outputs become generic numeric matches.
- Chill Lofi vs Deep Intense Rock: Lofi favors calm acoustic texture; Rock favors aggressive high-energy texture.
- Chill Lofi vs Conflicting Mood/Energy: Conflicting profile pulls in hotter tracks than Chill Lofi due to energy target.
- Chill Lofi vs Genre Lock-In: Both keep lofi songs high, but Lock-In feels less relaxed because intense preference shifts ranking.
- Chill Lofi vs Acoustic Contradiction: One rewards acoustic feel; the other conflicts with it, so lists diverge.
- Chill Lofi vs Nonexistent Category: Missing labels remove the clear lofi identity and increase generic results.
- Deep Intense Rock vs Conflicting Mood/Energy: Both can place Storm Runner high, but conflicting profile adds mixed mood behavior.
- Deep Intense Rock vs Genre Lock-In: Lock-In keeps lofi tracks competitive against expected rock-heavy ranking.
- Deep Intense Rock vs Acoustic Contradiction: Acoustic Contradiction elevates Winter Orchard unlike the rock profile.
- Deep Intense Rock vs Nonexistent Category: No category anchors means a less stylistically focused list.
- Conflicting Mood/Energy vs Genre Lock-In: Conflicting profile rewards raw energy; Lock-In rewards genre consistency.
- Conflicting Mood/Energy vs Acoustic Contradiction: First favors very high energy; second favors classical/serene cues.
- Conflicting Mood/Energy vs Nonexistent Category: Nonexistent category profile is more generic because labels do not match.
- Genre Lock-In vs Acoustic Contradiction: Lock-In repeatedly surfaces lofi; Acoustic Contradiction favors a different sound palette.
- Genre Lock-In vs Nonexistent Category: Lock-In uses labels; Nonexistent Category cannot, so it defaults to numeric closeness.
- Acoustic Contradiction vs Nonexistent Category: Contradiction still has valid category anchors; Nonexistent Category mostly does not.

Why Gym Hero keeps showing up for Happy Pop:

Gym Hero is pop and has very high energy, so it earns strong points even if mood is not a perfect match. In plain terms, the system reads it as very close to the target vibe because weighted features are aligned.

---

## 7. Intended Use and Non-Intended Use

Intended use:

- classroom learning
- experimenting with recommender design
- understanding scoring tradeoffs and bias

Non-intended use:

- real production recommendation for large user bases
- high-stakes decisions
- personalized recommendations without user history and richer data

---

## 8. Ideas for Improvement

1. Add input validation and normalization for all numeric targets.
2. Add diversity controls so top-k is not dominated by similar songs.
3. Add lightweight history signals (likes/skips) to reduce generic numeric fallback behavior.

---

## 9. Personal Reflection

My biggest learning moment was seeing how one small weight change can completely reorder the top recommendations. I learned that "simple" scoring rules are still powerful, and that tiny math choices can change user experience a lot.

AI tools helped me move faster when drafting scoring logic, generating profile ideas, and writing documentation. I still had to double-check AI suggestions by running the code, inspecting the ranking outputs, and verifying that explanations matched the actual points.

What surprised me most is that simple rules can still feel personal when they align with user preferences like genre, mood, and energy. Even without complex machine learning, the system often produced recommendations that felt believable.

If I extend this project, I would add input validation, stronger diversity controls, and a feedback loop using likes/skips so recommendations adapt over time instead of relying only on a fixed profile.
