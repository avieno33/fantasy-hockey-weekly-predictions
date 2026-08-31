# Fantasy Hockey Matchup Analyzer

**[Live demo →](#)** *(link goes here once deployed)*

A tool that answers a question most fantasy hockey apps don't: not just "who scores more points," but **how confident should you be**, and **where is your team actually vulnerable this week**.

## The problem

Most fantasy platforms project a single point value per player per week and call it a day. That throws away information: a player who's consistently good and a player who's boom-or-bust can have the same average projection but very different real value depending on whether you're trying to protect a lead or need a ceiling play. Standard tools also assume a fixed scoring system, which breaks down the moment your league uses custom categories or weights.

This tool models each player's output as a **distribution** (expected value + volatility), not a point estimate, and uses that to generate probabilistic, explainable recommendations for lineup decisions, goalie starts, and full-roster matchups — under whatever scoring system your league actually uses.

## What it does (current version)

- **Custom scoring support** — define your league's scoring rules (points per goal, assist, shot, save, etc.) and every analysis below runs against *your* league's math, not a generic default.
- **Matchup Analyzer** — compare two players (or two full lineups) and get a probability-based recommendation, with the underlying stats shown, not just a verdict.
- **Goalie start/sit** — factors in back-to-back starts, opponent scoring rate, and home/away splits.
- **Team-level matchup view** — input your roster and your opponent's roster for the week; get an overall win-probability estimate for the matchup, plus a breakdown of which positions you're favored or exposed at.

## How it works (the short version)

1. Pull raw per-game stats from the NHL's public API.
2. Apply your league's scoring config to convert raw stats into fantasy points per game.
3. Compute a rolling expected value (μ) and volatility (σ) per player, weighting recent games more heavily.
4. Normalize across positions using z-scores, so a 2-point defenseman and a 2-point winger aren't treated as equivalent.
5. Compare any two players (or two full rosters, summed) using a probability model: *what's the chance A outproduces B this week*, given both their expected value and their volatility.

Full methodology, including the statistical reasoning and the simplifying assumptions I made deliberately (and why), is in [`METHODOLOGY.md`](#).

## Tech stack

- **Data:** NHL public API, pandas for all transformation and analysis
- **Interface:** Streamlit (deployed via Streamlit Community Cloud)
- **No black-box modeling in this version** — every number the tool outputs is traceable back to a stat you could look up yourself. That's intentional at this stage; see the roadmap below for where modeling comes in.

## Example

*(Once built: a screenshot or worked example goes here — e.g., "Week 3: tool flagged Goalie X as a sit due to a back-to-back on the road against a top-5 offense; Goalie X posted a .870 SV% that night.")*

## Roadmap — what's next this season

This project is scoped deliberately: get a defensible, explainable statistical core shipped before the season starts, then layer in more sophisticated methods as more of the season's data becomes available to work with. Rough progression:

- [ ] **Waiver wire trend detector** — flag players trending up relative to their own baseline and to their rostered %, using the same rolling-stat pipeline as the matchup analyzer. Not a "breakout predictor" — a trend signal.
- [ ] **Projection model** — a simple, interpretable regression (not a black box) to improve the expected-value estimate using features beyond rolling average, e.g. ice time, shot rate, opponent strength. Feeds into the same downstream probability framework — doesn't replace it.
- [ ] **Category league support** — extend custom scoring to head-to-head category formats, not just points leagues.
- [ ] **Decision feedback loop** — log each recommendation's predicted confidence and the actual outcome, then check calibration over the season (did "70% confidence" calls actually hit ~70% of the time?). Requires a full season of logged decisions to be meaningful, which is why it's last.

## Known simplifications

Being upfront about the modeling choices:
- Player performance is treated as approximately normally distributed for the probability comparisons. Real point totals are more right-skewed (mostly low counts, occasional big games) — a fine approximation at this scope, but not literally accurate.
- Team-level variance is computed assuming rough independence across players' individual performances. Line combinations and game flow violate this a bit in reality; treated as a reasonable simplification rather than something correctable at this scope.

## Running it locally

```bash
git clone <repo-url>
cd fantasy-hockey-analyzer
pip install -r requirements.txt
streamlit run app.py
```
