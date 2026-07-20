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

To score a song, the recommender adds points when the song matches the user’s preferences. Genre and mood matches give the biggest boosts, while energy is scored by how close it is to the user’s target value. Acousticness is also used as a smaller signal for whether the user prefers more acoustic or less acoustic songs.

The recommender ranks all songs by total score and returns the highest-scoring ones. This makes the recommendations easy to explain because each result can be traced to a few clear reasons.

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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
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



