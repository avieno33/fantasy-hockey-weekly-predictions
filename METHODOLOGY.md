# Methodology

This document lays out the statistical model behind the weekly predictions: what it computes, why each piece was chosen, its known limitations, and where it's likely to be extended as the season progresses.

The model is versioned. Changes are only made in response to a *pattern* across multiple weeks, not a single missed call — since the model itself predicts probabilities, not certainties, some misses are expected by design. Each version change is logged in the **Version History** section at the bottom with the reason behind it.

---

## v1 — Base model

### 1. Expected value and volatility per player

For each player (or goalie), two numbers are tracked, not one:

- **μ (mu) — expected fantasy performance**, a rolling average of fantasy points per game.
- **σ (sigma) — volatility**, the standard deviation of fantasy points per game over the same window.

Modeling both matters because two players can have the same average production and completely different reliability — a consistent 3-point/game player and a boom-or-bust 3-point/game player are different fantasy assets, even though a simple projection would treat them identically.

**Recency weighting:** rather than a flat average over the window, more recent games are weighted more heavily, using an exponentially weighted moving average (EWMA) with a half-life of 5 games — a game from 5 games ago carries half the weight of the most recent game. This reflects the reality that hockey performance is streaky — role changes, hot lines, and recovery from injury all make recent games more informative than games from a month ago. The half-life of 5 is a judgment call, not derived mathematically, chosen by comparing behavior against real season data rather than by intuition alone. Open to tuning once real weekly predictions accumulate, see Version History.

### 2. Early-season shrinkage (handling small samples)

Early in the season, there are too few current-season games to compute a stable μ or σ — a standard deviation from 2-3 games is close to meaningless and would produce overconfident, misleading predictions if used directly.

**Fix:** blend last season's full-season stats (the *prior*) with a **flat cumulative mean** of the current season's games so far, weighting the current season more heavily as more games accumulate:

```
blended_μ = (n_current × current_μ + k × prior_μ) / (n_current + k)
```

where `n_current` is the number of current-season games observed, `current_μ` is the plain, unweighted average of fantasy points across those games, and `k` is a constant controlling how much weight the prior gets early on (higher `k` = trust the prior longer). The same blending is applied to σ. As the season progresses and `n_current` grows, the prior's influence fades out naturally.

v1 uses `k = 10`. Like the EWMA half-life, this was chosen by comparing how different values behaved on real season data — a small `k` overreacts to hot or cold stretches that are ultimately just noise, a large `k` is slower to recognize a real, sustained change in a player's level. `k = 10` sits in between. Also a judgment call, not derived mathematically, and open to tuning based on actual calibration once real predictions accumulate.

