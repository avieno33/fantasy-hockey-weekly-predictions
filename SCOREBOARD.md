# Scoreboard

Running record of every prediction made, checked against real
outcomes once games are played. This is the actual test of the model,
everything else confirms the math is implemented correctly, this
confirms whether the predictions are any good.

## How to read this

Each prediction is logged with its stated confidence *before* the
games happen (see commit history/timestamps for proof), then updated
with the actual outcome afterward. "Correct" means the favored side
(probability > 50%) actually did outperform.

This isn't about being "right" every time, a well-calibrated 65%
prediction should be wrong about a third of the time. What matters is
whether, in aggregate, predictions at a given confidence level land
that often. See the Calibration Summary section below.

---

## Calibration summary

Updated as predictions resolve. Not enough data yet to compute this
meaningfully, needs enough predictions to fill each confidence bucket.

| Confidence bucket | Predictions | Correct | Actual hit rate |
|---|---|---|---|
| 50-60% | — | — | — |
| 60-70% | — | — | — |
| 70-80% | — | — | — |
| 80%+ | — | — | — |

A well-calibrated model's 60-70% bucket should resolve correct
roughly 60-70% of the time, not 90%, not 40%. Once there's enough data
here, this becomes the honest answer to "is this model good," see
METHODOLOGY.md's calibration-driven correction roadmap item.

---

## Week 1

Logged before puck drop, season opens Sept 29, 2026. League 1 hasn't
drafted yet, excluded this week.

### My picks

| League | Position | My Player | Opponent | P(mine wins) | Result | Correct? |
|---|---|---|---|---|---|---|
| League 2 | LW | Tim Stutzle | Will Smith | 64.1% | pending | pending |
| League 3 | C | Connor McDavid | Brady Tkachuk | 63.1% | pending | pending |
| League 3 | RW | Porter Martone | Logan Stankoven | 73.8% | pending | pending |

Notes at the time of the pick:
- **Tim Stutzle vs. Will Smith** and **Connor McDavid vs. Brady
  Tkachuk** are the two most trustworthy calls this week, both built
  on a full season of data for both players.
- **Porter Martone vs. Logan Stankoven** has the highest raw
  confidence, but treat with real caution, Martone has only 9 games
  of prior-season data (10 points), so this leans on a genuinely thin,
  noisy prior rather than an established one.

Full position-by-position breakdown (not just the 3 headline picks):
League 2 favored in 11 of 13 comparable slots (53.6% average edge),
League 3 favored in 11 of 17 (53.4% average edge). See
`notebooks/week01_matchup_calls.ipynb` for every comparison.

### Sleeper picks

| Player | Position | Leagues | Thesis | Result |
|---|---|---|---|---|
| Gabe Perreault | RW | League 2, 3 | Trending up (51-59% above own baseline), possible top-line role | pending |
| Chris Kreider | LW | League 2, 3 | Speculative, reported top-line practice reps in Montreal | pending |
| Bobby McMann | LW | League 2, 3 | Real, already-completed trade TOR → SEA, +0.5 pts/game since | pending |

All three under 17% rostered on Yahoo as of 09/17/26. Full reasoning
and plots in `notebooks/week01_matchup_calls.ipynb`.

### What to check next week

- Did Perreault's late-2025-26 trend (up) carry into real 2026-27
  games, and did any line change actually happen?
- Did Kreider's speculative top-line placement in Montreal materialize?
- Does McMann's Seattle bump hold up in real games?
- Two bugs were fixed while building week 1 (a name-typo mismatch,
  and a Carter Hart search-resolution issue), worth confirming no
  similar issue turns up with a new week's roster of names.
- Does the current prediction and sleeper format make sense (i.e., multiple League scoring make sense)?  

---
