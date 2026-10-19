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

## Model version

All predictions so far use **model v1**, unchanged since Week 1. It stays frozen through Week 6. Candidate changes (goalie start share that blends this season's starts, a probability of playing each game, credibility weighting for thin-data players) are being tested on the side only. Review date: **Monday Nov 9**, with the switch rule written down before looking at the results. From Week 4 on, each prediction file carries a `model_version` column.

## Calibration summary (running)

Weeks 1 to 3 combined (119 scored matchups). Week 1 used per-game probabilities and Weeks 2 and 3 used weekly totals, so read this as a running tally, not a clean sample.

| Confidence | Picks | Won | Hit rate |
|---|---|---|---|
| 50-60% | 53 | 26 | 49.1% |
| 60-70% | 39 | 21 | 53.8% |
| 70-80% | 16 | 12 | 75.0% |
| 80%+ | 11 | 9 | 81.8% |
| **All** | **119** | **68** | **57.1%** |

Equal-games matchups only (where the model has no schedule edge): Week 1 6 of 13, Week 2 16 of 31, Week 3 28 of 43, so **50 of 87 (57.5%)** so far. Matchups with unequal games: Week 2 went 10 of 13 and Week 3 went 2 of 2.

Hit rates now rise with confidence in every bucket, which is the direction we want. But the same players appear in all three leagues, so 119 matchups is fewer independent bets than it sounds. At this size the standard error on a hit rate is about 5 points, and it would take roughly 600 matchups to tell 55% from 50%. Treat this as encouraging, not proven.

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
- **Novak's role never changed.** His ice time (15.4 to 15.1 minutes) and shots (1.50 to 1.75 per game) held, and his fantasy points per game ended close to last season's (+6% and +11% in leagues 1 and 2).

## Week 3 (late start, Tue Oct 13 to Sun Oct 18)

### Results

| Measure | Result |
|---|---|
| All matchups | 30 of 45 picks won (66.7%), Brier 0.200 |
| League 1 | 10 of 13 (76.9%), Brier 0.210 |
| League 2 | 8 of 14 (57.1%), Brier 0.200 |
| League 3 | 12 of 18 (66.7%), Brier 0.192 |
| Unequal games (predicted) | 2 of 2 |
| Equal games (predicted) | 28 of 43 |

Brier 0.200 is clearly better than the 0.250 of always predicting 50%. It is still one week of overlapping matchups.

| Confidence | n | Won | Hit rate |
|---|---|---|---|
| 50-60% | 15 | 8 | 53.3% |
| 60-70% | 15 | 8 | 53.3% |
| 70-80% | 8 | 8 | 100% |
| 80%+ | 7 | 6 | 85.7% |

Weeks 2 and 3 combined (both weekly totals): 56 of 89 (62.9%).

What I take from it:
- I expected a near coin flip, because only two matchups had unequal games. The equal-games record was 28 of 43 (65%), so the model separated similar players better than Week 2 suggested. Across all three weeks the equal-games record is 50 of 87 (57%).
- Point estimates held up: mean expected 8.18 vs mean actual 8.53, correlation 0.55 (0.44 in Week 2). Goalies came in 0.47 above expectation and skaters 0.32.
- Goalies played 21 games against 20.1 expected, so Week 2's gap (30 vs 22.5) did not repeat. Good reason not to change the start-share rule on one week of data.
- Every game-count mismatch was a goalie, so skaters played all their predicted games this week, unlike Week 2.

### Headline picks

2 of 3. Stutzle lost at 85% (4.90 vs 7.80). Aho and Sergachev each won by under a point.

### Sleepers

| Player | Rostered | Week 3 games | Thesis | Held? |
|---|---|---|---|---|
| Devon Levi (G, EDM) | 35% | 2 | Taking the starting job; start share of 2 or more of 3 games | Yes. 2 of 3 starts, save percentage .860 to .940, but fantasy points flat (1 win in 2 starts) |
| Trevor Connelly (VGK) | 13% | 3 | Ice time stays above 15 minutes | No. 14.5 minutes; points +51% to +59% came from 40% shooting while shots fell |
| Shane Pinto (OTT) | 22% | 3 | Extra ice time keeps him above last season | No. 19% to 32% below last season in every league; ice time back to 18.0 minutes |

1 of 3 on its own thesis, which is a record of how the method does and not evidence about it. Two weeks of sleepers so far: Week 2 went 0 of 3 against the last-season baseline and Week 3 went 1 of 3. Levi's actual start share (3 of 5, then 2 of 3) is a case a start share that blends this season's starts would handle better, so it goes on the list of v2 candidates for the Week 6 review.

## Week 4 (Mon Oct 19 to Sun Oct 25), predictions committed before games

45 matchups (league 1: 13, league 2: 14, league 3: 18), model v1, weekly totals. I'm favored in 27 of 45: league 1 in 6 of 13 (49.0% average win probability), league 2 in 10 of 14 (52.5%), league 3 in 11 of 18 (54.0%). 20 of the 45 have unequal game counts, 9 of them in league 1.

### Headline picks

| Pick | League | Probability | Result |
|---|---|---|---|
| Connor McDavid over Sidney Crosby | 3 | 90% | Pending |
| Nathan MacKinnon over William Nylander | 2 | 71% | Pending |
| Cale Makar over Jakob Chychrun | 1 | 94% (Chychrun 6%) | Pending |

Makar's call is mostly the schedule (4 games vs 2). McDavid's and MacKinnon's are equal-games calls where per-game and recent form agree.

### Sleepers

| Player | Team | Rostered | Games this week | Thesis |
|---|---|---|---|---|
| Adam Edstrom | NSH | 8% | 3 | The 4 goals are a 27% shooting streak and won't last, but ice time and shots are up and he's above last season's average in all 8 games. |
| Michael Brandsegg-Nygard | DET | 14% | 3 | Shots nearly doubled and ice time is up at a normal 9% shooting rate, but about half his points came in two games, so expect spiky weeks. |
| Boone Jenner | WSH | 17% | 2 | Not a breakout: points per game match last season, but shots are up about 40%. Only 2 team games this week. |

They will be graded against the model's own expectation (`season_mu`), not just last season's average.

## What to check next week

- Grade Week 4 and update the running calibration table (119 matchups so far).
- Whether the 2-game-week calls hold up, especially Chychrun in all three leagues and Makar's 4 games.
- Goalie usage against start share again (Blackwood at 0.44 on 4 games; the Week 3 gap did not repeat).
- Equal-games record against 50 of 87 so far.
- Model review is Monday Nov 9, after Week 6. No model change before then.
