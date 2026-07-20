# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version builds a simple content-based music recommender that suggests songs by matching a user’s taste profile to song attributes such as genre, mood, energy, acousticness, and a few additional numeric features like liveness, speechiness, and instrumentalness.

---

## How The System Works

This system uses a simple content-based recommender. Each song is described by features such as genre, mood, energy, valence, tempo, acousticness, liveness, speechiness, and instrumentalness. The user profile stores a preferred genre, preferred mood, target energy level, and a preference for acoustic or non-acoustic songs, plus optional targets for the new numeric features.

### Plan (Data Flow)

- Input: User preferences (favorite genre, favorite mood, target energy, and optional numeric targets)
- Process: Loop through every song in the CSV and compute a song score using the scoring rules
- Output: Sort all songs by score and return the Top K recommendations

### Finalized Algorithm Recipe

For each song:

1. Start with score = 0.
2. Add +2.0 if the song genre matches the user favorite genre.
3. Add +1.0 if the song mood matches the user favorite mood.
4. Add an energy similarity score, where:
   similarity = 1.0 - abs(song_energy - target_energy)
5. Add smaller tie-breaker contributions from acousticness, valence, liveness, speechiness, and instrumentalness when those user targets/preferences are provided.
6. After scoring all songs, rank them from highest to lowest and return the Top K.

This setup keeps the logic explainable: each recommendation can be traced to exact matching and similarity terms.

### Potential Biases

This system might over-prioritize genre and under-recommend songs outside the user favorite genre, even when those songs match mood and energy very well. It may also reflect dataset bias if some genres or moods are underrepresented in the catalog.

At a larger scale, real recommender systems usually combine this kind of content matching with user-interaction data such as listens, skips, likes, and playlists. They often learn patterns from millions of users and songs, then update recommendations continuously as behavior changes.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

4. Choose a ranking strategy mode:

```bash
python -m src.main --mode balanced
python -m src.main --mode genre_first
python -m src.main --mode mood_first
python -m src.main --mode energy_focused
python -m src.main --mode all
```

Available modes:

- balanced: default blend of all features
- genre_first: stronger weight on genre/decade alignment
- mood_first: stronger weight on mood and mood-tag alignment
- energy_focused: stronger weight on energy and intensity features

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

```text
Loading songs from data/songs.csv...

===============================================================
Top Recommendations
===============================================================

1. Midnight Coding - LoRoom
   Final Score : 6.25
   Reasons     :
   - genre match (+2.0)
   - mood match (+1.0)
   - energy similarity (+1.00)
   - acoustic preference match (+0.5)
   - valence similarity (+0.75)
   - liveness similarity (+0.38)
   - speechiness similarity (+0.45)
   - instrumentalness similarity (+0.17)

2. Library Rain - Paper Lanterns
   Final Score : 6.21
   Reasons     :
   - genre match (+2.0)
   - mood match (+1.0)
   - energy similarity (+0.93)
   - acoustic preference match (+0.5)
   - valence similarity (+0.78)
   - liveness similarity (+0.38)
   - speechiness similarity (+0.45)
   - instrumentalness similarity (+0.17)

3. Focus Flow - LoRoom
   Final Score : 5.26
   Reasons     :
   - genre match (+2.0)
   - energy similarity (+0.98)
   - acoustic preference match (+0.5)
   - valence similarity (+0.78)
   - liveness similarity (+0.38)
   - speechiness similarity (+0.45)
   - instrumentalness similarity (+0.17)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

I tested three normal profiles and four adversarial profiles:

- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Adversarial: Conflicting Mood vs Energy
- Adversarial: Genre Lock-In Test
- Adversarial: Acoustic Contradiction
- Adversarial: Nonexistent Category

Observed behavior:

- The top song changed across normal profiles, showing the model can adapt by profile.
- Chill Lofi results felt intuitive, with Midnight Coding and Library Rain ranked highest.
- In conflicting/adversarial cases, high-energy or exact genre signals could still dominate, exposing expected tradeoffs in fixed-weight scoring.
- When genre/mood categories were missing from the dataset, ranking fell back to numeric similarity and acoustic preference.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

This project helped me understand how recommenders transform profile data into ranked decisions. With only a few weighted rules, the system produced believable outputs for very different profiles, especially for Chill Lofi and High-Energy Pop.

I also learned that fairness and robustness issues appear quickly in simple systems. Adversarial profiles exposed how fixed weights can over-prioritize one preference and produce less intuitive results when user preferences conflict. That made the tradeoff between explainability and flexibility very clear.