**Important — this uses the flat cumulative mean, not the EWMA from Section 1.** These were tested combined during development (blending the prior with the EWMA value directly, hoping for one number that's both recency-weighted and prior-informed), and that combination doesn't work: EWMA's weighting stays constant regardless of how many games have been played, so it never stops reacting to recent streaks, while a flat mean's sensitivity to any single new game naturally shrinks as `1/n`, stabilizing over the season. EWMA and shrinkage are answering genuinely different questions — EWMA answers "how is this player doing right now, recently," shrinkage answers "what is this player's underlying level this season, overall." Both get computed and used, but kept separate, not combined into one number.

This is a simplified form of a shrinkage estimator (related to empirical Bayes methods): early estimates lean on outside information, and lean less as more direct evidence comes in.

### 3. Cross-position comparability: z-scores

Raw fantasy points aren't comparable across positions — a defenseman's 2 points/game and a winger's 2 points/game don't mean the same thing. Each player's μ is converted into a **z-score relative to their position group**:

```
z = (player_μ − position_group_mean) / position_group_std
```

This gives one comparable scale across the whole roster.

### 4. Comparing two players: probability, not just a bigger number

For any head-to-head call (start/sit, trade, waiver pickup), the model doesn't just compare averages — it computes the **probability that one player outperforms another**, treating each player's per-game output as approximately normally distributed:

```
P(A > B) = Φ( (μ_A − μ_B) / sqrt(σ_A² + σ_B²) )
```

where Φ is the standard normal cumulative distribution function. This is the number reported as "confidence" in each weekly pick — e.g., a 68% call means the model estimates a 68% chance A outperforms B, not a guarantee.

### 5. Goalies

Goalies use the same μ/σ/P(A>B) structure as skaters, built from save percentage and goals-against rather than skater scoring stats. Two further adjustments are planned but **not yet implemented in v1**:
- **Back-to-back starts** (goalies playing on no rest tend to perform worse on average — planned to be estimated empirically from the pulled data rather than assumed)
- **Opponent offensive strength** (a stronger-scoring opponent raises expected goals against)

---

## Known simplifications (v1)

Being upfront about where this model is deliberately simple:

- **Normality assumption.** Real per-game fantasy point totals are right-skewed (mostly modest games, occasional big ones), not symmetric like a true normal distribution. Treating them as normal is a standard simplifying approximation for this kind of comparison, not a claim that it's exactly correct.
- **Independence assumption (for any team-level aggregation).** Summing variance across multiple players assumes their performances are independent of one another. In reality, linemates' performances are somewhat correlated (a hot line lifts everyone on it). Treated as a reasonable simplification at this scope.
- **This model predicts fantasy performance, not game outcomes.** It says nothing about which team wins the actual game — that's a separate, harder problem (team-strength modeling) that's intentionally out of scope so this stays focused.
- **Not every scoreable category is available from the data source.** Faceoffs won and lost (FW, FL) aren't obtainable as raw counts from this project's data source — only a faceoff win percentage exists, which can't be split back into wins and losses. These categories are excluded from scoring rather than approximated. Hits and blocked shots (HIT, BLK) are supported, but required a second data pull (a per-game boxscore) beyond the basic game log — worth knowing scoring isn't sourced from one single unified endpoint.
- **Incomplete or partial appearances are handled explicitly, not dropped by default.** A goalie relief appearance with no official decision recorded, for example, still contributes its real save and goals-against stats to scoring rather than being excluded outright for having one missing field.
-  **No adjustment for opportunity or context.** Ice time, team pace, and
  strength of schedule aren't factored in, the model measures realized
  production, not production adjusted for role or opponent quality. A
  sudden role change (more ice time, a new linemate) won't be reflected
  until it shows up in the stats after the fact.
- **The shrinkage prior assumes last season is a fair baseline.** Team
  changes, aging, or league-wide rule changes between seasons could
  make the prior systematically biased in ways the model has no way
  to detect.

---

## Where this is likely to go — planned directions

These aren't commitments on a timeline — they're the directions under consideration, to be pursued if the weekly review process surfaces a real, repeated gap in v1 (per the versioning rule above).

### Near-term, still within the same framework
- **Goalie adjustments for rest and opponent strength**, described in Section 5 above, planned for v1 but not yet built.
- **Better μ estimate via lightweight regression.** Instead of (blended) rolling average, a simple, interpretable model (e.g., ridge regression) using a few added features — ice time, shot rate, opponent defensive strength — to estimate expected performance. This would replace *only* the μ estimate; the σ/z-score/P(A>B) machinery downstream stays the same. Kept intentionally simple (not a large model) because the amount of public per-player data available doesn't support anything more complex without overfitting.
- **Tuning `k` and the EWMA half-life empirically**, rather than by comparison alone — e.g., checking which values would have produced the best-calibrated predictions against past data.

### Longer-term / larger changes, worth naming honestly as "maybe"
- **Machine learning for performance projection.** If enough weekly data accumulates over a full season (predictions + actual outcomes), there could eventually be enough signal to train a small supervised model (e.g., gradient-boosted trees) predicting next-week fantasy output from a richer feature set. This is explicitly a "maybe, later" item, not a v1 goal — with only weekly-cadence data from one season, sample size will likely stay a real constraint, and an uninterpretable model would work against the project's whole point of showing *why* a call was made, not just what it was.
- **Calibration-driven correction.** Since every prediction is logged with a confidence level and an eventual outcome, over a full season there will be enough data to check calibration directly — do "70% confidence" calls actually land around 70% of the time? If they're systematically over- or under-confident, that's a concrete, data-backed reason to adjust the model (e.g., scaling σ up or down), rather than a guess.
- **Team-level matchup view.** Aggregating predicted μ/σ across a full projected lineup (yours vs. an opponent's) to produce an overall weekly matchup confidence and flag positions of relative weakness. Uses the same math as above, just summed across a roster.
- **Faceoff scoring**, if a data source with raw won/lost counts (rather than just a percentage) is found.

---

## Version History

- **v1** (current) — rolling EWMA μ (half-life 5) for recent form, flat cumulative mean blended with prior-season stats (k=10) for early-season shrinkage, positional z-scores, P(A>B) comparison model. Goalie-specific rest/opponent adjustments not yet implemented.
