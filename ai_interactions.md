# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to iteratively build and refine a CLI-first music recommender, then document and evaluate it. The tasks included implementing scoring logic, expanding the dataset with richer attributes, running profile-based experiments, formatting outputs, and completing README/model card writeups.

**Prompts used:**

- "implement the load_songs function ... use Python's csv module ... numerical values ... converted to floats or integers"
- "format the output of your recommendations ... clean, readable layout ... song title, final score, reasons"
- "Define at least three distinct user preference dictionaries"
- "suggest adversarial or edge case user profiles"
- "Introduce 5 or more complex attributes to your dataset"
- "Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes"
- "Update the Evaluation section of your model_card.md"
- "Implement a diversity-penalty reranking rule: when selecting top recommendations, subtract a penalty from a candidate song if its artist already appears in the selected list (and optionally a smaller penalty for repeated genre), then pick the highest adjusted score each step."
- "Improve terminal output readability using tabulate or plain ASCII table formatting, and ensure each row includes song title, artist, score, and the reasons that explain that score."

**What did the agent generate or change?**

- Implemented/updated recommender pipeline in `src/recommender.py`:
	- CSV loading and typed parsing
	- weighted score computation
	- explainable reason strings with point values
	- ranking logic for top-k recommendations
	- diversity penalty reranking to discourage repeated artists/genres in top results
	- support for new attributes (`popularity_100`, `release_decade`, `mood_tags`, `loudness_db`, `duration_sec`, `explicitness_0_1`)
- Updated CLI workflow and profile runs in `src/main.py`:
	- multiple core profiles and adversarial profiles
	- readable terminal output blocks
- Expanded dataset in `data/songs.csv`:
	- additional songs
	- new complex columns and values
- Updated project docs:
	- `README.md` (algorithm recipe, experiments, sample output, reflection)
	- `model_card.md` (full phase-5 sections, evaluation and bias analysis)

Commands run by the agent included:
- `python -m src.main`
- `pytest -q`
- targeted Python sanity checks for score math and parsed field types

**What did you verify or fix manually?**

- Verified that tests still passed after each major edit (`pytest -q`).
- Verified runtime behavior with `python -m src.main` and checked profile-specific top-5 outputs.
- Checked that new CSV attributes were parsed with correct types (int/float/str).
- Reviewed recommendation quality with adversarial profiles and confirmed a real limitation: energy-heavy weighting can cause filter-bubble behavior.
- Cleaned documentation formatting after one accidental terminal-output paste into `README.md`.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern (simple mode-based strategy selection).

**How did AI help you brainstorm or implement it?**

I asked the AI to brainstorm a modular approach for supporting multiple ranking modes without duplicating the whole scoring function. The AI suggested a lightweight Strategy-style design where each ranking mode (balanced, genre-first, mood-first, energy-focused) behaves like a strategy that modifies feature weights while reusing one shared scoring pipeline.

The AI contribution was useful because it separated concerns clearly:
- core scoring math stays in one place
- mode-specific behavior is isolated to strategy configuration
- the CLI only selects a strategy name and passes it through

I then implemented that approach by introducing mode multipliers and a strategy-weight resolver so new ranking styles can be added with minimal code changes.

**How does the pattern appear in your final code?**

The pattern appears in `src/recommender.py` through:
- `BASE_WEIGHTS` as the default policy baseline
- `STRATEGY_MULTIPLIERS` as interchangeable strategy definitions
- `get_strategy_weights(ranking_strategy)` as the strategy selector/resolver
- `score_song(..., ranking_strategy=...)` and `recommend_songs(..., ranking_strategy=...)` that apply the chosen strategy without changing the scoring pipeline

It is exposed to users in `src/main.py` via `--mode` (`balanced`, `genre_first`, `mood_first`, `energy_focused`, or `all`). This keeps the code modular and makes strategy changes explicit and testable.
