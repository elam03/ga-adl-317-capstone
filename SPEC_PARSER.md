# LLM Spec for data parsing

## Using Antigravity/Gemini 3.1 Pro

## Prompt

```txt
Write me a python parser which processes the data in `data/raw/games_detailed_info2025.csv` and saves the result in `data/processed/games_detailed_info2025.csv`. The parser should be written to `src/`, called `process_games_detailed_info2025.py`. I'm okay with hard-coding the relative paths into the python file.

It should output a csv with the following columns in this order:

- id
- name
- description
- boardgamecategory
- boardgamemechanic
- boardgamedesigner
- usersrated
- rating (average)
- bayes_rating (bayesaverage)
- num_comments
- playtime
- min_playtime
- max_playtime
```
