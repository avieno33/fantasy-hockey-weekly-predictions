# Methodology

This document lays out the statistical model behind the weekly predictions: what it computes, why each piece was chosen, its known limitations, and where it's likely to be extended as the season progresses.

The model is versioned. Changes are only made in response to a *pattern* across multiple weeks, not a single missed call, since the model itself predicts probabilities, not certainties, some misses are expected by design. Each version change is logged in the **Version History** section at the bottom with the reason behind it.

---

## v1 — Base model

### 1. Expected value and volatility per player

For each player (or goalie), two numbers are tracked, not one:

- **μ (mu) — expected fantasy performance**, a rolling average of fantasy points per game.
- **σ (sigma) — volatility**, the standard deviation of fantasy points per game over the same window.

Modeling both matters because two players can have the same average production and completely different reliability, a consistent 3-point/game player and a boom-or-bust 3-point/game player are different fantasy assets, even though a simple projection would treat them identically.

**Recency weighting:** rather than a flat average over the window, more recent games are weighted more heavily, using an exponentially weighted moving average (EWMA) with a half-life of 5 games, a game from 5 games ago carries half the weight of the most recent game. This reflects the reality that hockey performance is streaky, role changes, hot lines, and recovery from injury all make recent games more informative than games from a month ago. The half-life of 5 is a judgment call, not derived mathematically, chosen by comparing behavior against real season data rather than by intuition alone. Open to tuning once real weekly predictions accumulate, see Version History.

### 2. Early-season shrinkage (handling small samples)

Early in the season, there are too few current-season games to compute a stable μ or σ, a standard deviation from 2-3 games is close to meaningless and would produce overconfident, misleading predictions if used directly.

**Fix:** blend last season's full-season stats (the *prior*) with a **flat cumulative mean** of the current season's games so far, weighting the current season more heavily as more games accumulate:

```
blended_μ = (n_current × current_μ + k × prior_μ) / (n_current + k)
```

where `n_current` is the number of current-season games observed, `current_μ` is the plain, unweighted average of fantasy points across those games, and `k` is a constant controlling how much weight the prior gets early on (higher `k` = trust the prior longer). The same blending is applied to σ. As the season progresses and `n_current` grows, the prior's influence fades out naturally.

v1 uses `k = 10`. Like the EWMA half-life, this was chosen by comparing how different values behaved on real season data, a small `k` overreacts to hot or cold stretches that are ultimately just noise, a large `k` is slower to recognize a real, sustained change in a player's level. `k = 10` sits in between. Also a judgment call, not derived mathematically, and open to tuning based on actual calibration once real predictions accumulate.

