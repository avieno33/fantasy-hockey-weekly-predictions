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

## Units

Week 1 probabilities were **per game** (one average game for each player). From Week 2 on, probabilities are **weekly totals**: they are scaled by each player's team games that week, and goalies by expected starts. "3g" in a label means team games that week, not starts. Week 1 is scored both ways below.

## Calibration summary (running)

| Confidence | Picks | Won | Hit rate |
|---|---|---|---|
| 50-60% | 23 | 10 | 43.5% |
| 60-70% | 6 | 2 | 33.3% |
| 70-80% | 1 | 0 | 0.0% |
| 80%+ | 0 | - | - |

Week 1 only so far (30 scored matchups). That is far too few to say anything about calibration, and each bucket is only a handful of coin flips. Lower confidence did not do worse than higher confidence, but nothing here is distinguishable from noise yet.

## Week 1

### Results

| Measure | Result | Brier |
|---|---|---|
| Per-game, all matchups | 12.0 of 30 (40.0%) | 0.269 |
| Weekly total, all matchups | 11.0 of 30 (36.7%) | 0.276 |
| Equal-games matchups only | 6.0 of 13 (46.2%) | 0.267 |

Average confidence on the equal-games subset was 57.6%. Brier reference: 0.25 is what always predicting 50% scores, so 0.269 is slightly worse than a coin flip on 30 matchups. Not enough to change the model.

Calibration bins from the notebook:

| Bin | n | Avg confidence | Hit rate |
|---|---|---|---|
| 50-55% | 15 | 52.3% | 26.7% |
| 55-60% | 8 | 56.9% | 75.0% |
| 60%+ | 7 | 63.9% | 28.6% |

### Headline picks

| Pick | League | Result |
|---|---|---|
| Tim Stützle | 2 | Lost, 2.90 vs 4.90 (he played 1 game, the opponent 2) |
| Connor McDavid | 3 | Won, 9.45 vs 1.22 |
| Porter Martone | 3 | Lost, 0.20 vs 1.32 |

### Sleepers (first games only)

| Player | Games | League 2 | League 3 |
|---|---|---|---|
| Perreault | 4 | +46% | +29% |
| Kreider | 2 | +76% | +27% |
| McMann | 3 | +57% | +38% |

Percent changes are against last season's per-game baseline, from only a few games, so treat them as a direction and not a verdict.

## Week 2

### Headline picks

| Pick | League | Probability |
|---|---|---|
| Nathan MacKinnon | 2 | 87.9% |
| Connor McDavid | 3 | 82.0% |
| Jeremy Swayman | 1 | 71.5% |

### Slate

| League | Favored | Avg confidence |
|---|---|---|
| 1 | 6 of 13 | 51.8% |
| 2 | 10 of 13 | 60.8% |
| 3 | 13 of 18 | 55.8% |

Goalie start shares used: Swayman .66, Oettinger .66, Blackwood .44, Vejmelka .77, Wallstedt .40, Dobes .51. The most lopsided matchup is Harley vs Karlsson in league 3, at 11.5%.

### Sleepers

| Player | Rostered | Games | Pts/g this season (last) | Shots/g | Shooting % | TOI |
|---|---|---|---|---|---|---|
| Paul Cotter (VAN) | 28% | 4 | 1.50 (0.19) | 1.75 (0.77) | 57% (15%) | 15:22 (10:41) |
| Eli Tolvanen (NYR) | 6% | 4 | 0.75 (0.46) | 1.50 (1.81) | 50% (9%) | 13:29 (16:02) |
| Tommy Novak (PIT) | 22% | 2 | 2.00 (0.51) | 1.50 (1.59) | 67% (12%) | 15:23 (14:17) |

Cotter and Novak are mostly shooting-percentage luck: their shot volume is flat. Cotter's ice time did rise, which is the better sign. Tolvanen's shot volume and ice time are both down, so he is the riskiest of the three.

### What to check next week

- Did the 70%+ picks win?
- Did goalie expected starts match actual starts?
- Did the sleepers keep their per-game rates or regress toward last season?
