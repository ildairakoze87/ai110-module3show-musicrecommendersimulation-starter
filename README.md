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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