**Important — this uses the flat cumulative mean, not the EWMA from Section 1.** These were tested combined during development (blending the prior with the EWMA value directly, hoping for one number that's both recency-weighted and prior-informed), and that combination doesn't work: EWMA's weighting stays constant regardless of how many games have been played, so it never stops reacting to recent streaks, while a flat mean's sensitivity to any single new game naturally shrinks as `1/n`, stabilizing over the season. EWMA and shrinkage are answering genuinely different questions, EWMA answers "how is this player doing right now, recently," shrinkage answers "what is this player's underlying level this season, overall." Both get computed and used, but kept separate, not combined into one number.

This is a simplified form of a shrinkage estimator (related to empirical Bayes methods): early estimates lean on outside information, and lean less as more direct evidence comes in.

### 3. Cross-position comparability: z-scores

Raw fantasy points aren't comparable across positions, a defenseman's 2 points/game and a winger's 2 points/game don't mean the same thing. Each player's μ is converted into a **z-score relative to their position group**:

```
z = (player_μ − position_group_mean) / position_group_std
```

This gives one comparable scale across the whole roster.

### 4. Comparing two players: probability, not just a bigger number

For any head-to-head call (start/sit, trade, waiver pickup), the model doesn't just compare averages, it computes the **probability that one player outperforms another**, treating each player's per-game output as approximately normally distributed:

```
P(A > B) = Φ( (μ_A − μ_B) / sqrt(σ_A² + σ_B²) )
```

where Φ is the standard normal cumulative distribution function. This is the number reported as "confidence" in each weekly pick, e.g., a 68% call means the model estimates a 68% chance A outperforms B, not a guarantee.

The comparison function is tested against a set of properties any correct version must satisfy regardless of the specific players involved: P(A>B) and P(B>A) must sum to exactly 1, two identical players must give exactly 50%, a strictly higher μ with equal σ must push above 50%, more volatility with the same μ gap must pull the result closer to 50%, and zero volatility on both sides must resolve deterministically rather than dividing by zero.

Worth being precise about what this probability claims: it's P(A outperforms B) in one game, not "who is the better player overall." Even a large talent gap can produce a modest single-game probability, since per-game variance is large for everyone in this sport, this is correct behavior, not a flaw.

### 5. Goalies

Goalies use the same μ/σ/P(A>B) structure as skaters, built from save percentage and goals-against rather than skater scoring stats. Two further adjustments were investigated, following the same standard as the rest of this model, measure the effect against real season data before building anything, don't assume it just because it's intuitive.

**Back-to-back starts, tested, not implemented.** Pooled fantasy points across 142 goalies with a reasonable sample size, 53 back-to-back starts (a rest gap of one day or less) against 2,521 other starts. Observed a -0.34 fantasy point difference, but a two-sample t-test returned p=0.560, statistically indistinguishable from no effect at all given this sample size. Not built into v1. See `future_directions/back_to_back_adjustment.md`.

**Opponent shot volume, implemented.** An opponent's raw goals-for rate was tested first and found too weak to build on (r=-0.137 against fantasy points). A stronger relationship was found and used instead: shots faced correlates with save percentage, r=0.260, pooled across goalies with full-game appearances only (to rule out goalies being pulled early after a bad start as a confound). A league-wide fitted line (`save_pctg ≈ 0.833 + 0.0023 × shots_against`) converts an opponent's typical shot volume into an expected shift in save percentage. This shift is split correctly between saves and goals against using the relevant scoring weights, and applied as an addition on top of each goalie's own baseline μ from Section 2, since a single goalie's own season doesn't provide enough data to fit this relationship individually.

An exploratory extension checked whether individual goalies deviate from this league-wide relationship, using partial pooling (blending each goalie's own fitted slope with the league slope, weighted by how many of their own games exist). Found a real but modest pattern, goalies with a higher average save percentage tend to have flatter slopes (r=-0.284, p=0.0199, across 67 goalies), suggesting elite goaltending is somewhat less dependent on shot volume than average. This refinement is not yet wired into the main estimate, both because the effect is moderate (r² under 0.09) and because of a mild circularity risk in how it was measured (a goalie's own slope and average are both derived from the same games). See `future_directions/goalie_slope_partial_pooling.md`.

---

## Known simplifications (v1)

Being upfront about where this model is deliberately simple:

- **Normality assumption.** Real per-game fantasy point totals are right-skewed (mostly modest games, occasional big ones), not symmetric like a true normal distribution. Treating them as normal is a standard simplifying approximation for this kind of comparison, not a claim that it's exactly correct.
- **Independence assumption (for any team-level aggregation).** Summing variance across multiple players assumes their performances are independent of one another. In reality, linemates' performances are somewhat correlated (a hot line lifts everyone on it). Treated as a reasonable simplification at this scope.
- **This model predicts fantasy performance, not game outcomes.** It says nothing about which team wins the actual game, that's a separate, harder problem (team-strength modeling) that's intentionally out of scope so this stays focused.
- **Not every scoreable category is available from the data source.** Faceoffs won and lost (FW, FL) aren't obtainable as raw counts, only a faceoff win percentage exists, which can't be split back into wins and losses. These categories are excluded from scoring rather than approximated. Hits and blocked shots (HIT, BLK) are supported, but required a second data pull (a per-game boxscore) beyond the basic game log. Goals-against average (GAA) is also currently unscored if a league includes it, it's a multi-game rate stat, not a single-game value, and doesn't fit the current per-game scoring model, see `future_directions/goalie_gaa_rate_stat.md`.
- **Incomplete or partial appearances are handled explicitly, not dropped by default.** A goalie relief appearance with no official decision recorded, for example, still contributes its real save and goals-against stats to scoring rather than being excluded outright for having one missing field.
- **No adjustment for opportunity or context.** Ice time, team pace, and strength of schedule aren't factored in for skaters, the model measures realized production, not production adjusted for role or opponent quality. A sudden role change (more ice time, a new linemate) won't be reflected until it shows up in the stats after the fact.
- **Opponent-strength adjustments currently only exist for goalies, not skaters.** A mirrored version for skaters (using opponent goals/shots-against instead of goals/shots-for) is the next planned build, see `future_directions/opponent_strength_for_skaters.md`.
- **The shrinkage prior assumes last season is a fair baseline.** Team changes, aging, or league-wide rule changes between seasons could make the prior systematically biased in ways the model has no way to detect. Notably, the 2026-27 season expanded to an 84-game schedule (up from 82), so raw season totals aren't directly comparable across the prior and current season, all comparisons here use per-game rates specifically to avoid this issue, but it's worth keeping in mind as a real difference between the two seasons.
- **Goalie opponent-strength adjustments are league-wide, not goalie-specific.** The shift applied is the same for every goalie, since no individual goalie's season has enough data to reliably fit their own version of the relationship. An exploratory, partially-pooled goalie-specific version was tested and found a real but modest effect, not yet built into the main pipeline (see Section 5 and `future_directions/goalie_slope_partial_pooling.md`).

---

## Where this is likely to go — planned directions

These aren't commitments on a timeline, they're the directions under consideration, to be pursued if the weekly review process surfaces a real, repeated gap in v1 (per the versioning rule above).

### Near-term, still within the same framework
- **Skater opponent-strength adjustment**, mirroring the goalie version using opponent goals/shots-against. Next priority once the base model is stable, see `future_directions/opponent_strength_for_skaters.md`.
- **Wiring individual goalie slopes into the main estimate**, pending further validation of the partial-pooling approach and resolving the circularity concern noted above.
- **Category league support**, extending custom scoring beyond points leagues to head-to-head category formats, see `future_directions/category_league_support.md`.
- **Better μ estimate via lightweight regression.** Instead of (blended) rolling average, a simple, interpretable model (e.g., ridge regression) using a few added features, ice time, shot rate, opponent defensive strength, to estimate expected performance. This would replace *only* the μ estimate; the σ/z-score/P(A>B) machinery downstream stays the same. Kept intentionally simple (not a large model) because the amount of public per-player data available doesn't support anything more complex without overfitting.
- **Tuning `k` and the EWMA half-life empirically**, rather than by comparison alone, e.g., checking which values would have produced the best-calibrated predictions against past data.

### Longer-term / larger changes, worth naming honestly as "maybe"
- **Machine learning for performance projection.** If enough weekly data accumulates over a full season (predictions + actual outcomes), there could eventually be enough signal to train a small supervised model (e.g., gradient-boosted trees) predicting next-week fantasy output from a richer feature set. This is explicitly a "maybe, later" item, not a v1 goal, with only weekly-cadence data from one season, sample size will likely stay a real constraint, and an uninterpretable model would work against the project's whole point of showing *why* a call was made, not just what it was.
- **Calibration-driven correction.** Since every prediction is logged with a confidence level and an eventual outcome, over a full season there will be enough data to check calibration directly, do "70% confidence" calls actually land around 70% of the time? If they're systematically over- or under-confident, that's a concrete, data-backed reason to adjust the model (e.g., scaling σ up or down), rather than a guess.
- **Team-level matchup view.** Aggregating predicted μ/σ across a full projected lineup (yours vs. an opponent's) to produce an overall weekly matchup confidence and flag positions of relative weakness. Uses the same math as above, just summed across a roster.
- **A learned team-strength rating** (Elo-style, updating game by game based on outcomes), rather than a rolling or pooled average, see `future_directions/team_strength_rating_model.md`.
- **Faceoff scoring**, if a data source with raw won/lost counts (rather than just a percentage) is found.
- **Injury / missed-game detection**, comparing a player's game log against their team's schedule to flag unexplained absences, see `future_directions/injury_status_detection.md`.

---

## Version History

- **v1** (current) — rolling EWMA μ (half-life 5) for recent form, flat cumulative mean blended with prior-season stats (k=10) for early-season shrinkage, positional z-scores, P(A>B) comparison model with formal correctness checks, goalie opponent shot-volume adjustment (league-wide, based on a tested shots-vs-save-percentage relationship). Back-to-back adjustment tested and found statistically insignificant, not implemented. Skater opponent-strength adjustment not yet built.
