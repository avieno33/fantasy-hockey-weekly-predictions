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

Week 3 was a **late start**: predictions were made Tuesday Oct 13, after Monday's games, so the window is Tue Oct 13 to Sun Oct 18 and is not a full Yahoo week.

## Calibration summary (running)

Weeks 1 and 2 combined (74 scored matchups). The two weeks use different units (per-game and weekly total), so read this as a running tally, not a clean sample.

| Confidence | Picks | Won | Hit rate |
|---|---|---|---|
| 50-60% | 38 | 18 | 47.4% |
| 60-70% | 24 | 13 | 54.2% |
| 70-80% | 8 | 4 | 50.0% |
| 80%+ | 4 | 3 | 75.0% |
| **All** | **74** | **38** | **51.4%** |

Equal-games matchups only (where the model has no schedule edge): Week 1 6 of 13, Week 2 16 of 31, so **22 of 44 (50%)** so far. Matchups with unequal games: Week 2 went 10 of 13.

Far too few picks to say anything about calibration. Nothing here is distinguishable from noise yet.

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

Percent changes are against last season's per-game baseline, from only a few games, so treat them as a direction and not a verdict. League 1 is not shown.

## Week 2

### Results

| Measure | Result |
|---|---|
| All matchups | 26.0 of 44 picks won (59.1%), Brier 0.244 |
| League 1 | 7 of 13 (53.8%), Brier 0.251 |
| League 2 | 8 of 13 (61.5%), Brier 0.216 |
| League 3 | 11 of 18 (61.1%), Brier 0.260 |
| Unequal games (predicted) | 10 of 13 |
| Equal games (predicted) | 16 of 31 |

Brier 0.244 is a hair better than the 0.250 that always predicting 50% scores. One week, so not evidence of skill.

| Confidence | n | Won | Avg confidence | Hit rate |
|---|---|---|---|---|
| 50-60% | 15 | 8 | 53.8% | 53.3% |
| 60-70% | 18 | 11 | 65.2% | 61.1% |
| 70-80% | 7 | 4 | 75.1% | 57.1% |
| 80%+ | 4 | 3 | 85.9% | 75.0% |

What I take from it:
- The wins came mostly where game counts differed. On equal-game matchups the model was 16 of 31 (52%). The schedule edge is working; separating two similar players is not, yet.
- The weekly point estimates are well centred: mean expected 8.00 vs mean actual 8.03 points per player, correlation 0.44. Skaters came in 0.25 below expectation on average, goalies 1.84 above.
- Games missed to injury or scratches (Demidov 0 of 3, Marchand 1 of 2, Dobes 1 of 3) cost several slots. The model assumes everyone plays every team game.
- Goalies: 5 of 6 picks won, but all twelve goalies appeared in 30 games against 22.5 expected from last season's start share. Watching whether early-season usage keeps running above start share. No model change on one week.

### Headline picks

| Pick | League | Probability | Result |
|---|---|---|---|
| Nathan MacKinnon | 2 | 87.9% | Won, 12.10 vs 8.60 (3 games each) |
| Connor McDavid | 3 | 82.0% | Lost, 12.88 vs 13.68 (2 games each) |
| Jeremy Swayman | 1 | 71.5% | Won, 11.00 vs 3.90 (3 games vs 2) |

2 of 3. McDavid's loss was by under a point, a normal 1-in-5 outcome at 82%.

### Biggest misses

| Matchup | League | Model said | Result |
|---|---|---|---|
| McDavid vs Hischier | 3 | 82% | 12.88 vs 13.68 |
| Porter Martone vs Mitch Marner | 3 | 73% | 5.42 vs 15.48 |
| Chychrun vs Cole Hutson | 2 | 69% | 2.00 vs 6.15 |
| Andersson vs Hronek | 3 | 22% | 3.67 vs 2.30 (I won) |
| Elias Pettersson vs Quinn Hughes | 1 | 22% | 7.00 vs 6.30 (I won) |

### Sleepers

The pre-week process numbers (4 games or fewer, first week of the season):

| Player | Rostered | GP 2026-27 | Pts/g this season (last) | Shots/g | Shooting % | TOI |
|---|---|---|---|---|---|---|
| Paul Cotter (VAN) | 28% | 4 | 1.50 (0.19) | 1.75 (0.77) | 57% (15%) | 15:13 (10:41) |
| Eeli Tolvanen (NYR) | 6% | 4 | 0.75 (0.46) | 1.50 (1.81) | 50% (9%) | 13:29 (16:02) |
| Tommy Novak (PIT) | 22% | 2 | 2.00 (0.51) | 1.50 (1.59) | 67% (12%) | 15:23 (14:17) |

Week 2 fantasy points per game against last season's per-game average, under each league's scoring:

| Player | Week 2 games | League 1 | League 2 | League 3 |
|---|---|---|---|---|
| Cotter | 3 | -23% | -21% | -46% |
| Tolvanen | 3 | -24% | -15% | -30% |
| Novak | 4 | +6% | +11% | -39% |

None of the three beat last season's baseline in a convincing way.
- **Hot shooting percentages did not last.** Cotter's 57% and Novak's 67% in Week 1 became 0% and 14% in Week 2.
- **Novak's role never changed.** His ice time (15.4 to 15.1 minutes) and shots (1.50 to 1.75 per game) held, and his
