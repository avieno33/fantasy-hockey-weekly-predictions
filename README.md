# Fantasy Hockey Weekly Predictions

Like many sports fans, I love fantasy sports, whether it be hockey, baseball, basketball, or football, I cannot wait for the next season to start, and to draft my favourite players. But also like many sports fans, my results are wildly inconsistent. Some seasons I go 16-5 and win my league with ease, other seasons I go 6-15 and barely scrape into the playoffs. That inconsistency got me thinking, what if I put my math degree to actual use, dust off and sharpen my statistical skills, and build something that could genuinely help. With hockey season approaching fast, that seemed like the obvious place to start.

The idea is a running, public record of weekly fantasy hockey predictions, built on a probabilistic statistical model, tracked against real outcomes, and revised openly as the season goes on.

## The idea

Most fantasy hockey tools give you a single projected point value per player and stop there. This project does four things differently:

1. **It models uncertainty, not just an average.** Every prediction comes with an explicit confidence level, based on both a player's expected performance and how consistent (or volatile) that performance has been, not just "Player A should score more," but "Player A has roughly a 70% chance of outproducing Player B this week."
2. **It adapts to your league's actual scoring, not a generic default.** Scoring rules are configurable (goals, assists, hits, blocks, powerplay points, and more), validated against a fixed set of real Yahoo fantasy hockey categories rather than assumed to be standard.
3. **It adjusts for matchup context, when the evidence actually supports it.** Goalie projections account for the opponent's typical shot volume, based on a real, tested relationship between shots faced and save percentage, not just intuition. An intuitive-sounding adjustment (goalies performing worse on back-to-backs) was tested the same way and didn't hold up statistically, so it isn't included, being willing to *not* build something the data doesn't support is as much a part of this project as building what it does.
4. **It's honest about being wrong, on the record.** Each week, I make 2-3 concrete calls, which players or goalies I expect to perform well, log them *before* the games happen, and then go back afterward to check the outcome against the prediction. When a call misses, I look at whether it was normal variance (the model expected some chance of that) or an actual gap in the model, and only change the model in response to the latter.

The result is a season-long, dated log of predictions, outcomes, and reasoning, not a one-off tool, but a visible practice of building and refining a statistical model in public.

## What this project is (and isn't)

- **Is:** a fantasy hockey performance model, predicting which players/goalies are likely to outperform others, with a stated confidence level.
- **Isn't:** a game-outcome predictor (who wins the actual NHL game). That's a different, harder problem requiring team-strength modeling, and it's intentionally out of scope here so the project stays focused and well-calibrated rather than stretched thin.

## Where to start

`notebooks/00_building_the_model.ipynb` builds and explains the base statistical model from the ground up, data pull, scoring, cleaning, the math behind the confidence estimates, and the goalie matchup adjustment, including the statistical testing behind each decision. It's meant to be read, not just run. Every weekly prediction notebook builds on what's established there.

## How a week works

1. **Predict:** Before games are played, pick 2-3 players or goalies to call (e.g., "Goalie X is a strong start this week," "Player A over Player B for your active roster spot"), each with the underlying stats and a stated confidence level.
2. **Log:** Commit the notebook with the prediction and timestamp before puck drop, so there's a clear, provable record that the call was made in advance.
3. **Review:** After the games, revisit the same notebook (or the next week's) and record what actually happened.
4. **Diagnose:** For any miss, explicitly assess whether it fell within the model's expected variance or represents a real gap in the model's reasoning.
5. **Iterate (when warranted):** Only make a model change when there's a pattern across multiple weeks, not a reaction to a single result. Every change is logged with a reason.

See `METHODOLOGY.md` for the full statistical model behind this and how it's expected to evolve.

## Repo structure

```
notebooks/           00_building_the_model.ipynb (the base model, start here),
                      then one notebook per week - prediction, then outcome review
src/                  Reusable model functions (data pull, scoring, stats, matchup
                      comparison), imported into each week's notebook
tests/                test_src.ipynb, regression tests confirming src/ reproduces
                      known-good results from the base notebook
config/               Scoring configuration(s) used to convert raw stats into fantasy points
data/                 Cached raw stat pulls (not committed in full, see .gitignore)
SCOREBOARD.md         Running tally of predictions vs. outcomes and confidence calibration
METHODOLOGY.md        The statistical model, its assumptions, and planned improvements
future_directions/    Notes on extensions being considered, tested and shelved, or planned
```

## Status

Season-long, ongoing project. New notebook published weekly. `SCOREBOARD.md` reflects the latest tally.

## Running it

Notebooks are built and run in Google Colab, open `00_building_the_model.ipynb` directly from the GitHub repo in Colab (File → Open notebook → GitHub, paste the repo URL), no local setup required. They can also be run locally with Jupyter if you have `pandas`, `numpy`, `scipy`, `requests`, and `matplotlib` installed, though a couple of upload-based cells (custom scoring config) are Colab-specific and would need adapting.
